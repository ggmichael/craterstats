
import numpy as np

def normal(m,s,x,cumulative=False):
  #m - mean
  #s - sd
  #x - point to evaluate

  if cumulative:
      return 0.5 * (1 + np.erf((x - m) / (s * np.sqrt(2.))))
  else:
      return np.exp(-((x-m)**2)/(2*s**2))/(s*np.sqrt(2*np.pi))


if __name__ == '__main__':
    pass
    # x=gm_scl(findgen(300),out_range=[0.,x_max])
    # plot,x,gm_normal(m,s,x,cumulative=cumulative)
