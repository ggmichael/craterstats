# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:11:08 2020

@author: gmichael
"""

import re
import gm


def gmrts_simple_value(s): #s contains one keyword only (possibly multi-line value)
  
    if s.startswith('*'): #no need for pointer, since using lists: just ignore
        s=s[1:]
    
    if s.startswith('['):
        w=s.strip('[] \n').split(',')
        r=[gm.strip_quotes(e.strip('\n ')) for e in w]
        
    elif s.startswith('('):   
        w=s.strip('() \n').split(',')
        r=[gm_strip_quotes(e.strip('\n ')) for e in w]
    
    elif s.startswith('{'):  #declare ascii table: should be tag names after (otherwise, was structure)   
        w=s.splitlines()
        tag0=w[0].split(',')      
        tag=[e.strip('{ ') for e in tag0]      
        
        r={t:[] for t in tag}
        for row in w[1:]:
            #v=row.split() #not yet implemented - quoted string split
            v=gm.quoted_split(row)
            if v[0]=='}': break
            for t in tag:
                r[t].append(v.pop(0) if len(v)>0 else '')
            
    else: 
        r=s.strip(' \n')
        if r[0] in ['"',"'"]: r=gm.strip_quotes(r)
    
    return r



def gmrts_merge(s1,sr): # merge single tag structure into cumulative structure

    # if first is duplicate of tag in remainder -> add to array
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
  



def gmrts_evaluate(s):

    # separate off first definition
    # find keyword followed by either struct_value, multiline text_value, or simple value; then following keyword
    m=re.search("(?ms)^\s*(?P<keyword>[\w\.]*\^?)\s*=\s*(\{\s*$(?P<struct_value>[^{]*)^\s*\}.*?|\"\s*$(?P<text_value>[^{]*)^\s*\".*?|(?P<value>.*?))^\s*(?P<keyword2>[\w\.]*\^?) *=",s+"\nend=")
      
    if not m: return -1 #no definitions to process 
    
    keyword=m['keyword']
    if keyword.endswith('^'): keyword='ptr_'+keyword.rstrip('^')    
     
    
    #if structure, send contents for evaluation
    if m['struct_value'] != None:  
        r=gmrts_evaluate(m['struct_value'])
       
    elif m['text_value'] != None: #text block
        r=m['text_value']
    
    #if simple value, evaluate directly      
    else: r=gmrts_simple_value(m['value']) #simple value
    
    #new entry
    dict1={keyword:r}     
    
    #evaluate remainder  
    remainder = s[m.start('keyword2'):] if m['keyword2'] != None else ''    
    dict_r=gmrts_evaluate(remainder)
    
    #join together  
    dict_out=gmrts_merge(dict1,dict_r)
    
    return dict_out #structure encapsulated by s



def read_textstructure(p,from_string=False):
    #p1 - if string, treat as filename; if strarr, process directly
    #,doubleq - set if want table strings allowed delimited by double quotes
    
    if not from_string:
        s=gm.read_textfile(p, ignore_hash=True, strip=';', as_string=True) #read and remove comments
    else:
        s=p
        
    return gmrts_evaluate(s)


if __name__ == '__main__':
    c=gm.read_textstructure("../../craterstats3/def/default.plt")
    print(c)


















































