#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

def write_textfile(filename,s,BOM=False):
    '''
    write string or list of strings to text file

    :param filename: filename
    :param s: string or list of strings
    :return: none
    '''
    
    with open(filename, 'w', encoding='utf-8-sig' if BOM else 'utf-8') as file:
        file.writelines('\n'.join(s) if type(s) is list else s)