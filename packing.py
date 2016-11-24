import random
import sys
import timeit

class Box:
	def __init__(self, label, length, width):
		self.label = label
		self.length = length
		self.width = width
		self.area = length*width


class BinPacking:
	def __init__(self, storage_dimensions, boxes):
		# length and width of storage space
		self.l = storage_dimensions[0]
		self.w = storage_dimensions[1]
		
		self.storage_matrix = []
		for i in xrange(self.l):
			self.storage_matrix.append([])
			for j in xrange(self.w):
				self.storage_matrix[i].append(-1)
		
		# [[(0,topleftx0,toplefty0),(0,bottomrightx0, bottomrighty0)],
		#  [(1,topleftx1,toplefty1),(1,bottomrightx1, bottomrighty1)], ...]
		self.storage_list = []
		for i in xrange(self.l):
			self.storage_list.append([])
		
		# [Box1, Box2, Box3, ...]
		self.boxes = boxes

		# domain for box
		self.domain = {}

	# greedy approach - sort boxes from largest to smallest area
	# and pack the largest ones first
	def greedyAlgorithm(self):
		packed = 0
		boxes = sorted(self.boxes, key=lambda x:(-x.area));
		for box in boxes:
			orientation, row, column = self.findEmptySpot(box.length, box.width)
			if orientation == -1:
				print "Cannot find empty spot for box", box.label
			elif orientation == 0:
				for i in xrange(row, row+box.length):
					for j in xrange(column, column+box.width):
						self.storage_matrix[i][j] = box.label
				packed += 1
			elif orientation == 1:
				for i in xrange(row, row+box.width):
					for j in xrange(column, column+box.length):
						self.storage_matrix[i][j] = box.label
				packed += 1

		print "Packed ", packed, "out of", len(boxes), "boxes"
		self.prettyPrintStorage()
	
	# returns first empty spot (top left corner of box) found for a specified 
	# length and width and orientation to place it in: 0 for length*width, 1 
	# for width*length. if none is found, returns -1
	def findEmptySpot(self, length, width):
		for row in xrange(self.l):
			for column in xrange(self.w):
				if self.storage_matrix[row][column] == -1:
					# check if there is space for length*width
					if row+length < self.l and column+width < self.w:
						for i in xrange(row, row+length):
							for j in xrange(column, column+width):
								if (self.storage_matrix[i][j] != -1):
									continue
								else:
									if i == row+length-1 and j == column+width-1:
										return (0, row, column)
					# check if there is space for width*length
					elif row+width < self.l and column+length < self.w:
						for i in xrange(row, row+width):
							for j in xrange(column, column+length):
								if (self.storage_matrix[i][j] != -1):
									continue
								else:
									if i == row+width-1 and j == column+length-1:
										return (1, row, column)

		return (-1,-1, -1)

	# creates a new version of the storage list with box assigned
	def setVariable(self, label, topleftx, toplefty, bottomrightx, bottomrighty):
		box = [(label, topleftx, toplefty), (label, bottomrightx, bottomrighty)]
		newStorageList = deepcopy(self.storage_list)
		num_stored = len(newStorageList)
		for i in xrange(num_stored):
			if label == newStorageList[i][0][0]:
				newStorageList[i] = box
			elif label != newStorageList[i][0][0] and i == num_stored-1:
				newStorageList.append(box)
				break
		return newStorageList

	# returns true if assignment is complete
	def complete(self):
		if len(self.storage_list) == len(self.boxes):
			return True
		return False

	# returns a list of the available locations for a given box 
	# in the storage space
	def getDomain(self, input_box):
		domain = [] 
		num_stored = len(self.storage_list)
		for row in xrange(self.l): 
			for column in xrange(self.w):
				# check if there is space for length*width
				if row+input_box.width < self.l and column+input_box.width < self.w:
					for i in xrange(num_stored): 
						result = box_overlap(row, column, row+input_box.width, 
							column+input_box.length, self.storage_list[i][0][1], 
							self.storage_list[i][0][2], self.storage_list[i][1][1],
							self.storage_list[i][1][2])
						if result == True:
							continue
						elif result == False and i == num_stored-1:
							domain.append([(row,column),(row+width,column+length)])
				# check if there is space for width*length
				elif row+input_box.length < self.l and column+input_box.width < self.w:
					for i in xrange(num_stored): 
						result = box_overlap(row, column, row+input_box.length, 
							column+input_box.width, self.storage_list[i][0][1], 
							self.storage_list[i][0][2], self.storage_list[i][1][1],
							self.storage_list[i][1][2])
						if result == True:
							continue
						elif result == False and i == num_stored-1:
							domain.append([(row,column),(row+width,column+length)])

		return domain

	def getAllDomains(self):
		for box in self.boxes:
			self.domain[box.label] = self.getDomain(box)

	# helper function that checks if two boxes are overlapping 
	def box_overlap(l1x, l1y, r1x, r1y, l2x, l2y, r2x, r2y):
		# check if one rectangle is on left side of other
		if l1x > r2x or l2x > r1x: 
			return False
		# check if one rectangle is above other
		if l1y < r2y or l2y < r1y:
			return False
		return True

	# returns next variable to try assigning
	def nextVariable(self):
		pass

	# returns new assignments with each possible value assigned to the variable
	# returned by 'nextVariable'
	def getSuccessors(self):
		box = self.nextVariable()
		domain = self.getDomain(box)
		successors = []
		for val in domain:
			successors.append(self.setVariable(box.label, val[0][0], val[0][1],
				val[1][0], val[1][1]))
		return successors

	def getSuccessorsWithForwardChecking(self):
		return [s for s in self.getSuccessors() if s.forwardCheck()]

	# returns true if all boxes have non-empty domains.
	def forwardCheck(self):
		# for key, value in self.domain.iter
		pass

	# pretty prints the storage space. where the box is located in the storage
	# space is indicated by its box number/label. -1 indicates an empty space
	def prettyPrintStorage(self):
		for i in xrange(self.l):
			for j in xrange(self.w):
				print self.storage_matrix[i][j],
			print


def main():
	storage_dimensions = (10,10)
	boxes = [Box(0,2,2), Box(1,1,3), Box(2,4,4), Box(3,2,2), Box(4,2,4), Box(5,2,5), Box(6,3,3), Box(7,3,5), Box(8,4,4)]
	start = BinPacking(storage_dimensions, boxes)
	start.greedyAlgorithm()

if __name__ == '__main__':
	main()