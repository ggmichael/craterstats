#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import re

from ..string.strip_quotes import strip_quotes
from ..string.quoted_split import quoted_split
from . import read_textfile


def simple_value(s):
    '''evaluate single (possibly multi-line) value'''
  
    if s.startswith('*'): #no need for pointer, since using lists: just ignore
        s=s[1:]
    
    if s.startswith('['):
        w=s.strip('[] \n').split(',')
        r=[strip_quotes(e.strip('\n ')) for e in w]
        
    elif s.startswith('('):   
        w=s.strip('() \n').split(',')
        r=[strip_quotes(e.strip('\n ')) for e in w]
    
    elif s.startswith('{'):  #declare ascii table: should be field names after (otherwise, was structure)
        w=s.splitlines()
        tag0=w[0].split(',')      
        tag=[e.strip('{ ') for e in tag0]      
        
        r={t:[] for t in tag}
        for row in w[1:]:
            v=quoted_split(row)
            if v[0]=='}': break
            for t in tag:
                r[t].append(v.pop(0) if len(v)>0 else '')
    else: 
        r=strip_quotes(s.strip(' \n'))
    
    return r


def merge(s1, sr):
    '''merge single tag structure into cumulative structure'''

    # if first is duplicate of tag in remainder (implicit array) -> add to array
    # else make union of first+remainder
    
    if type(sr) != dict: return s1
    s1_tag=list(s1)[0]
    if s1_tag in list(sr):
        if type(sr[s1_tag]) != list:
            sr.update({s1_tag:[s1[s1_tag]]+[sr[s1_tag]]})    
        else:
            sr[s1_tag].insert(0,s1[s1_tag]) 
    else:
       sr.update(s1) 
       
    return sr    


def evaluate(s):
    '''evaluate first definition; join with recursively evaluated remainder'''

    # find keyword followed by either struct_value, multiline text_value, or simple value; then following keyword
    # m=re.search(r"(?ms)^\s*(?P<keyword>[\w\.]*\^?)\s*=\s*"
    #             r"(\{\s*$(?P<struct_value>[^{]*)^\s*\}.*?|"
    #             r"\"\s*$(?P<text_value>[^{]*)^\s*\".*?|"
    #             r"(?P<value>.*?))"
    #             r"^\s*(?P<keyword2>[\w\.]*\^?) *="
    #             ,s+"\nend=")

    m=re.search(r"(?ms)^\s*(?P<keyword>[\w\.]*\^?)\s*=\s*"
                r"(\{\s+(?P<struct_value>(\{[a-zA-Z].*?\}|[^{}]*?)*?)^\s*\}.*?|"
                r"\"\s*$(?P<text_value>[^{]*)^\s*\".*?|"
                r"(?P<value>.*?))"
                r"^\s*(?P<keyword2>[\w\.]*\^?) *="
                ,s+"\nend=")
      
    if not m: return None #no definitions to process
    
    keyword=m['keyword']
    if keyword.endswith('^'): keyword='ptr_'+keyword.rstrip('^')
    
    #if structure, send contents for evaluation
    if m['struct_value'] != None:  
        r=evaluate(m['struct_value'])
       
    elif m['text_value'] != None: #text block
        r=m['text_value']
    
    #if simple value, evaluate directly      
    else: r=simple_value(m['value']) #simple value
    
    #new entry
    dict1={keyword:r}     
    
    #evaluate remainder  
    remainder = s[m.start('keyword2'):] if m['keyword2'] != None else ''    
    dict_r=evaluate(remainder)
    
    #join together  
    dict_out=merge(dict1, dict_r)
    
    return dict_out #structure from s

def read_textstructure(p,from_string=False):
    '''
    Read set of key-value pairs from text file

    :param p: filename
    :param from_string: interpret string in p directly
    :return: dictionary
    '''
    
    if not from_string:
        s=read_textfile(p, ignore_hash=True, strip=';', as_string=True) #read and remove comments
    else:
        s=p
        
    return evaluate(s)



















































