#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

#import craterstats.gm.string.sigfigs as sigfigs
from .sigfigs import sigfigs

def scientific_notation(v,e1=None,e2=0,sf=3,force=False, MathML=False, unit=None):
    '''
    Convert number to latex/MathML-style scientific notation string

    values >0.01 and <10000 are shown without multiplier unless force=True

    :param v: value to convert
    :param e1,e2: plus/minus values
    :param sf: number of significant figures
    :param force: force notation even for low-value exponents
    :return: formatted string
    '''

    u = ('', '')
    if unit is not None: #add more as needed
        u = {'km-2':(r'$ km$^{-2}','<msup><mtext>&#8239;km</mtext><mtext>-2</mtext></msup>'),
             'km2': (r'$ km$^{2}', '<msup><mtext>&#8239;km</mtext><mtext>2</mtext></msup>')
             }[unit]

    if v==0 or -2 < np.log10(abs(v)) < 4 and not force: # avoid log(0)
        st = sigfigs(v, sf)
        exp = 0
    else:
        s0 = f"{v:.{sf - 1}e}"
        s = s0.split('e')
        exp = int(s[1])
        st = s[0]

    if e1 is not None:
        e1s = sigfigs((e1 - v)/10**exp, sf - 1)
        e2s = sigfigs((v - e2)/10**exp, sf - 1)
        if MathML:
            st = '<msubsup><mtext>'+st+'</mtext><mtext>&#x2212;'+e2s+'</mtext><mtext>+'+e1s+'</mtext></msubsup>'
        else:
            st += '^{+' + e1s + '}_{-' + e2s + '}'

    if MathML:
        st = ('<math xmlns="http://www.w3.org/1998/Math/MathML">'+st
              +('' if exp==0 else '<mo>&#183;</mo><msup><mtext>10</mtext><mtext>'+str(exp)+'</mtext></msup>')
              +u[1]+'</math>')
    else:
        st = '$' + st + ('' if exp==0 else r'\cdot10^{'+str(exp)+'}')+u[0] + '$'

    return st

if __name__ == '__main__':
    print(scientific_notation(3.14e9,3.17e9,2.6e9))
    print(scientific_notation(3.14e9,3.17e9,2.6e9,unit='km-2'))
    print(scientific_notation(3.14e9,3.17e9,2.6e9, MathML=True))
    print(scientific_notation(3.14e9,3.17e9,2.6e9,unit='km-2', MathML=True))
    print(scientific_notation(3.14,3.17,2.6))
    print(scientific_notation(3.14,3.17,2.6,unit='km-2'))
    print(scientific_notation(3.14,3.17,2.6, MathML=True))
    print(scientific_notation(3.14,3.17,2.6,unit='km-2', MathML=True))
