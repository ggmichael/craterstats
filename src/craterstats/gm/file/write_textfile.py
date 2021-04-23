#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

def write_textfile(filename,s):
    '''
    write string or list of strings to text file

    :param filename: filename
    :param s: string or list of strings
    :return: none
    '''
    
    with open(filename, 'w') as file:
        file.writelines('\n'.join(s))