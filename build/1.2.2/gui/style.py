# -*- coding: cp1251 -*-
__author__ = 'whoami'

from os import listdir
from itertools import chain


def get_style_sheet(path="./gui/styles/", qss=''):
    set_ = ["QWidget.styl", "Main.styl"]
    buf = set(set_)
    qss_files = set(listdir(path))
    qss_files = qss_files - buf

    for qss_file in chain([set_[0]], qss_files, [set_[1]]):
        with open(path + qss_file) as f:
            qss += f.read()

    return qss