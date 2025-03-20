#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import craterstats.gm as gm

def str_age(age,e1=0,e2=0,sf=3,unit=None,simple=False,no_error=False,mu=False,MathML=False):
    '''
    Convert numerical age in Ga to latex-style string, optionally with sub/superscript errors and mu uncertainty function

    :param age:
    :param e1: plus error
    :param e2: minus error
    :param sf: no of sig figs
    :param unit: force specified unit
    :param simple: don't show zero decimals (for isochrons), nor use latex-style
    :param no_error: don't show errors
    :param mu: show mu uncertainty function
    :param MathML - use MathML instead of latex. Can paste into MS Word
    :return: age string
    '''

    f = [1, 1e-3, 1e-6, 1e-9]
    unit0 = ['Ga', 'Ma', 'ka', 'a']

    if unit is not None:
        a = next((e, u) for e, u in zip(f, unit0) if unit == u)
    else:
        a = next((e, u) for e, u in zip(f, unit0) if age >= e or u =='a')

    v=age/a[0]

    if simple:
        st='{:g}'.format(v)
    else:
        st= gm.sigfigs(v, sf)

    if e1>0 and not no_error :
        e1s = gm.sigfigs(e1 / a[0], sf - 1)
        e2s = gm.sigfigs(e2 / a[0], sf - 1)
        if MathML:
            st = '<msubsup><mtext>'+st+'</mtext><mtext>&#x2212;'+e2s+'</mtext><mtext>+'+e1s+'</mtext></msubsup>'
        else:
            st += '^{+' + e1s + '}_{-' + e2s + '}'

    if simple:
        st += ' ' + a[1]
    elif MathML:
        st = ('<math xmlns="http://www.w3.org/1998/Math/MathML">'
              +('<mi>&#956;</mi>' if mu else '')+st+'<mtext>&#8239;'+a[1]+'</mtext></math>')
    else:
        st = '$' + (r'\mu' if mu else '') + st + '$ ' + a[1]

    return st


if __name__ == '__main__':
    print(str_age(.314,.11,.14))
    print(str_age(.314, .11, .14,unit='Ga',mu=True))
    print(str_age(.314, simple=True))
    print(str_age(.314, .11, .14, unit="ka"))
