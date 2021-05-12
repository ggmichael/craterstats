#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.


def strip_quotes(s):
    '''remove matching quotes from start/end of string'''

    if len(s)>1 and s[0]==s[-1] and s[0] in ['"',"'"]:
        return s[1:-1]
    else:
        return s

