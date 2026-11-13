
import time
import pytest

from app.monitoring import PipelineMonitor


def test_monitor_start_and_stop():
    monitor = PipelineMonitor()

    monitor.start()
    time.sleep(0.2)

    metrics = monitor.stop()

    assert metrics["execution_time_seconds"] >= 0
    assert metrics["start_memory_mb"] > 0
    assert metrics["end_memory_mb"] > 0


def test_memory_usage():
    monitor = PipelineMonitor()

    memory = monitor.get_memory_usage()

    assert memory > 0


def test_stop_without_start():
    monitor = PipelineMonitor()

    with pytest.raises(RuntimeError):
        monitor.stop()


def test_memory_change():
    monitor = PipelineMonitor()

    monitor.start()
    time.sleep(0.2)

    metrics = monitor.stop()

    assert "memory_change_mb" in metrics


def test_peak_memory_is_recorded():
    monitor = PipelineMonitor()

    monitor.start()
    time.sleep(0.3)

    metrics = monitor.stop()

    assert "peak_memory_mb" in metrics
    assert metrics["peak_memory_mb"] >= metrics["start_memory_mb"]
    assert metrics["peak_memory_mb"] >= metrics["end_memory_mb"]
