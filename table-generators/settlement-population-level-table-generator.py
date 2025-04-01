#!/usr/bin/python3

import numpy as np
import pandas as pd
import math

# define size of die to make table from
nd = 20
# define settlement types and their population ranges
settlement_types = ['Hamlet', 'Village', 'Town', 'City', 'Metropolis']
pop_ranges = [(2,25e0), (25e0,25e1), (25e1,25e2), (25e2,25e3), (25e3,25e4)]
level_ranges = [(0,0), (0,1), (2,4), (5,7), (8,20)]

# function to create logarithmic divisions for a d20 roll
def create_log_divisions(min_val, max_val, num_divisions=nd):
  # use log scale for population
  log_min = math.log(min_val)
  log_max = math.log(max_val)

  # create divisions in log space
  log_divisions = np.linspace(log_min, log_max, num_divisions + 1)

  # convert back to original scale and round to integers
  divisions = np.round(np.exp(log_divisions)).astype(int)

  # ensure the min and max values are exactly as specified
  divisions[0] = min_val
  divisions[-1] = max_val

  return divisions

def create_log_level_divisions(min_level, max_level, num_divisions=nd):
  if min_level == max_level:
    return [min_level] * (num_divisions+1)

  log_divisions = np.linspace(math.log(min_level+1), math.log(max_level+1), num_divisions)
  divisions = np.round(np.exp(log_divisions)).astype(int)-1

  divisions[0] = min_level
  divisions[-1] = max_level

  return divisions

# create tables for each settlement type
for i, settlement_type in enumerate(settlement_types):
  min_pop, max_pop = pop_ranges[i]
  min_level, max_level = level_ranges[i]

  pop_divisions = create_log_divisions(min_pop, max_pop)
  level_divisions = create_log_level_divisions(min_level, max_level)

  # create table data
  data = []
  for j in range(nd):
    roll = j+1
    min_pop_range = pop_divisions[j]
    max_pop_range = pop_divisions[j+1]-1
    if j == nd-1:
      max_pop_range = pop_divisions[j+1]

    level = level_divisions[j]

    data.append([roll, f'{min_pop_range}-{max_pop_range}', level])

  df = pd.DataFrame(data, columns=['d20 Roll', 'Population Range', 'Settlement Level'])

  print(f'## {settlement_type} Population Table')
  print(df.to_markdown(index=False))
  print('\
      ')

print('All tables generated successfully')
