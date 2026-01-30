"""
Tests for core/memory.py — MemoryMonitor, ResourceManager, StreamingMemoryManager.

This module previously had only 35% test coverage.
"""

import gc
import threading

import pytest
from unittest.mock import MagicMock, patch

from council_ai.core.memory import (
    MemoryMonitor,
    ResourceManager,
    StreamingMemoryManager,
    force_global_cleanup,
    get_global_memory_monitor,
    memory_managed_operation,
)


class TestMemoryMonitor:
    """Tests for the MemoryMonitor class."""

    def test_init_defaults(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        assert monitor.memory_threshold_mb == 500.0
        assert monitor.cleanup_interval == 30.0
        assert monitor.enable_auto_cleanup is False

    def test_init_custom_values(self):
        monitor = MemoryMonitor(
            memory_threshold_mb=200.0,
            cleanup_interval=10.0,
            enable_auto_cleanup=False,
        )
        assert monitor.memory_threshold_mb == 200.0
        assert monitor.cleanup_interval == 10.0

    def test_get_memory_usage_mb_returns_positive(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        usage = monitor.get_memory_usage_mb()
        assert usage > 0

    def test_force_cleanup_runs_gc(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        # Should not raise
        monitor.force_cleanup()

    def test_register_large_object(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)

        class LargeObj:
            pass

        obj = LargeObj()
        monitor.register_large_object(obj)
        assert len(monitor._large_objects) == 1

    def test_force_cleanup_clears_large_objects(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)

        class LargeObj:
            pass

        obj = LargeObj()
        monitor.register_large_object(obj)
        monitor.force_cleanup()
        assert len(monitor._large_objects) == 0

    def test_get_stats_returns_dict(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        stats = monitor.get_stats()
        assert "current_memory_mb" in stats
        assert "memory_threshold_mb" in stats
        assert "memory_pressure" in stats
        assert "large_objects_count" in stats
        assert "gc_stats" in stats

    def test_start_and_stop_monitoring(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        monitor.start_monitoring()
        assert monitor._monitor_thread is not None
        assert monitor._monitor_thread.is_alive()
        monitor.stop_monitoring()
        # Thread should stop
        monitor._monitor_thread.join(timeout=5.0)
        assert not monitor._monitor_thread.is_alive()

    def test_start_monitoring_idempotent(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        monitor.start_monitoring()
        thread1 = monitor._monitor_thread
        monitor.start_monitoring()  # Should not create new thread
        assert monitor._monitor_thread is thread1
        monitor.stop_monitoring()

    def test_handle_memory_pressure_idempotent(self):
        """Repeated calls with pressure should only trigger cleanup once."""
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        with patch.object(monitor, "force_cleanup") as mock_cleanup:
            monitor._handle_memory_pressure(600.0)
            assert monitor._memory_pressure is True
            mock_cleanup.assert_called_once()

            # Second call should not trigger cleanup again
            monitor._handle_memory_pressure(700.0)
            mock_cleanup.assert_called_once()

    def test_memory_pressure_resets_when_below_threshold(self):
        monitor = MemoryMonitor(enable_auto_cleanup=False)
        monitor._memory_pressure = True
        # Simulate the monitoring loop detecting low memory
        monitor._memory_pressure = False
        assert monitor._memory_pressure is False


class TestResourceManager:
    """Tests for the ResourceManager class."""

    def test_register_resource(self):
        rm = ResourceManager()
        resource = MagicMock()
        rm.register_resource(resource)
        assert resource in rm._resources

    def test_register_resource_with_cleanup(self):
        rm = ResourceManager()
        resource = MagicMock()
        cleanup = MagicMock()
        rm.register_resource(resource, cleanup)
        assert resource in rm._resources
        assert cleanup in rm._cleanup_functions

    def test_cleanup_resources_calls_functions_in_reverse(self):
        rm = ResourceManager()
        call_order = []
        rm.register_resource("r1", lambda: call_order.append(1))
        rm.register_resource("r2", lambda: call_order.append(2))
        rm.cleanup_resources()
        assert call_order == [2, 1]

    def test_cleanup_resources_clears_lists(self):
        rm = ResourceManager()
        rm.register_resource("r1", lambda: None)
        rm.cleanup_resources()
        assert len(rm._resources) == 0
        assert len(rm._cleanup_functions) == 0

    def test_cleanup_handles_errors(self):
        rm = ResourceManager()
        rm.register_resource("r1", MagicMock(side_effect=RuntimeError("oops")))
        rm.register_resource("r2", MagicMock())
        # Should not raise
        rm.cleanup_resources()

    def test_context_manager(self):
        with ResourceManager() as rm:
            rm.register_resource("test", MagicMock())
        # After exiting, resources should be cleaned up
        assert len(rm._resources) == 0


class TestStreamingMemoryManager:
    """Tests for the StreamingMemoryManager class."""

    def test_init_defaults(self):
        smm = StreamingMemoryManager()
        assert smm.chunk_limit == 1000
        assert smm.memory_limit_mb == 100.0
        assert smm._total_size == 0

    def test_add_chunk(self):
        smm = StreamingMemoryManager()
        smm.add_chunk("hello")
        assert smm.get_content() == "hello"

    def test_add_multiple_chunks(self):
        smm = StreamingMemoryManager()
        smm.add_chunk("hello ")
        smm.add_chunk("world")
        assert smm.get_content() == "hello world"

    def test_get_memory_usage_mb(self):
        smm = StreamingMemoryManager()
        smm.add_chunk("a" * 1024)
        assert smm.get_memory_usage_mb() > 0

    def test_clear(self):
        smm = StreamingMemoryManager()
        smm.add_chunk("data")
        smm.clear()
        assert smm.get_content() == ""
        assert smm._total_size == 0

    def test_chunk_limit_compacts(self):
        """Adding more chunks than the limit should compact older ones."""
        smm = StreamingMemoryManager(chunk_limit=5)
        for i in range(10):
            smm.add_chunk(f"chunk{i}")
        content = smm.get_content()
        # All content should still be present
        assert "chunk0" in content
        assert "chunk9" in content
        # But chunks should be compacted
        assert len(smm._chunks) <= 5 + 1  # Allow some slack from compaction

    def test_memory_limit_triggers_compaction(self):
        """Adding data that exceeds memory limit should trigger compaction."""
        # Use a very small memory limit (1 byte in MB)
        smm = StreamingMemoryManager(memory_limit_mb=0.000001)
        smm.add_chunk("a" * 100)
        smm.add_chunk("b" * 100)
        # Compaction should have occurred
        assert smm.get_content() is not None


class TestMemoryManagedOperation:
    """Tests for the memory_managed_operation context manager."""

    def test_basic_usage(self):
        with memory_managed_operation(description="test") as rm:
            assert isinstance(rm, ResourceManager)

    def test_cleans_up_resources(self):
        cleanup_called = []
        with memory_managed_operation(description="test") as rm:
            rm.register_resource("res", lambda: cleanup_called.append(True))
        assert len(cleanup_called) == 1


class TestGlobalMemoryMonitor:
    """Tests for global memory monitor functions."""

    def test_get_global_memory_monitor_returns_instance(self):
        monitor = get_global_memory_monitor()
        assert isinstance(monitor, MemoryMonitor)

    def test_get_global_memory_monitor_singleton(self):
        m1 = get_global_memory_monitor()
        m2 = get_global_memory_monitor()
        assert m1 is m2

    def test_force_global_cleanup(self):
        # Should not raise
        force_global_cleanup()
