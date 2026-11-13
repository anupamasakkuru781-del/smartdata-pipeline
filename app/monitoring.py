
import time
import psutil
import os
import threading


class PipelineMonitor:

    def __init__(self, interval=0.1):
        self.process = psutil.Process(os.getpid())

        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0

        self.interval = interval
        self.stop_event = threading.Event()
        self.monitor_thread = None

    def _monitor_memory(self):
        while not self.stop_event.is_set():

            current_memory = (
                self.process.memory_info().rss / (1024 * 1024)
            )

            self.peak_memory = max(
                self.peak_memory,
                current_memory
            )

            self.stop_event.wait(self.interval)

    def start(self):
        self.start_time = time.perf_counter()

        self.start_memory = (
            self.process.memory_info().rss / (1024 * 1024)
        )

        self.peak_memory = self.start_memory

        self.stop_event.clear()

        self.monitor_thread = threading.Thread(
            target=self._monitor_memory,
            daemon=True
        )

        self.monitor_thread.start()

        print("\nPipeline monitoring started.")

    def get_memory_usage(self):
        memory = self.process.memory_info().rss

        return round(
            memory / (1024 * 1024),
            2
        )

    def stop(self):

        if self.start_time is None:
            raise RuntimeError(
                "Monitoring has not been started"
            )

        self.stop_event.set()

        if self.monitor_thread is not None:
            self.monitor_thread.join()

        end_time = time.perf_counter()

        end_memory = self.get_memory_usage()

        execution_time = end_time - self.start_time

        metrics = {
            "execution_time_seconds": round(
                execution_time, 2
            ),
            "start_memory_mb": round(
                self.start_memory, 2
            ),
            "end_memory_mb": end_memory,
            "peak_memory_mb": round(
                max(self.peak_memory, end_memory), 2
            ),
            "memory_change_mb": round(
                end_memory - self.start_memory, 2
            )
        }

        print("\nPipeline Performance Report")
        print("---------------------------")

        print(
            f"Execution time: "
            f"{metrics['execution_time_seconds']} seconds"
        )

        print(
            f"Starting memory: "
            f"{metrics['start_memory_mb']} MB"
        )

        print(
            f"Ending memory: "
            f"{metrics['end_memory_mb']} MB"
        )

        print(
            f"Peak memory: "
            f"{metrics['peak_memory_mb']} MB"
        )

        print(
            f"Memory change: "
            f"{metrics['memory_change_mb']} MB"
        )

        return metrics
