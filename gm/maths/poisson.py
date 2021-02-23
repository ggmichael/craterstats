

import numpy as np

import gm

def poisson(k,lam,cumulative=False):
  #poisson pmf
  #vectorised in lambda, but not k
  
  threshold=23 #threshold for switching to normal approximation

  if k<threshold:       #poisson
      if cumulative:
          res = 0.
          for i in range(k+1):
              res += (lam**i) / np.math.factorial(i)
          return np.exp(-lam) * res

      else:
          return lam**k * np.exp(-lam) / np.math.factorial(k)

  else:                 #normal
      if cumulative:
          return gm.normal(lam, np.sqrt(lam), k, cumulative=True)
      else:
          return gm.normal(lam, np.sqrt(lam), k)




#
# import matplotlib.pyplot as plt
#
# if __name__ == '__main__':
#
#     ns=1000
#     x=np.linspace(0,100,ns)
#     fig, (ax1, ax2) = plt.subplot(1, 2)
#     for i in range(1,99):
#         ax1.plot(x,poisson(i,x),color='0' if i<30 else '0.')
#     plt.show()



