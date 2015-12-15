# -*- coding: utf-8 -*-
__author__ = 'home'

from configparser import ConfigParser, Error


def write_cfg(file, section, option, value):
    parser = ConfigParser()

    try:
        parser.read(file)
        parser.set(section, option, str(value))
        with open(file, "w") as f:
            parser.write(f)

    except (Error, TypeError) as e:
        del parser
        raise SystemExit(e)
    else:
        del parser


def read_cfg(*args, **kwargs):
    if args:
        file_info = dict(file=args[0],
                         section=args[1])
    elif kwargs:
        file_info = kwargs
    else:
        return None
    parser = ConfigParser()
    try:
        parser.read(file_info["file"])
        result = {}
        if parser.has_section(file_info["section"]):
            items = parser.items(file_info["section"])
            for item in items:
                result[item[0]] = item[1]
            return result
        else:
            del parser
            raise SystemExit(
                '{0} not found in the {1} file'.format(section, filename))
    except Error as e:
        print(e)
    else:
        del parser
