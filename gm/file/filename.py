
import re

def filename(f,code,insert1=None,insert2=None,max_ext_length=4):
    
  # ;f - filename(s)
  # ;code - string containing 'pn12e' in any order/combination:
  # ;p - path; n - name (without extension); e (extension with '.'); 1,2 - insert string ; u - up (parent dir)
  # ;insert1,2 - optional strings to insert (if arrays, should agree in dim with f)
  # max_ext_length = 4  so that vicar files including dots but no extension are not cut

  # ;e.g. gm_filename("d:\tmp\fred.txt","pn1e","_en") gives "d:\tmp\fred_en.txt"
  # ;e.g. gm_filename("d:\tmp\fred.txt","ne") gives "fred.txt"
  # ;e.g. gm_filename("d:\tmp\fred.txt","une") gives "tmp/fred.txt"
  # ;e.g. gm_filename("F:\broom\ortho-090\nd.l3_he330_0000.tif","p1une",'nd\') gives "F:\broom\nd\ortho-090\nd.l3_he330_0000.tif"
  
  if type(f) is list:
      return [filename(e,code,insert1=insert1,insert2=insert2) for e in f]

  m = re.search(r'(?P<path>.*?)(?P<name>[\.\w-]*?)(?P<ext>(\.\w{1,'+str(max_ext_length)+'})?$)', f)

  path=m['path']
  name=m['name']
  ext = m['ext']

  out=''  
  for ch in code[::-1]:
    if ch=='p':
        out=path+out
    elif ch=='n':
        out=name+out
    elif ch=='e':
        out=ext+out
    elif ch=='1':
        out=insert1+out
    elif ch=='2':
        out=insert2+out
    #elif ch=='u':
        # p=stregex(path,"[^\\|^/]*[\\|/]$")
        # out=path.substring(p)+out
        # path=path.remove(p) 

  return out

