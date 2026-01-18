# Test memory module

from council_ai.core import MemoryMonitor, ResourceManager


def test_memory_monitor_basic():
    monitor = MemoryMonitor(memory_threshold_mb=100.0, enable_auto_cleanup=False)
    assert monitor.get_memory_usage_mb() >= 0
    stats = monitor.get_stats()
    assert "current_memory_mb" in stats


# Test resource manager
def test_resource_manager():
    rm = ResourceManager()
    rm.register_resource("test")
    assert len(rm._resources) == 1
