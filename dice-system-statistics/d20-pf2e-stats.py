#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

num_dice = 1
num_sides = 20

cs_nums = 20
cf_nums = 1
roll_arr = np.arange(1,num_sides+1)

hit_arr = np.arange(-1,20)+1
#hit_arr = np.arange(0,20)
hit_arr = np.arange(-5,10)
dc_arr = np.arange(10,20)
ratio_mat = np.zeros((np.size(dc_arr), np.size(hit_arr)))
ratio_mat2 = np.zeros((np.size(dc_arr), np.size(hit_arr)))

# this double for-loop could probably be written using matrix manipulation
for i, DC in enumerate(dc_arr):
  for j, H in enumerate(hit_arr):
    # check if rolls + hit are in which degree of success
    dosidx = np.zeros((4,num_sides), dtype = 'int')
    cfidx = np.where(roll_arr+H<=DC-10)[0]
    fidx = np.where(np.logical_and(roll_arr+H<DC, roll_arr+H>DC-10))[0]
    sidx = np.where(np.logical_and(roll_arr+H>=DC,roll_arr+H<DC+10))[0]
    csidx = np.where(roll_arr+H>=DC+10)[0]
    dosidx[0,cfidx] = 1
    dosidx[1,fidx] = 1
    dosidx[2,sidx] = 1
    dosidx[3,csidx] = 1
    # I learned numpy roll for this! funny name (good name, too) for shift-wrapping an array in +/-n indices
    if(dosidx[0,0]==0):
      dosidx[:,0] = np.roll(dosidx[:,0],-1)
    if(dosidx[-1,-1]==0):
      dosidx[:,-1] = np.roll(dosidx[:,-1],1)

    # Now while we don't really need to know which ones are cf and f for calculating the damage in PF2e, it's still nice to have in general
    # damage_total = (a*num_cf + b* num_f + c*num_s + d*num_cs) / num_sides
    # a = 0, b = 0, c = damage_hit, d = 2*c
    # we don't need to know damage_total but the ratio damage_total / damage_hit is the general metric we want
    ratio_melee = ( np.count_nonzero(dosidx[2,:]) + 2*np.count_nonzero(dosidx[3,:]) ) / 20
    ratio_spell = ( 0.5*np.count_nonzero(dosidx[1,:]) + np.count_nonzero(dosidx[2,:]) + 2*np.count_nonzero(dosidx[3,:]) ) / 20
    ratio_mat[i,j] = ratio_melee
    ratio_mat2[i,j] = ratio_spell


plt.figure()
for i, DC in enumerate(dc_arr):
  plt.plot(hit_arr, ratio_mat[i,:], 'k:')
  plt.plot(hit_arr, ratio_mat[i,:], '^', label='DC:%d'%DC)

plt.xlabel('to Hit modifier')
plt.ylabel('ratio of damage')
plt.ylim(0,np.max(ratio_mat))
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
plt.close()

plt.figure()
for i, DC in enumerate(dc_arr):
  plt.plot(hit_arr, ratio_mat2[i,:], 'k:')
  plt.plot(hit_arr, ratio_mat2[i,:], '^', label='DC:%d'%DC)

plt.xlabel('to Hit modifier')
plt.ylabel('ratio of damage')
plt.ylim(0,np.max(ratio_mat))
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
plt.close()

pow_2_approx = ratio_mat[0,:] / ratio_mat[:,0]

plt.plot(hit_arr, pow_2_approx)
plt.xlim(hit_arr[0],hit_arr[-1])
plt.xlabel('to Hit modifier')
plt.ylabel('ratio of ratio that needs explained')
plt.grid(True)
plt.show()

plt.close()
