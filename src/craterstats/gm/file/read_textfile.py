#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

from . import file_exists

def read_textfile(filename,n_lines=-1,ignore_blank=False,ignore_hash=False,strip=None,as_string=False):
    
  # ;/ignore_hash - ignore # lines
  # ;/ignore_blank - ignore blank lines
  # ;option n_lines - read n lines
  # ;remove trailing comments after strip symbol (e.g. ';')
  # as_string - concatenate into single string

  if not file_exists(filename) :
      return 'no file'

  with open(filename, 'r', encoding='utf-8-sig') as file: # encoding='utf-8-sig' removes BOM if present
    if n_lines !=-1: 
        s=[]
        for i in range(n_lines): s.append(file.readline().strip())
    else:
        s=file.read().splitlines()
  
  if ignore_blank: 
      s = [e for e in s if e != '']

  if ignore_hash:
      s = [e for e in s if not e.lstrip().startswith('#')]  

  if strip != None:
      s = [e.partition(strip)[0] for e in s]  #still cuts within quoted strings
      
  if as_string:
      s='\n'.join(s)
      
      
#   if n_elements(strip) ne 0 then begin
#     dq='"'
#     cc=strip
#     dq1='"[^"]*"'
#     rgx="^([^'"+dq+cc+"]*('[^']*'|"+dq1+"))*[^"+cc+"]*"
#     s=stregex(s,rgx,/extract)
#     ;  print,"this; shouldn't be deleted"
#     ;  print,' or this;'
#     s=(stregex(s,"^.*[^ \t].*$",/extract)) ;cut blank/tab lines to zero  
#   end

  return s

read_textfile(r"d:\mydocs\tmp\test.txt")