#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

def write_textfile(filename,s):
    
    with open(filename, 'w') as file:
        file.writelines('\n'.join(s))
            
        