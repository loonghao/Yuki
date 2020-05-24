# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""

# Import built-in modules
import logging
import traceback
import os
from functools import wraps

# Import third-party modules
from PySide2 import QtWidgets
from PySide2 import QtCore

# Import local modules
from yuki.error import YukiError


def create_missing_directories(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def get_file_ext(path):
    if os.path.splitext(path)[1]:
        ext = os.path.splitext(path)[1]
        ext = ext.replace(".", "")
        return ext
    else:
        return ""


class WaitCursorMgr(object):
    """Safe way to manage wait cursors.

    Automatically restoreOverrideCursor every time the function is completed.

    Example:
        >>> import time
        >>> with WaitCursorMgr():
        ...     time.sleep(3)

    """

    def __enter__(self):
        """Set the QApplication cursor to wait cursor."""
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def __exit__(self, *exc_info):
        """Reset the original cursor.

        Args:
            *exc_info: exc length argument list.

        """
        QtWidgets.QApplication.restoreOverrideCursor()


def wait_cursor(func):
    """Wait cursor decorator to manage the cursor scope.

    Example:
        >>> @wait_cursor
        >>> def hello():
        ...     print('hello')

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrap function for WaiCursorMgr.

        Args:
            args: Arguments to pass into the wrapper.
            kwargs: Arguments to pass into the wrapper.

        Returns:
            object: Instance object.

        """
        with WaitCursorMgr():
            return func(*args, **kwargs)

    return wrapper


class ProgressBarMgr(object):  # pylint: disable=too-few-public-methods
    """Manage the ProgressBar reset and show each time it runs.

    Note:
        This function only work with the gui.

    Example:
        >>> import time
        >>> with ProgressBarMgr():
        ...     time.sleep(3)

    """

    def __init__(self, parent_widget, *args):
        """Wrap and inherit the progress bar.

        Args:
            parent_widget (QtWidgets.QWidget): The parent widget of
                progressBar, note here that the progress bar object name
                must be `progress_bar`.
            *args: Arguments to pass into the wrapper.

        """
        self.parent_widget = parent_widget
        self.progress_bar = self.parent_widget.progress_bar
        self.visible = self.progress_bar.isVisible()

    def __enter__(self):
        """Reset and show the progress bar."""
        self.progress_bar.reset()
        self.progress_bar.show()

    def __exit__(self, *exc_info):
        """Hide the progress bar after execution.

        Decide whether to hide based on the invisible state saved before
        this progress bar.

        Args:
            *exc_info: exc length argument list.

        """
        if not self.visible:
            self.progress_bar.hide()


def progress_bar(func):
    """Wrap function of progress bar.

    Example:
        >>> import time
        >>> @progress_bar
        >>> def do_some_heavy_operation():
        ...     time.sleep(3)

    Args:
        func (str): Name of the function.

    Returns:
        object: Instance of the function.

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrap function.

        Args:
            args: Arguments to pass into the wrapper.
            kwargs: Arguments to pass into the wrapper.

        """
        with ProgressBarMgr(*args):
            return func(*args, **kwargs)

    return wrapper


def catch_error_message(func):
    """Extract the stack trace for the current exception.

    Args:
        func (Object): Function object.

    Returns:
        Object: Instance of function.

    """

    @wraps(func)
    def _deco(*args, **kwargs):
        """Wrap function for errors.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: Instance function object.

        """
        try:
            return func(*args, **kwargs)
        except Exception as err:  # noqa: F841 # pylint: disable=unused-variable
            message = str(err)
            logger = logging.getLogger(__name__)
            logger.exception(message)
            msg = QtWidgets.QMessageBox()
            msg.setText(message)
            msg.exec_()
            # raise YukiError(message)
    return _deco


class ProgressBarMrg(object):  # pylint: disable=too-few-public-methods
    """Safe way to manage ProgressBar.

    Example:
        with ProgressBarMrg():
            do_some_heavy_operation()

    """

    def __init__(self, *args):
        """Wrap and inherit the progress bar.

        Args:
            *args: Variable length argument list.

        """
        self.parent = args[0]
        self.progress_bar = self.parent.progress_bar

    def __enter__(self):
        """Reset and show the progress bar."""
        self.progress_bar.reset()
        self.progress_bar.show()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Hide the progress bar."""
        self.progress_bar.hide()

