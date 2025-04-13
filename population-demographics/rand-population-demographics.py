#!/usr/bin/python3

import numpy as np
from scipy.stats import skewnorm, poisson
import json

filepath = './population-data-zorus.json'
try:
  with open(filepath, 'r') as f:
    data = json.load(f)

  commonancestry = list(data.get('Common', {}).keys())
  commonodds = list(data.get('Common', {}).values())

  uncommonancestry = list(data.get('Uncommon', {}).keys())
  uncommonodds = list(data.get('Uncommon', {}).values())

  rareancestry = list(data.get('Rare', {}).keys())
  rareodds = list(data.get('Rare', {}).values())
  print('Population data loaded successfully!')

except Exception as e:
  print(f'Error loading file: {str(e)}')

vastmajority = False

ndecimals = 0
if ndecimals > 0:
  scale = 10**(ndecimals)
  width = 3+ndecimals
else:
  scale = 1
  width = 2

commonchance = 0.7
uncommonchance = 0.25
rarechance = 0.05

ncmax = np.count_nonzero(commonodds)
nucmax = np.count_nonzero(uncommonodds)
nrmax = np.count_nonzero(rareodds)

commonodds /= np.sum(commonodds)
uncommonodds /= np.sum(uncommonodds)
rareodds /= np.sum(rareodds)

maxiterations = 0

while(maxiterations<1):
  #nc = min(ncmax, np.random.geometric(1-commonchance)-1)
  #nuc = min(nucmax, np.random.geometric(1-uncommonchance)-1)
  #nr = min(nrmax, np.random.geometric(1-rarechance)-1)
  nc = min(ncmax,   poisson.rvs(0.25+2*commonchance))
  nuc = min(nucmax, poisson.rvs(0.25+2*uncommonchance))
  nr = min(nrmax,   poisson.rvs(0.25+2*rarechance))
  maxiterations = nc + nuc + nr

commonscale = np.around(27.2343*np.tan(-1.4076*(commonchance-0.5)))
uncommonscale = np.around(27.2343*np.tan(-1.4076*(uncommonchance-0.5)))
rarescale = np.around(27.2343*np.tan(-1.4076*(rarechance-0.5)))
common_dist = skewnorm.rvs(commonscale, loc=commonchance, scale=0.20, size = nc)
common_choice = np.random.choice(commonancestry, nc, replace=False, p=commonodds)
uncommon_dist = skewnorm.rvs(uncommonscale, loc=uncommonchance, scale=0.20, size = nuc)
uncommon_choice = np.random.choice(uncommonancestry, nuc, replace=False, p=uncommonodds)
rare_dist = skewnorm.rvs(rarescale, loc=rarechance, scale=0.20, size = nr)
rare_choice = np.random.choice(rareancestry, nr, replace=False, p=rareodds)

dist = np.append(common_dist, uncommon_dist)
dist = np.append(dist, rare_dist)
choice = np.append(common_choice, uncommon_choice)
choice = np.append(choice, rare_choice)
sort_idx = np.argsort(dist)[::-1]
dist = dist[sort_idx]
choice = choice[sort_idx]

if(maxiterations>1):
  tol = 2 * scale # tolerance, when remainder is less than end simulation

  remainder = 100 * scale

  if(vastmajority):
    mode = 75
    rng = int(scale * np.random.triangular(61, mode, 90))
  else:
    mode = 25 * scale
    rng = int(scale * np.random.triangular(1, mode, 50))
  # population demographic
  popdemo = np.array([rng], dtype='int')
  remainder -= rng

  iterations = 1
  while(remainder >= tol and iterations < maxiterations):
    rng = int(np.random.triangular(1 * scale,remainder//2,remainder))

    popdemo = np.append(popdemo, rng)
    remainder -= rng
    iterations += 1

  popdemo = np.sort(popdemo)[::-1]
  nmax = ncmax+nucmax+nrmax
  other_cap = min(nmax//3, np.random.randint(7,15))
  other_cap *= scale
  other_diff = remainder-other_cap

  if(other_diff <= 0):
    if(iterations < maxiterations):
      diff = maxiterations-iterations
      for i in range(diff):
        idx = np.argmax(popdemo)
        shift = np.random.randint(1,scale*(diff-i)+1)
        popdemo[idx] -= shift
        popdemo = np.append(popdemo, shift)
      popdemo = np.sort(popdemo)[::-1]
      popdemo = np.append(popdemo,remainder)
    else:
      popdemo = np.sort(popdemo)[::-1]
      popdemo = np.append(popdemo,remainder)
  else:
    popdiff1 = np.random.randint(0,other_diff+1)
    popdiff2 = other_diff-popdiff1
    popdemo[0] += max(popdiff1,popdiff2)
    popdemo[1] += min(popdiff1,popdiff2)
    popdemo = np.append(popdemo, other_cap)

  if ndecimals > 0:
    popdemo = np.round(popdemo / scale, ndecimals)


  print('%d common, %d uncommon, and %d rare ancestries' % (nc, nuc, nr))
  choice = np.append(choice,'other')
  for val, anc in zip(popdemo, choice):
    print(f'{val:{width}}' + '%: ' +anc)

else:
  print('%d common, %d uncommon, and %d rare ancestries' % (nc, nuc, nr))
  print(f'99%: {choice[0]}')
  print(' 1%: other')
