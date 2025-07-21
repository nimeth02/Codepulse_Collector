# utils/threading.py
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
import traceback

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            traceback.print_exc()
            self.signals.error.emit(e)

def worker_spinner(parent, progress_bar, task_fn, on_success, on_error):
    """
    Utility to run a task with a progress bar spinner and callbacks.

    :param parent: The parent widget holding the threadpool
    :param progress_bar: The QProgressBar to show/hide
    :param task_fn: A no-arg function to run in the background
    :param on_success: Callback for success (runs on main thread)
    :param on_error: Callback for error (runs on main thread)
    """
    # Show spinner
    progress_bar.setVisible(True)
    progress_bar.setRange(0, 0)
    progress_bar.repaint()  # Force update in case UI is stuck

    from PyQt6.QtWidgets import QApplication
    QApplication.processEvents()

    # Wrap success to stop spinner
    def wrapped_success(result):
        progress_bar.setVisible(False)
        on_success(result)

    def wrapped_error(e):
        progress_bar.setVisible(False)
        on_error(e)

    # Start worker
    worker = Worker(task_fn)
    worker.signals.finished.connect(wrapped_success)
    worker.signals.error.connect(wrapped_error)
    parent.threadpool.start(worker)