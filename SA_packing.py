# Simulated annealing for 2D packing 
# Daniel Wang, Fanney Zhu
# Harvard University, CS182
# 2016

import numpy as np
import matplotlib.pyplot as plt
import random
from random import randint
import math
import copy

# STEP 1: Specify dimensions of the storage space. 
dim  = (10,10)

# list of boxes that have been stored in the storage space 
storage = []

# initialize the storage matrix with -1s to represent an empty container 
initial_matrix = []
for i in xrange(dim[0]):
  initial_matrix.append([])
  for j in xrange(dim[1]):
    initial_matrix[i].append(-1)

# generate N boxes of random weights, weight limits, and dimensions 
def generateBoxes(num_boxes, max_length, max_width, max_weight, max_weight_limit):
  boxes = []
  for i in xrange(num_boxes):
    length = random.randint(1,max_length)
    width = random.randint(1,max_width)
    weight = random.randint(1,max_weight)
    weight_limit = random.randint(1,max_weight_limit)
    boxes.append((i, length, width, weight_limit, weight))
  return boxes

# STEP 2: Specify the max width/length values for the random boxes (item 1 and 2 for the function below)
boxes = generateBoxes(100,8,8,1,1)

#number of items
N = len(boxes)-1

# find the first empty spot within the container for a given box. returns -1, -1, -1 if none found 
def findEmptySpot(length, width, storage_matrix):
  for row in xrange(dim[0]):
    for column in xrange(dim[1]):
      if storage_matrix[row][column] == -1:
        # check if there is space for length*width
        if row+length-1 < dim[0] and column+width-1 < dim[1]:
          valid = True
          for i in xrange(row, row+length):
            for j in xrange(column, column+width):
              if (storage_matrix[i][j] != -1):
                valid = False
              if valid and i == row+length-1 and j == column+width-1:
                return (0, row, column)
        # check if there is space for width*length
        if row+width-1 < dim[0] and column+length-1 < dim[1]:
          valid = True
          for i in xrange(row, row+width):
            for j in xrange(column, column+length):
              if (storage_matrix[i][j] != -1):
                valid = False
              if valid and i == row+width-1 and j == column+length-1:
                return (1, row, column)

  return (-1,-1, -1)

# determines if we should accept the new solution (matrix) 
def accept(old_cost, new_cost, temperature):
  return math.e ** ((new_cost - old_cost) / temperature)

# generate a new bag that is a random "neighbor" of the current bag 
# first add a random new item and the remove a random one if the weight is over W 
def random_neighbor(storage_matrix):
  # make sure we dont have duplicates
  assert(len(storage)==len(set(storage)))
  assert(len(boxes)==len(set(boxes)))
  
  # make a copy of the old solution 
  updated_matrix = copy.deepcopy(storage_matrix)
  if len(storage) > 0: 
    # choose a random box to remove from the current storage list 
    rand_remove = randint(0,len(storage)-1)

    #get the actual of the id of the box to remove
    remove_member = storage[rand_remove][0] 
    
    # remove the box from the storage area replacing with -1s 
    for row in xrange(dim[0]):
      for column in xrange(dim[1]):
        if updated_matrix[row][column] == remove_member: 
          updated_matrix[row][column] = -1


    # remove the box from the list of stored boxes and add it back to the list of boxes 
    remove_box = storage[rand_remove]
    assert(remove_box not in boxes)
    boxes.append(remove_box)
    assert(remove_box in boxes)
    assert(remove_box in storage)
    storage.remove(remove_box)
    assert (remove_box not in storage)
    
  # try to fit in as many new boxes as possible   
  for new_member in boxes: 

    # double check that the box isn't already in the storage space 
    box_num = new_member[0]
    box_exists = False 
    for row in xrange(dim[0]):
      for column in xrange(dim[1]):
        if updated_matrix[row][column] == box_num: 
          box_exists = True
    if box_exists == False: 
   
      # this is where we need to check if the box can fit in with the proper constraints 
      orientation, row, column = findEmptySpot(new_member[1],new_member[2],updated_matrix)
      box_num = new_member[0]
      length = new_member[1]
      width = new_member[2]
 
      # for orientation 0 or 1, add the new box to the storage list, remove it from the 
      # list of unstored boxes, and then put the box in updated_matrix 
      if orientation == 0:
        assert(new_member not in storage)
        storage.append(new_member)
        assert(new_member in storage)
        assert(new_member in boxes)
        boxes.remove(new_member)
        assert(new_member not in boxes)
        for i in xrange(row, row+length):
          for j in xrange(column, column+width):
            updated_matrix[i][j] = box_num

      elif orientation == 1:
        assert(new_member not in storage)
        storage.append(new_member)
        assert(new_member in storage)
        assert(new_member in boxes)
        boxes.remove(new_member)
        assert(new_member not in boxes)
        for i in xrange(row, row+width):
          for j in xrange(column, column+length):
            updated_matrix[i][j] = box_num

  # return the new matrix with updated boxes 
  return updated_matrix
  


# the amount of unused space in the matrix; high score is good since we use (area - unused space) as the scoring metric 
def score(matrix):
  # initially the size of the matrix 
  score = dim[0]*dim[1] 
  for row in xrange(dim[0]):
    for column in xrange(dim[1]):
      if matrix[row][column] == -1:
        score -=1 
  return score


def simulated_annealing(initial_solution, alpha, random_neighbor, fitness, threshold=accept):
  # YOUR CODE HERE
  # return a trace of values resulting from your simulated annealing
  temperature = 1.0
  min_temperature = 0.00001
  current_solution = initial_solution
  current_solution_cost = score(current_solution)
  solution_list = [] 

  
  while temperature > min_temperature:
      for i in range(100):
          
          new_solution = random_neighbor(current_solution)
          new_solution_cost = score(new_solution)
          # always accept the new solution if it is better than the old one 
          if (new_solution_cost - current_solution_cost) > 0: 
            current_solution = new_solution
            current_solution_cost = new_solution_cost
          # if new solution is worse, accept if threshold probability is greater than random value  
          else: 
            prob = threshold(current_solution_cost, new_solution_cost, temperature)
            if prob > random.random():
                current_solution = new_solution
                current_solution_cost = new_solution_cost
          solution_list.append(score(current_solution))
      # update temperature             
      temperature *= alpha
  # return the solution matrix, packing density, and the list of boxes in the solution matrix
  return current_solution, current_solution_cost, solution_list

if __name__ == "__main__":
    # list of the number of unfilled spaces per simulation trial 
    unstored = [] 
    # number of simulation trials 
    sims = 10
    # run simulations and collect data 
    for i in xrange(sims):
      SA_trace = simulated_annealing(initial_matrix,0.9,random_neighbor,score,accept)
      unstored.append(SA_trace[1])
    unstored_mean = math.ceil((sum(unstored))/sims)
    print unstored_mean
    print unstored

    #plt.plot(SA_trace[2], label="SA")
    #plt.legend(bbox_to_anchor=(40, 1.02, 1., .102), loc=3,
          #ncol=2, mode="expand", borderaxespad=0.)
    #plt.show()
    