



import numpy as np

def poly(p,x):
    """Evaluate polynomial with coefficients in ASCENDING order."""

    p1=p[::-1]
    return np.polyval(p1,x)