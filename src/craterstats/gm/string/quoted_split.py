#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import re

from .strip_quotes import strip_quotes

def quoted_split(s,separator=r'\s'):
    r'''
    split string using separator characters, leaving separators within quoted substrings

    :param s: source string
    :param separator: default is whitespace; for comma with whitespace, use '\s,'
    :return: list of substrings
    '''

    return [strip_quotes(p).replace('\\"', '"').replace("\\'", "'") \
            for p in re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|[^'+separator+']+', s)]