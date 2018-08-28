# Import built-in modules
import os
import sys


def resource_path(relative_path=None):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    if not relative_path:
        return base_path
    return os.path.join(base_path, relative_path)

os.environ['PIPELINE_ICON'] = 'logo.ico'
ROOT = os.path.dirname(__file__)
APP_NAME = 'yuki'
APP_VERSION = '0.6.2'
os.environ['BUILD_VERSION'] = APP_VERSION
