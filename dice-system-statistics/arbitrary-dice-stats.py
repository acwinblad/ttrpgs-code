#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt


# success ranges should follow this format
#                    roll + mod < DC + first range
# DC + n range    <= roll + mod < DC + n+1 range
# DC + last range <= roll + mod
# this may mean adjusting the range values to account for "and equal" bounds
# PF2e example they have +/-10 on DC, you'd put [-9,0,10]

num_dice = 1
num_sides = 20
success_ranges = np.array([-9,0,10]) #PF2e success ranges
#success_ranges = np.array([-4,0,5]) #PF2e success ranges
success_multiplier = np.array([0,0.5,1.0,2])

#num_dice = 2
#num_sides = 6
#success_ranges = np.array([7,10]) #PBTA success ranges
#success_multiplier = np.array([0,0,1])
#
#num_dice = 2
#num_sides = 10
#success_ranges = np.array([12,17]) #Draw Steel success ranges
#success_multiplier = np.array([1,1.5,2])
#success_multiplier = np.array([1,0,0])

num_suc_ranges = np.size(success_ranges)+1


crits_flag = True
cf_nums = num_dice
cs_nums = num_dice*num_sides

hit_arr = np.arange(0,10)
dc_arr = np.arange(10,20)
#hit_arr = np.arange(-2,5)
#dc_arr = np.arange(0,1)

if(num_dice==1):
  roll_arr = np.arange(1,num_sides+1)
else:
  roll_arr = np.zeros((num_dice,num_sides))
  for i, val in enumerate(roll_arr):
    roll_arr[i,:] = np.arange(1,num_sides+1)
  tmp_arr = roll_arr[0,:]
  for i in range(num_dice-1):
    tmp_arr = np.add.outer(tmp_arr,roll_arr[i+1,:])
  roll_arr = np.sort(np.matrix.flatten(tmp_arr))

ratio_mat = np.zeros((np.size(dc_arr), np.size(hit_arr)))

# this double for-loop could probably be written using matrix manipulation
for i, DC in enumerate(dc_arr):
  for j, H in enumerate(hit_arr):
    # check if rolls + hit are in which degree of success
    dosidx = np.zeros((num_suc_ranges,np.size(roll_arr)), dtype = 'int')
    idx = np.where(roll_arr+H<DC+success_ranges[0])[0]
    dosidx[0,idx] = 1
    for k in range(num_suc_ranges-2):
      idx = np.where(np.logical_and( DC + success_ranges[k] <= roll_arr + H, roll_arr+H < DC + success_ranges[k+1]))[0]
      dosidx[k+1,idx] = 1
    idx = np.where(roll_arr+H>=DC+success_ranges[-1])[0]
    dosidx[-1,idx] = 1

    # I learned numpy roll for this! funny name (good name, too) for shift-wrapping an array in +/-n indices
    if(crits_flag):
      if(dosidx[0,0]==0):
        dosidx[:,0] = np.roll(dosidx[:,0],-1)
      if(dosidx[-1,-1]==0):
        dosidx[:,-1] = np.roll(dosidx[:,-1],1)

    # Now while we don't really need to know which ones are cf and f for calculating the damage in PF2e, it's still nice to have in general
    # damage_total = (a*num_cf + b* num_f + c*num_s + d*num_cs) / num_sides
    # a = 0, b = 0, c = damage_hit, d = 2*c
    # we don't need to know damage_total but the ratio damage_total / damage_hit is the general metric we want
    tmp = 0
    for k in range(num_suc_ranges):
      tmp += success_multiplier[k] * np.count_nonzero(dosidx[k,:])

    ratio_mat[i,j] = tmp / (num_sides** num_dice)

plt.figure()
for i, DC in enumerate(dc_arr):
  plt.plot(hit_arr, ratio_mat[i,:], 'k:')
  plt.plot(hit_arr, ratio_mat[i,:], '^', label='DC:%d'%DC)

plt.xlabel('modifier bonus')
plt.ylabel('ratio of degree of success')
plt.ylim(0,np.max(ratio_mat))
#plt.ylim(0,1)
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
plt.close()

pow_2_approx = ratio_mat[0,:] / ratio_mat[:,0]

plt.plot(hit_arr, pow_2_approx)
plt.xlim(hit_arr[0],hit_arr[-1])
plt.ylim(0,np.ceil(pow_2_approx[-1]))
plt.ylim(0,8)
plt.xlabel('to Hit modifier')
plt.ylabel('ratio of ratio that needs explained')
plt.grid(True)
plt.show()

plt.close()
