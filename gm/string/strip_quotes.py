# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 21:23:45 2020

@author: gmichael
"""

def strip_quotes(s):
    if s[0]==s[-1] and s[0] in ['"',"'"]:
        return s[1:-1]
    else:
        return s