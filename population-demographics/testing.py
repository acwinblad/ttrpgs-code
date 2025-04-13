#!/usr/bin/python3

import numpy as np
from scipy.stats import poisson
from matplotlib import pyplot as plt

chances = np.array([0.05,0.25,0.70])
plt.figure()
for j, chance in enumerate(chances):
  prob = poisson.rvs(0.5+ 1*(chance), size=1000)
  end = np.max(prob)+1
  t = np.arange(0,end)-0.5
  plt.hist(prob, bins=t, histtype='step', align='mid', density=True)
plt.show()
plt.close()
