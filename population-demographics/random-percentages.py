#!/usr/bin/python3

import numpy as np

#vast_majority = np.random.randint(0,2)
vast_majority = False
#vast_majority = True

npercent = np.random.randint(1,9)
#npercent = 4
ndecimals = 0
other_max = np.random.randint(8,16)
#percent = np.random.randint(1,101, npercent+1)
modes = np.random.randint(1,101, npercent+1)
percent = np.around(np.random.triangular(1, modes, 100, npercent+1))

if vast_majority:
  max_idx = np.argmax(percent)
  percent[max_idx] *= npercent+1

percent = percent / np.sum(percent)
percent = np.around(percent[np.argsort(percent)[::-1]]*100, ndecimals)
sum_diff = 100 - np.sum(percent)
percent[0] += sum_diff
if percent[-2] < other_max and np.random.randint(0,2) == 1:
  percent[-2], percent[-1] = percent[-1], percent[-2]
if percent[-1] >= other_max:
  adjust_diff = int(percent[-1] - other_max)
  buffer_array = np.zeros(npercent)
  for j in range(adjust_diff):
    k = j % npercent
    buffer_array[k] += 1
  percent[:-1] += buffer_array
  percent[-1] = other_max

#print("Vast majority %s" % bool(vast_majority))
print(percent)
