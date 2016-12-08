import numpy as np
import matplotlib.pyplot as plt
import random
from random import randint
import math
import copy



# dimensions of the storage space. Global
dim  = (10,10)

# empty space
empty_space = dim[0]*dim[1]

storage = []

# for greedy algorithm
initial_matrix = []
for i in xrange(dim[0]):
  initial_matrix.append([])
  for j in xrange(dim[1]):
    initial_matrix[i].append(-1)

boxes = [(0,2,2,100,1), (1,1,3,100,1), (2,4,4,100,1), (3,2,2,100,1), (4,2,4,100,1),(5,2,5,100,1),(6,3,3,100,1),(7,3,5,100,1),(8,4,4,100,1),(9,1,1,100,1),(10,1,1,100,1),(11,1,1,100,1),(12,1,1,100,1)]
#number of items
N = len(boxes)-1

def findEmptySpot(length, width, storage_matrix):
  for row in xrange(dim[0]):
    for column in xrange(dim[1]):
      if storage_matrix[row][column] == -1:
        # check if there is space for length*width
        if row+length < dim[0] and column+width < dim[1]:
          for i in xrange(row, row+length):
            for j in xrange(column, column+width):
              if (storage_matrix[i][j] != -1):
                continue
              else:
                if i == row+length-1 and j == column+width-1:
                  return (0, row, column)
        # check if there is space for width*length
        elif row+width < dim[0] and column+length < dim[1]:
          for i in xrange(row, row+width):
            for j in xrange(column, column+length):
              if (storage_matrix[i][j] != -1):
                continue
              else:
                if i == row+width-1 and j == column+length-1:
                  return (1, row, column)

  return (-1,-1, -1)

# determines if we should accept the new bag 
def accept(old_cost, new_cost, temperature):
  return math.e ** ((new_cost - old_cost) / temperature)

# generate a new bag that is a random "neighbor" of the current bag 
# first add a random new item and the remove a random one if the weight is over W 
def random_neighbor(storage_matrix):

  updated_matrix = copy.deepcopy(storage_matrix)
  if len(storage) > 1: 
    # choose a random box to remove from the current storage list 
    rand_remove = randint(0,len(storage)-1)
    remove_member = storage[rand_remove][0] #get the actual of the id of the box to remove

    # remove the box from the storage area 
    for row in xrange(dim[0]):
      for column in xrange(dim[1]):
        if updated_matrix[row][column] == remove_member: 
          updated_matrix[row][column] = -1

    # remove the box from the list of stored boxes and add it back to the list of boxes 
    boxes.append(storage[rand_remove])
    storage.remove(storage[rand_remove])



  for new_member in boxes: 
  
    # make sure that the item isn't already in our bag 
    #while new_member in storage:
    #  new_member = randint(0,N-1)

    # this is where we need to check if the box can fit in with the proper constraints 
    # updated_solution.append(new_member) --> from the original problem set SA 

    orientation, row, column = findEmptySpot(new_member[1],new_member[2],updated_matrix)
    box_num = new_member[0]
    length = new_member[1]
    width = new_member[2]
    #if orientation == -1:
    #  self.unstored_greedy.append(box.label)
    if orientation == 0:
      storage.append(new_member)
      boxes.remove(new_member)
      for i in xrange(row, row+length):
        for j in xrange(column, column+width):
          updated_matrix[i][j] = box_num

    elif orientation == 1:
      storage.append(new_member)
      boxes.remove(new_member)
      for i in xrange(row, row+width):
        for j in xrange(column, column+length):
          updated_matrix[i][j] = box_num
        


  return updated_matrix

# the amount of unused space in the matrix; high score is good since we use (area - unused space) as the scoring metric 
def score(matrix):
  score = dim[0]*dim[1] # initially the size of the matrix 
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

  
  while temperature > min_temperature:
      print "random neighbor"
      for i in range(5):
          
          new_solution = random_neighbor(current_solution)
          new_solution_cost = score(new_solution)
          if (new_solution_cost - current_solution_cost) > 0: 
            print current_solution_cost
            current_solution = new_solution
            current_solution_cost = new_solution_cost
          else: 
            prob = threshold(current_solution_cost, new_solution_cost, temperature)
            if prob > random.random():
                current_solution = new_solution
                current_solution_cost = new_solution_cost
                print new_solution_cost
          #solutions_list.append(score(current_solution))
                  
      temperature *= alpha
  # get the total weight of the current solution    

  # current solution is the contents of the bag, cost is the value, weight is the bag weight, and solutions list is all of hte 
  # bags that we explored through simulated annealing 
  return current_solution, current_solution_cost
  #, solutions_list



if __name__ == "__main__":
    
    
    #start = BinPacking(storage_dimensions, boxes, storage)
    

    SA_trace = simulated_annealing(initial_matrix,0.9,random_neighbor,score,accept)


    print("SA Algorithm:\nValue:{}, Occupied:{}".format(SA_trace[0], SA_trace[1]))
    #plt.plot([greedy_val]*len(SA_trace[3]), label="Greedy")
    #plt.plot(SA_trace[3], label="SA")
    #plt.legend(bbox_to_anchor=(40, 1.02, 1., .102), loc=3,
           #ncol=2, mode="expand", borderaxespad=0.)
    #plt.show()
    