#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import re

# try:
#     import importlib.resources as importlib_resources #Fails on 3.8 - no 'importlib.resources.files'
# except ImportError:
#     # Try backported to PY<37 `importlib_resources`.
import importlib_resources
import pathlib

def read_textfile(filename,n_lines=None,ignore_blank=False,ignore_hash=False,strip=None,as_string=False,
                  substitute_resource=None):
    '''

    :param filename: full filepath
    :param n_lines: number of lines to read (all, if omitted)
    :param ignore_blank: ignore blank lines
    :param ignore_hash: ignore # lines
    :param strip: remove trailing comments after strip symbol (e.g. ';')
    :param as_string: concatenate into single string, joined with '\n'
    :return: file contents as list of strings or single string
    '''

    #:param: substitute_resource {packagename,path}, e.g. {'package':'craterstats','path':'src/craterstats/'}

    if 'substitute_resource' not in read_textfile.__dict__: read_textfile.substitute_resource=None
    if substitute_resource is not None: read_textfile.substitute_resource=substitute_resource

    if read_textfile.substitute_resource is not None and filename.startswith(read_textfile.substitute_resource['path']):
        rpath=filename[len(read_textfile.substitute_resource['path']):]
        rpath1=pathlib.Path(rpath)
        pkg='.'.join([read_textfile.substitute_resource['package']]+list(rpath1.parts[0:-1]))
        rname=rpath1.parts[-1]
        trav = importlib_resources.files(pkg) / rname
        with importlib_resources.as_file(trav) as src:
            with open(src, 'r', encoding='utf-8-sig') as file:
                s = file.read().splitlines()
    else:
        with open(filename, 'r', encoding='utf-8-sig') as file: # encoding='utf-8-sig' removes BOM if present
            if n_lines is not None:
                s=[]
                for i in range(n_lines): s.append(file.readline().strip())
            else:
                s=file.read().splitlines()

    if ignore_blank:
        s = [e for e in s if e != '']

    if ignore_hash:
        s = [e for e in s if not e.lstrip().startswith('#')]

    if strip is not None:
        c = re.compile(r'(("[^"]*?")|(\'[^\']*?\')|[^;\'"]*)*') # avoid splitting within quoted string
        s = [c.match(e)[0] for e in s]

    if as_string:
        s='\n'.join(s)

    return s



