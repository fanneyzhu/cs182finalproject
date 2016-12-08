import random
import sys
import timeit
import copy

class Box:
	def __init__(self, label, length, width, weight_limit, weight):
		self.label = label
		self.length = length
		self.width = width
		self.area = length*width
		self.weight_limit = weight_limit
		self.weight = weight


class BinPacking:
	def __init__(self, storage_dimensions, boxes, storage):
		# length and width of storage space
		self.dim = storage_dimensions
		
		# for greedy algorithm
		self.storage_matrix = []
		for i in xrange(self.dim[0]):
			self.storage_matrix.append([])
			for j in xrange(self.dim[1]):
				self.storage_matrix[i].append(-1)
		self.unstored_greedy = []
		
		# storage dictionary with key as label and value as list of two tuples
		# 0: [(topleftx, toplefty), (bottomrightx, bottomrighty)]
		self.storage = storage
		
		# [Box1, Box2, Box3, ...]
		self.boxes = boxes

		# domain for each box
		self.domain = {}

		# empty space
		self.empty_space = self.dim[0]*self.dim[1]

	# greedy approach - sort boxes from largest to smallest area
	# and pack the largest ones first
	def greedyAlgorithm(self):
		packed = 0
		boxes = sorted(self.boxes, key=lambda x:(-x.area));
		for box in boxes:
			orientation, row, column = self.findEmptySpot(box)
			if orientation == -1:
				self.unstored_greedy.append(box.label)
			elif orientation == 0:
				for i in xrange(row, row+box.length):
					for j in xrange(column, column+box.width):
						self.storage_matrix[i][j] = box.label
				packed += 1
				self.empty_space -= box.length*box.width
			elif orientation == 1:
				for i in xrange(row, row+box.width):
					for j in xrange(column, column+box.length):
						self.storage_matrix[i][j] = box.label
				packed += 1
				self.empty_space -= box.length*box.width

		print "Packed", packed, "out of", len(boxes), "boxes"

	# returns overhead weight of box
	def get_overhead_weight(self, row, column, box, orientation):
		overhead_weight = 0
		for key, value in self.storage.iteritems():
			if box.label != key: # don't add itself to overhead weight
				if value[1][0] < row: # if the bottom right is above the row (y) of the new box 
					x_values = range(value[0][1], value[1][1]+1)
					if box.label in self.storage.keys():
						y = self.storage[box.label][1][1] - self.storage[box.label][1][0]
					elif orientation == 0:
						y = box.width
					elif orientation == 1:
						y = box.length
					overlap = sum([i in x_values for i in xrange(column, column+y+1)])
					frac = float(overlap)/len(x_values)
					overhead_weight += frac*self.boxes[key].weight

		return overhead_weight

	# Given a potential position, determine if the box can support the weight on top of it 
	# and if the boxes underneath it can support the added weight 
	# 0: [(topleftx, toplefty), (bottomrightx, bottomrighty), weight_limit, weight]
	# orientation 0 for length*width, 1 for width*length
	# returns False if no weight violations were found (good!)
	def check_weights(self, row, column, box, orientation):
		weight = self.get_overhead_weight(row, column, box, orientation)
		if weight > box.weight_limit:
			return True
		else:
			updated_weights = {}

			if orientation == 0:
				x = range(row, row+box.width)
				y = box.length
			elif orientation == 1:
				x = range(row, row+box.length)
				y = box.width

			for key, value in self.storage.iteritems(): 
				# add the new box to the weight_limits of the boxes underneath it
				if (value[0][0] > row+y-1): # if the top left corner y is under bottom right of the new box
					overlap = sum([i in x for i in xrange(value[0][1],value[1][1]+1)])
					frac = float(overlap)/len(x)
					updated_weights[key] = frac*box.weight

					if (updated_weights[key]+self.get_overhead_weight(
						value[0][0], value[0][1], self.boxes[key], orientation)
						> self.boxes[key].weight_limit):
						return True

			return False
	
	# returns first empty spot (top left corner of box) found for a specified 
	# length and width and orientation to place it in: 0 for length*width, 1 
	# for width*length. if none is found, returns -1
	def findEmptySpot(self, box):
		for row in xrange(self.dim[0]):
			for column in xrange(self.dim[1]):
				if self.storage_matrix[row][column] == -1:
					# check if there is space for length*width
					if row+box.length < self.dim[0] and column+box.width < self.dim[1]:
						# check weights first 
						if self.check_weights(row, column, box, 0) == True: 
							continue 
						for i in xrange(row, row+box.length):
							for j in xrange(column, column+box.width):
								if (self.storage_matrix[i][j] != -1):
									continue
								else:
									if i == row+box.length-1 and j == column+box.width-1:
										return (0, row, column)
					# check if there is space for width*length
					elif row+box.width < self.dim[0] and column+box.length < self.dim[1]:
						# check weights first 
						if self.check_weights(row, column, box, 1) == True: 
							continue 
						for i in xrange(row, row+box.width):
							for j in xrange(column, column+box.length):
								if (self.storage_matrix[i][j] != -1):
									continue
								else:
									if i == row+box.width-1 and j == column+box.length-1:
										return (1, row, column)

		return (-1,-1, -1)

	# creates a new version of the storage list with box assigned
	def setVariable(self, label, topleftx, toplefty, bottomrightx, bottomrighty):
		new_storage = copy.deepcopy(self.storage)
		new_storage[label] = [(topleftx, toplefty), (bottomrightx, bottomrighty)]
		return BinPacking(self.dim, self.boxes, new_storage)

	# returns most constrained variable to assign next
	def mostConstrainedVariable(self):
		self.getAllDomains()
		box = None
		min_domains = sys.maxint
		for i in self.getUnstoredBoxesCSP():
			domains = len(self.domain[i.label])
			if domains < min_domains:
				min_domains = domains
				box = i
		return box

	# returns true if assignment is complete
	def complete(self):
		if len(self.storage) == len(self.boxes):
			return True
		return False

	# returns a list of the available locations for a given box 
	# in the storage space
	def variableDomain(self, box):
		domain = set()
		if box:
			for row in xrange(self.dim[0]):
				for column in xrange(self.dim[1]):
					# check if there is space for length*width
					new_row = row+box.length-1
					new_col = column+box.width-1
					location = ((row,column),(new_row,new_col))
					if new_row < self.dim[0] and new_col < self.dim[1]:
						if len(self.storage) == 0:
							domain.add(location)
						else:
							overlap = False
							for key, value in self.storage.iteritems():
								result = self.box_overlap(row, column, new_row,
									new_col, value[0][0], value[0][1],
									value[1][0], value[1][1])
								if result == True:
									overlap = True
									break
							if overlap == False:
								if not self.check_weights(row, column, box, 0):
									domain.add(location)

					# check if there is space for width*length
					new_row = row+box.width-1
					new_col = column+box.length-1
					location = ((row,column),(new_row,new_col))
					if new_row < self.dim[0] and new_col < self.dim[1]:
						if len(self.storage) == 0:
							domain.add(location)
						else:
							overlap = False
							for key, value in self.storage.iteritems(): 
								result = self.box_overlap(row, column, new_row,
									new_col, value[0][0], value[0][1], 
									value[1][0], value[1][1])
								if result == True:
									overlap = True
									break
							if overlap == False:
								if not self.check_weights(row, column, box, 1):
									domain.add(location)
		return domain

	def getAllDomains(self):
		for box in self.getUnstoredBoxesCSP():
			self.domain[box.label] = self.variableDomain(box)

	# helper function that checks if two boxes are overlapping 
	def box_overlap(self, l1x, l1y, r1x, r1y, l2x, l2y, r2x, r2y):
		if (r1x < l2x):
			return False # a is left of b
		if (l1x > r2x): 
			return False # a is right of b
		if (r1y < l2y): 
			return False # a is above b
		if (l1y > r2y): 
			return False # a is below b
		return True # boxes overlap

	# returns next variable to try assigning
	def nextVariable(self):
		return self.mostConstrainedVariable()

	# returns new assignments with each possible value assigned to the variable
	# returned by 'nextVariable'
	def getSuccessors(self):
		box = self.nextVariable()
		successors = []
		for val in self.domain[box.label]:
			successors.append(self.setVariable(box.label, val[0][0], val[0][1],
				val[1][0], val[1][1]))
		return successors

	def getSuccessorsWithForwardChecking(self):
		return [s for s in self.getSuccessors() if s.forwardCheck()]

	# returns true if all boxes have non-empty domains.
	def forwardCheck(self):
		if self.complete():
			return True
		else:
			self.getAllDomains()
			for box in self.getUnstoredBoxesCSP():
				if len(self.domain[box.label]) == 0:
					return False
			return True

	def getEmptySpace(self):
		for value in self.storage.values():
			self.empty_space -= (value[1][0]-value[0][0]+1)*(value[1][1]-value[0][1]+1)
		return self.empty_space	

	def getUnstoredBoxesCSP(self):
		unstored = []
		for box in self.boxes:
			if box.label not in self.storage.keys():
				unstored.append(box)
		return unstored

	def getUnstoredBoxesGreedy(self):
		return self.unstored_greedy

	# pretty prints the storage space. where the box is located in the storage
	# space is indicated by its box number/label. -1 indicates an empty space
	def prettyPrintMatrix(self, matrix):
		for i in xrange(self.dim[0]):
			for j in xrange(self.dim[1]):
				print matrix[i][j],
			print

	def prettyPrintStorage(self):
		res = []
		for i in xrange(self.dim[0]):
			res.append([])
			for j in xrange(self.dim[1]):
				res[i].append(-1)
		for key, value in self.storage.iteritems():
			for x in xrange(value[0][0],value[1][0]+1):
				for y in xrange(value[0][1], value[1][1]+1):
					if res[x][y] != -1:
						print "error"
					else:
						res[x][y] = key
		self.prettyPrintMatrix(res)


