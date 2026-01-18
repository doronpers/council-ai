"""
Memory management utilities for Council AI.

Provides memory monitoring, cleanup mechanisms, and resource management
for large consultations and streaming operations.
"""

from __future__ import annotations

import gc
import logging
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, List, Optional
from weakref import WeakSet

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory usage and trigger cleanup when needed."""

    def __init__(
        self,
        memory_threshold_mb: float = 500.0,
        cleanup_interval: float = 30.0,
        enable_auto_cleanup: bool = True,
    ):
        self.memory_threshold_mb = memory_threshold_mb
        self.cleanup_interval = cleanup_interval
        self.enable_auto_cleanup = enable_auto_cleanup
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._memory_pressure = False

        # Track large objects for cleanup
        self._large_objects: WeakSet = WeakSet()

        if enable_auto_cleanup:
            self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start the memory monitoring thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="memory-monitor"
        )
        self._monitor_thread.start()
        logger.debug("Memory monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the memory monitoring thread."""
        if self._monitor_thread:
            self._stop_monitoring.set()
            self._monitor_thread.join(timeout=5.0)
            logger.debug("Memory monitoring stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_monitoring.is_set():
            try:
                memory_mb = self.get_memory_usage_mb()
                if memory_mb > self.memory_threshold_mb:
                    self._handle_memory_pressure(memory_mb)
                else:
                    self._memory_pressure = False
            except Exception as e:
                logger.debug(f"Memory monitoring error: {e}")

            self._stop_monitoring.wait(self.cleanup_interval)

    def _handle_memory_pressure(self, memory_mb: float) -> None:
        """Handle memory pressure by triggering cleanup."""
        if self._memory_pressure:
            # Already handling pressure, avoid repeated cleanup
            return

        self._memory_pressure = True
        logger.warning(f"Memory pressure detected: {memory_mb:.1f} MB used")

        # Trigger cleanup
        self.force_cleanup()

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        if HAS_PSUTIL:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / (1024 * 1024)  # Convert to MB
            except Exception:
                pass

        # Fallback: use gc module info
        return len(gc.get_objects()) / 1000.0  # Rough estimate

    def register_large_object(self, obj: Any) -> None:
        """Register a large object for potential cleanup."""
        self._large_objects.add(obj)

    def force_cleanup(self) -> None:
        """Force garbage collection and cleanup."""
        logger.info("Performing memory cleanup...")

        # Clear weak references to large objects
        self._large_objects.clear()

        # Force garbage collection
        collected = gc.collect()

        # Clear any cached objects in commonly used libraries
        self._clear_library_caches()

        logger.info(f"Memory cleanup completed. Collected {collected} objects.")

    def _clear_library_caches(self) -> None:
        """Clear caches from commonly used libraries."""
        try:
            # Clear any cached regex patterns
            import re

            re.purge()
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get memory monitoring statistics."""
        return {
            "current_memory_mb": self.get_memory_usage_mb(),
            "memory_threshold_mb": self.memory_threshold_mb,
            "memory_pressure": self._memory_pressure,
            "large_objects_count": len(self._large_objects),
            "gc_stats": {"collected": gc.get_stats(), "objects": len(gc.get_objects())},
        }


class ResourceManager:
    """Manage resources with automatic cleanup."""

    def __init__(self):
        self._resources: List[Any] = []
        self._cleanup_functions: List[Callable] = []
        self._lock = threading.RLock()

    def register_resource(self, resource: Any, cleanup_func: Optional[Callable] = None) -> None:
        """Register a resource for cleanup."""
        with self._lock:
            self._resources.append(resource)
            if cleanup_func:
                self._cleanup_functions.append(cleanup_func)

    def cleanup_resources(self) -> None:
        """Clean up all registered resources."""
        with self._lock:
            for cleanup_func in reversed(self._cleanup_functions):
                try:
                    cleanup_func()
                except Exception as e:
                    logger.debug(f"Error during resource cleanup: {e}")

            # Clear references
            self._resources.clear()
            self._cleanup_functions.clear()

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and cleanup resources."""
        self.cleanup_resources()


@contextmanager
def memory_managed_operation(
    memory_monitor: Optional[MemoryMonitor] = None, description: str = "operation"
) -> Generator[ResourceManager, None, None]:
    """
    Context manager for memory-managed operations.

    Usage:
        with memory_managed_operation(monitor, "consultation") as rm:
            # Register large objects
            rm.register_resource(large_object, cleanup_func)
            # Perform operation
            result = do_something()
            yield result
    """
    resource_manager = ResourceManager()
    memory_monitor = memory_monitor or MemoryMonitor()

    try:
        yield resource_manager
    finally:
        # Cleanup resources
        resource_manager.cleanup_resources()

        # Check memory after operation
        if memory_monitor.get_memory_usage_mb() > memory_monitor.memory_threshold_mb:
            logger.info(f"High memory usage detected after {description}, triggering cleanup")
            memory_monitor.force_cleanup()


class StreamingMemoryManager:
    """Manage memory during streaming operations."""

    def __init__(self, chunk_limit: int = 1000, memory_limit_mb: float = 100.0):
        self.chunk_limit = chunk_limit
        self.memory_limit_mb = memory_limit_mb
        self._chunks: List[str] = []
        self._total_size = 0

    def add_chunk(self, chunk: str) -> None:
        """Add a chunk to the buffer, managing memory usage."""
        chunk_size = len(chunk.encode("utf-8"))

        # Check if adding this chunk would exceed memory limit
        if self._total_size + chunk_size > self.memory_limit_mb * 1024 * 1024:
            self._compact_chunks()

        self._chunks.append(chunk)
        self._total_size += chunk_size

        # Limit number of chunks to prevent unbounded growth
        if len(self._chunks) > self.chunk_limit:
            # Combine oldest chunks
            combined = "".join(self._chunks[:10])
            self._chunks = [combined] + self._chunks[10:]
            self._total_size = sum(len(c.encode("utf-8")) for c in self._chunks)

    def _compact_chunks(self) -> None:
        """Compact chunks to free memory."""
        if len(self._chunks) > 1:
            # Combine first half of chunks
            mid = len(self._chunks) // 2
            combined = "".join(self._chunks[:mid])
            self._chunks = [combined] + self._chunks[mid:]
            self._total_size = sum(len(c.encode("utf-8")) for c in self._chunks)

    def get_content(self) -> str:
        """Get the complete content."""
        return "".join(self._chunks)

    def clear(self) -> None:
        """Clear all chunks."""
        self._chunks.clear()
        self._total_size = 0

    def get_memory_usage_mb(self) -> float:
        """Get memory usage in MB."""
        return self._total_size / (1024 * 1024)


# Global memory monitor instance
_global_memory_monitor: Optional[MemoryMonitor] = None


def get_global_memory_monitor() -> MemoryMonitor:
    """Get the global memory monitor instance."""
    global _global_memory_monitor
    if _global_memory_monitor is None:
        _global_memory_monitor = MemoryMonitor()
    return _global_memory_monitor


def force_global_cleanup() -> None:
    """Force global memory cleanup."""
    monitor = get_global_memory_monitor()
    monitor.force_cleanup()
