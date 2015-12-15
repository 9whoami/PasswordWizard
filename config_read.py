# -*- coding: utf-8 -*-
__author__ = 'home'

from configparser import ConfigParser, Error


def write_cfg(file, section, option, value):
    parser = ConfigParser()
    parser.read(file)

    try:
        parser.set(section, option, str(value))
        with open(file, "w") as f:
            parser.write(f)

    except (Error, TypeError) as e:
        del parser
        print(e)
        raise SystemExit
    del parser


def read_cfg(*args, **kwargs):
    if args:
        file_info = dict(file=args[0],
                         section=args[1])
    elif kwargs:
        file_info = kwargs
    else:
        return None

    # create parser and read_cfg ini configuration file
    parser = ConfigParser()
    parser.read(file_info["file"])

    # get section, default to mysql
    result = {}
    if parser.has_section(file_info["section"]):
        items = parser.items(file_info["section"])
        for item in items:
            result[item[0]] = item[1]
    else:
        del parser
        raise SystemExit(
            '{0} not found in the {1} file'.format(section, filename))

    del parser
    return result
