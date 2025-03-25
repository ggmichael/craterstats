#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import re

def filename(f,code,insert1=None,insert2=None,max_ext_length=4):
    r'''
    Split path, filename, extension into constituent parts and reconstruct as required

    :param f: file name or full path
    :param code: string containing any order/combination of
        p - path; n - name (without extension); e (extension with '.'); 1,2 - insert string;
        u - up (parent path); b - back (parent dir name)
    :param insert1,insert2: optional strings to insert (if arrays, should agree in dim with f)
    :param max_ext_length: max extension length (so that files including dots but no extension are not cut)
    :return: reconstructed filename or fragment(s)

    e.g. filename(r"d:\tmp\fred.txt","pn1e","_en") gives "d:\tmp\fred_en.txt"
    e.g. filename(r"d:\tmp\fred.txt","ne") gives "fred.txt"
    e.g. filename(r"d:\tmp\fred.txt","bne") gives "tmp/fred.txt"
    e.g. filename(r"F:\broom\ortho-090\nd.l3_he330_0000.tif","p1bne",'nd\\') gives 'F:\\broom\\nd\\ortho-090\\nd.l3_he330_0000.tif'
    '''

    if type(f) is list:
        return [filename(e,code,insert1=insert1,insert2=insert2) for e in f]

    m = re.search(r'(?P<path>.*?)(?P<name>[\.,= \w-]*?)(?P<ext>(\.\w{1,'+str(max_ext_length)+'})?$)', f)
    path=m['path']
    name=m['name']
    ext = m['ext']

    out=''
    for ch in code[::-1]:
        if ch=='p': out=path+out
        elif ch=='n': out=name+out
        elif ch=='e': out=ext+out
        elif ch=='1': out=insert1+out
        elif ch=='2': out=insert2+out
        elif ch in ['u','b']:
            m = re.search(r'(?P<path>.*(\\|/))(?P<parentdir>.+)', path)
            path=m['path'] if m['path'] is not None else ''
            parentdir=m['parentdir'] if m['parentdir'] is not None else ''
            out=(parentdir if ch=='b' else path)+out

    return out



