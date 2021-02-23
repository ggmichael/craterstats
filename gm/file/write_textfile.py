# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 10:34:00 2020

@author: gmichael
"""

def write_textfile(filename,s):
    
    with open(filename, 'w') as file:
        file.writelines('\n'.join(s))
            
        