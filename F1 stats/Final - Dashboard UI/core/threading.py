"""
Shared worker infrastructure for running API and telemetry tasks off the UI thread.
"""

from typing import Any, Callable, Dict

from PyQt6 import QtCore


class Worker(QtCore.QThread):
    """Generic worker that executes a callable and emits results."""

    result_ready = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception)

    def __init__(self, fn: Callable[..., Any], **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.kwargs: Dict[str, Any] = kwargs

    def run(self) -> None:
        try:
            result = self.fn(**self.kwargs)
            self.result_ready.emit(result)
        except Exception as exc:  # pylint: disable=broad-except
            self.error.emit(exc)


def run_in_thread(fn: Callable[..., Any], on_result: Callable[[Any], None], on_error: Callable[[Exception], None], **kwargs: Any) -> Worker:
    """
    Helper to start a worker and connect signals.
    Returns the started worker to keep a reference alive.
    """
    worker = Worker(fn, **kwargs)
    worker.result_ready.connect(on_result)
    worker.error.connect(on_error)
    worker.start()
    return worker
