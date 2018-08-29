# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""
# Import third-party modules
from PySide import QtGui


class MessageDisplay(QtGui.QDialog):
    """Shows dialogues as stand alone application i.e. can be called from scripts
    that have no QApplication running.
    """

    INFO = QtGui.QMessageBox.information
    WARNING = QtGui.QMessageBox.warning
    CRITICAL = QtGui.QMessageBox.critical
    ABOUT = QtGui.QMessageBox.about

    def __init__(self, title, message, dialog=None):
        """
        Args:
            title (str): Window title.
            message (str): Text of body.
            dialog (QtGui.QMessageBox): information, warning, critical, about
                                         Default is INFO.

        """
        utf8_message = QtGui.QApplication.translate("ship_console",
                                                    message,
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8)
        if not dialog:
            dialog = MessageDisplay.INFO
        self.app = QtGui.QApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])
        super(MessageDisplay, self).__init__()
        dialog(self, title, utf8_message)