def solveGreedy(problem):
	problem.greedyAlgorithm()
	print 'Could not store boxes:', problem.getUnstoredBoxesGreedy()
	print 'Empty space:', problem.getEmptySpace()
	problem.prettyPrintMatrix(problem.storage_matrix)

def solveCSP(problem, trials = 500):
	statesExplored = 0
	frontier = [problem]
	max_stored = 0
	max_state = None
	min_space = problem.dim[0]*problem.dim[1]
	min_state = None
	while len(frontier) > 0 and statesExplored < trials:
		if (statesExplored % 500 == 0):
			print statesExplored
		state = frontier.pop()
		statesExplored += 1
		if state.complete():
			print 'Number of explored: ' + str(statesExplored)
			print 'Empty Space:', state.getEmptySpace()
			state.prettyPrintStorage()
			return state
		else:
			stored = len(state.storage)
			if stored > max_stored:
				max_stored = stored
				max_state = state
			space = state.getEmptySpace()
			if space < min_space:
				min_space = space
				min_state = state
			successors = state.getSuccessorsWithForwardChecking()
			frontier.extend(successors)

	if max_state:
		print 'Packed', max_stored, 'out of', len(max_state.boxes), 'boxes'
		print 'Could not store boxes:', [box.label for box in max_state.getUnstoredBoxesCSP()]
		print 'Empty Space:', max_state.getEmptySpace()
		max_state.prettyPrintStorage()
		print
	
	if min_state:
		print 'Packed', len(min_state.storage), 'out of', len(min_state.boxes), 'boxes'
		print 'Could not store boxes:', [box.label for box in min_state.getUnstoredBoxesCSP()]
		print 'Empty Space:', min_space
		min_state.prettyPrintStorage()
		print

def main():
	storage_dimensions = (10,10)
	boxes = [Box(0,2,2,1,1), Box(1,1,3,100,1), Box(2,4,4,100,10), Box(3,2,2,20,1), Box(4,2,4,100,10), Box(5,2,5,100,1), Box(6,3,3,100,1), Box(7,3,5,100,1), Box(8,4,4,100,1)]
	storage = {}
	start = BinPacking(storage_dimensions, boxes, storage)
	print "greedy: "
	solveGreedy(start)
	print "CSP: "
	solveCSP(start)
	
	# s = (10,5)
	# boxes = [Box(0,5,4,100,10), Box(1,1,5,100,10), Box(2,5,4,100,10), Box(3,1,5,100,10)]
	# storage = {}
	# start = BinPacking(s, boxes, storage)
	# solveCSP(start)

if __name__ == '__main__':
	main()