import random
import sys
import timeit

class Box:
	def __init__(self, length, width):
		self.length = length
		self.width = width
		self.area = length*width

class BinPacking:
	def __init__(self, storage_dimensions, boxes):
		# (length * width)
		self.l = storage_dimensions[0]
		self.w = storage_dimensions[1]
		self.storage = []
		for i in xrange(self.l):
			self.storage.append([])
			for j in xrange(self.w):
				self.storage[i].append(-1)
		
		# [Box1, Box2, Box3, ...]
		self.boxes = boxes

	# greedy approach - sort boxes from largest to smallest area
	# and pack the largest ones first
	def greedyAlgorithm(self):
		packed = 0
		areas = [(i, j) for i,j in enumerate(self.boxes)]
		areas = sorted(areas, key=lambda x:(-x[1].area))
		for label, box in areas:
			row, column = self.findEmptySpot(box.length, box.width)
			if (row, column) == (-1,-1):
				print "Cannot find empty spot for box", label
			else:
				for i in xrange(row, row+box.length):
					for j in xrange(column, column+box.width):
						self.storage[i][j] = label
				packed += 1
		print "Packed ", packed, "out of", len(self.boxes), "boxes"
		self.prettyPrintStorage()
	
	# returns first empty spot found for a specified length and width. 
	# if none is found, returns -1
	def findEmptySpot(self, length, width):
		for row in xrange(self.l):
			for column in xrange(self.w):
				if (self.storage[row][column] == -1 and 
					row+length < self.l and column+width < self.w):
					for i in xrange(row, row+length):
						for j in xrange(column, column+width):
							if (self.storage[i][j] != -1):
								continue
							else:
								if i == row+length-1 and j == column+width-1:
									return (row, column)
		return (-1, -1)

	# pretty prints the storage space. where the box is located in the storage
	# space is indicated by the label. -1 indicates an empty space
	def prettyPrintStorage(self):
		for i in xrange(self.l):
			for j in xrange(self.w):
				print self.storage[i][j],
			print


def main():
	storage_dimensions = (10,10)
	boxes = [Box(2,2), Box(1,3), Box(4,4), Box(2,2), Box(2,4), Box(2,5), Box(3,3), Box(3,5), Box(4,4)]
	start = BinPacking(storage_dimensions, boxes)
	start.greedyAlgorithm()

if __name__ == '__main__':
	main()