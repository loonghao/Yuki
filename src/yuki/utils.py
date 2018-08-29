# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""
# Import built-in modules
import logging
import os
import sys
import traceback
from functools import wraps
from tempfile import mkdtemp

import yaml
from PySide import QtCore, QtGui
# Import third-party modules
from addict import Dict

# Import local modules
from yuki.error import YukiError


def load_style_sheet(style_file, element_dir=''):
    """

    Args:
        style_file:
        element_dir:

    Returns:

    """
    with open(style_file, "r") as css_file:
        data = css_file.read().strip('\n')
        path = element_dir.replace('\\', '/')
        print(path)
        data = data.replace('<PATH>', path)
        return data


def get_temp_dir(suffix='yuki', dir_=None):
    return mkdtemp(suffix, dir=dir_)


def attr_dict(data):
    lists = list()
    if isinstance(data, list):
        for r in data:
            if isinstance(r, dict):
                lists.append(Dict(r))
        return lists
    elif isinstance(data, dict):
        return Dict(data)
    else:
        return data


def entity_data(function):
    def _deco(*args, **kwargs):
        lists = []
        return_value = function(*args, **kwargs)
        if isinstance(return_value, list):
            for r in return_value:
                if isinstance(r, dict):
                    lists.append(Dict(r))
            return lists
        elif isinstance(return_value, dict):
            return Dict(return_value)
        else:
            return return_value

    return _deco


def create_missing_directories(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def load_yaml(file_path, return_entity=False):
    with open(file_path, 'r') as f:
        data = yaml.load(f)
    if return_entity:
        return attr_dict(data)
    return data


def get_file_ext(path):
    if os.path.splitext(path)[1]:
        ext = os.path.splitext(path)[1]
        ext = ext.replace(".", "")
        return ext
    else:
        return ""


class WaitCursorMgr(object):
    """Safe way to manage wait cursors.

    Example:
        with WaitCursorMgr():
            doSomeHeavyOperation()

    """

    def __enter__(self):
        """Set the QApplication cursor to wait cursor."""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the original cursor."""
        QtGui.QApplication.restoreOverrideCursor()


def wait_cursor():
    """Wait cursor decorator to manage the cursor scope.

    Example:
        @wait_cursor()
        def do_some_heavy_operation():

    """

    def decorator(func):
        """Wrap function.

        Args:
            func (object): Object of function.

        Returns:
            object: Instance object.

        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrap function for WaiCursorMgr.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                object: Instance object.

            """
            with WaitCursorMgr():
                return func(*args, **kwargs)

        return wrapper

    return decorator


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
        # pylint: disable=global-variable-undefined, invalid-name
        logger = logging.getLogger(__name__)
        global trace_type
        try:
            return func(*args, **kwargs)
        except Exception, err:  # noqa: F841 # pylint: disable=unused-variable
            try:
                # Extract the stack trace for the current exception.
                err_type, value, trace_type = sys.exc_info()
                tb_stack = traceback.extract_tb(trace_type)
            finally:
                # See warning in sys.exc_type docs for why this is deleted
                #  here.
                del trace_type
            # Format the traceback, excluding our current level.
            format_trace = traceback.format_list(tb_stack[1:])
            result = format_trace + traceback.format_exception_only(err_type,
                                                                    value)
            err_msg = ' '.join(result)
            logger.error(err_msg)
            raise YukiError(err_msg)

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


def progress_bar(func):
    """Wrap function of progress bar.

    Args:
        func (object): Name of the function.

    Returns:
        object: Instance of the function.

    """

    @wraps(func)
    def _deco(*args, **kwargs):
        """Wrap function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        with ProgressBarMrg(*args):
            return func(*args, **kwargs)

    return _deco
