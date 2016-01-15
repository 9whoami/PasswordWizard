# -*- coding: utf-8 -*-
__author__ = 'whoami'

from PyQt4 import QtGui
from .get_style import get_style_sheet


def message_box(*args, parent=None):
    """
    Icons
    QMessageBox.Question
    QMessageBox.Information
    QMessageBox.Warning
    QMessageBox.Critical

    Buttons
    Abort = 262144
    AcceptRole = 0
    ActionRole = 3
    Apply = 33554432
    ApplyRole = 8
    ButtonMask = -769
    Cancel = 4194304
    Close = 2097152
    Critical = 3
    Default = 256
    DestructiveRole = 2
    Discard = 8388608
    Escape = 512
    FirstButton = 1024
    FlagMask = 768
    Help = 16777216
    HelpRole = 4
    Ignore = 1048576
    Information = 1
    InvalidRole = -1
    LastButton = 134217728
    No = 65536
    NoAll = 131072
    NoButton = 0
    NoIcon = 0
    NoRole = 6
    NoToAll = 131072
    Ok = 1024
    Open = 8192
    Question = 4
    RejectRole = 1
    Reset = 67108864
    ResetRole = 7
    RestoreDefaults = 134217728
    Retry = 524288
    Save = 2048
    SaveAll = 4096
    Warning = 2
    Yes = 16384
    YesAll = 32768
    YesRole = 5
    YesToAll = 32768

    :param args: message text, buttons, icon in message_box, window title, window icon
    :return:
    """
    confirmation_ok = (1024, 16384,)
    message_wnd = QtGui.QMessageBox(parent)

    try:
        message_wnd.setStyleSheet(get_style_sheet(target=("QMessageBox.styl",)))

        message_wnd.setText(args[0] if len(args) >= 1 else None)
        message_wnd.setStandardButtons(
            args[1] if len(args) >= 2 else QtGui.QMessageBox.Ok)
        message_wnd.setIcon(args[2] if len(args) >= 3
                            else QtGui.QMessageBox.NoIcon)

        message_wnd.setWindowTitle(args[3] if len(args) >= 4 else None)
        message_wnd.setWindowIcon(args[4] if len(args) >= 5
                                  else QtGui.QIcon(None))
    except TypeError as e:
        print(e)
        return False
    return message_wnd.exec_() in confirmation_ok
