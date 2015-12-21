# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "2.1.0"

"""
Загружает настройки QSS для виджетов
"""

from os import listdir, sep
from itertools import chain


def get_style_sheet(path="./gui/styles/", qss='', target=None, ignored=None):
    """
    Если указан параметр target то параметр ignored будет проигнорирован (
    забавная ирония :) ) Название файлов для target и ignored указывать с
    расширением
    :param path: str (путь к стилям)
    :param qss: str (содержимое фалов стилей)
    :param target: итерируемый обхект (если нужно загрузить определенные файлы)
    :param ignored: итерируемый объект (если нужно какие то файлы
                                                            проигнорировать)
    :return: str
    """
    filter_ = lambda l1, l2: set(l1).difference(set(l2))
    if path[-1] not in sep: path += sep
    qss_main = ["QWidget.styl", "Main.styl", "Animation.styl"]
    if ignored:
        qss_main += ignored

    if target:
        qss_files = target
    else:
        try:
            qss_files = chain([qss_main[0]], filter_(listdir(path), qss_main), [qss_main[1]])
        except FileNotFoundError:
            return None

    for qss_file in qss_files:
            with open(path + qss_file) as f:
                qss += f.read()

    return qss
