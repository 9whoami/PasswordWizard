# -*- coding: utf-8 -*-
__author__ = 'whoami'

import string
import random


def generation(length):
    spec = '!@#$%&*?^'
    digits = string.digits
    all_symbols = spec + digits + string.ascii_letters

    count = 0
    res = []
    while count < length:
        res.append(random.choice(all_symbols))
        count += 1
    password = ''.join(res)
    return password
