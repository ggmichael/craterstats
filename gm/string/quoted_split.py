# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 20:16:35 2020

@author: Ton van den Heuvel
"""

import re

def quoted_split(s):
    def strip_quotes(s):
        if s and (s[0] == '"' or s[0] == "'") and s[0] == s[-1]:
            return s[1:-1]
        return s
    return [strip_quotes(p).replace('\\"', '"').replace("\\'", "'") \
            for p in re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|[^\s]+', s)]