# The Path
# Yucheng Lin, Gerard Martinez, Marshall Sprigg
# Maze.py
# Maze class creates a random 2D maze, ensured to have an
# exit and reach each edge of the 2D array (list)

import sys
from random import randint

class Maze:
	# constructor
	def __init__(self, size=20):
		# data
		self.size = size		# size of 2D board
		self.retracing = False		# indicates whether or not in retrace state
		self.consecutiveRetraces = 0	# number of current consecutive retraces
		self.maxRetraces = 10		# number of retraces allowed before handofGod steps in		
		
		# maze lists for generation
		self.board = []			# will be 2D array representing maze
		self.possibleDir = []		# possible directions during generation
		self.previousMove = []		# stores last direction
		self.currentMove = []		# stores current direction
		self.currentPos = []		# coordinates of current position
		self.retraceCoord = []		# stores position coordinates for optimizing handofGod function
		
		# wall checking lists
		self.upVector = [1,0,0,0]	
		self.rightVector = [0,1,0,0]
		self.downVector = [0,0,1,0]
		self.leftVector = [0,0,0,1]
		self.zeroVector = [0,0,0,0]

		# character definitions in 2D maze
		self.wall = 'X'			# represents wall
		self.path = '.'			# represents path
		self.ubwall = '$'		# represents unbreakable wall
		return

	# print board
	def display(self):
		if len(self.board) == self.size:
			r = 0
			while r < self.size:
				c = 0
				while c < self.size:
					sys.stdout.write(self.board[r][c] + ' ')
					c += 1
				sys.stdout.write('\n')
				r += 1
		return

	# fills board with walls at every position
	def resetBoard(self):
		self.board = []
		r = 0
		while r < self.size:
			c = 0
			col = []
			while c < self.size:
				col.append(self.wall)
				c += 1
			self.board.append(col)
			r += 1
		return

	# updates possibleDir member data for potential moves
	def fillPossibleDir(self):
		# direction checks off end of list
		checkUp = 1
		checkRight = 1
		checkDown = 1
		checkLeft = 1

		# up
		if self.currentPos[0] == 0:
			checkUp = 0
			self.possibleDir[0] = 0

		# right
		if self.currentPos[1] == self.size-1:
			checkRight = 0
			self.possibleDir[1] = 0

		# down
		if self.currentPos[0] == self.size-1:
			checkDown = 0
			self.possibleDir[2] = 0

		# left
		if self.currentPos[1] == 0:
			checkLeft = 0
			self.possibleDir[3] = 0

		# check for non path locations around current position
		if checkUp == 1:
			self.lookUp(self.wall)
		if checkRight == 1:
			self.lookRight(self.wall)
		if checkDown == 1:
			self.lookDown(self.wall)
		if checkLeft == 1:
			self.lookLeft(self.wall)

		# ensure at least one possible direction
		i = 0
		
		while i < len(self.possibleDir):
			if self.possibleDir[i] == 1:
				self.retracing = False # reset retracing count
				return
			i += 1

		# if here must retrace
		# check to only retrace over path
		self.retracing = True
		self.consecutiveRetraces += 1

		if checkUp == 1:
                        self.lookUp(self.path)
                if checkRight == 1:
                        self.lookRight(self.path)
                if checkDown == 1:
                        self.lookDown(self.path)
                if checkLeft == 1:
                        self.lookLeft(self.path)
		return

	# selects a direction from possible moves and updates current move member data
	def chooseMove(self):
		move = int()
		while True:
			move = randint(0, len(self.possibleDir)-1)
			if self.possibleDir[move] == 1:
				self.currentMove = self.zeroVector
				self.currentMove[move] = 1
				break

		# update current position
		if self.consecutiveRetraces >= self.maxRetraces:
			self.handOfGod()
			return

		if move == 0:
			self.currentPos[0] -= 1 # move up
		elif move == 1:
			self.currentPos[1] += 1 # move right
		elif move == 2:
			self.currentPos[0] += 1 # move down
		elif move == 3:
			self.currentPos[1] -= 1 # move left
		else:
			print "Invalid move."
			sys.exit()	

		self.updateHelper()
		return

	# determines if an "unbreakable wall" needs to be placed and places them
	def wallCheck(self):
		# form ub walls if current % previous move vectors form an L shape
		if self.retracing:
			return

		if self.currentMove == self.rightVector and self.previousMove == self.upVector and self.board[self.currentPos[0]+1][self.currentPos[1]] != self.path:
			self.board[self.currentPos[0]+1][self.currentPos[1]] = self.ubwall
			return

		if self.currentMove == self.rightVector and self.previousMove == self.downVector and self.board[self.currentPos[0]-1][self.currentPos[1]] != self.path:
                        self.board[self.currentPos[0]-1][self.currentPos[1]] = self.ubwall
                        return

		if self.currentMove == self.leftVector and self.previousMove == self.upVector and self.board[self.currentPos[0]+1][self.currentPos[1]] != self.path:
                        self.board[self.currentPos[0]+1][self.currentPos[1]] = self.ubwall
                        return

		if self.currentMove == self.leftVector and self.previousMove == self.downVector and self.board[self.currentPos[0]-1][self.currentPos[1]] != self.path:
                        self.board[self.currentPos[0]-1][self.currentPos[1]] = self.ubwall
                        return

		if self.currentMove == self.upVector and self.previousMove == self.rightVector and self.board[self.currentPos[0]][self.currentPos[1]-1] != self.path:
                        self.board[self.currentPos[0]][self.currentPos[1]-1] = self.ubwall
                        return

		if self.currentMove == self.upVector and self.previousMove == self.leftVector and self.board[self.currentPos[0]][self.currentPos[1]+1] != self.path:
                        self.board[self.currentPos[0]][self.currentPos[1]+1] = self.ubwall
                        return

		if self.currentMove == self.downVector and self.previousMove == self.leftVector and self.board[self.currentPos[0]][self.currentPos[1]+1] != self.path:
                        self.board[self.currentPos[0]][self.currentPos[1]+1] = self.ubwall
                        return

		if self.currentMove == self.downVector and self.previousMove == self.rightVector and self.board[self.currentPos[0]][self.currentPos[1]-1] != self.path:
                        self.board[self.currentPos[0]][self.currentPos[1]-1] = self.ubwall
                        return
		return

	# checks if there is maze path along edges of Board
	def baseCheck(self):
		count = 0

		# check top row for path
		r = 0
		while r < self.size:
			if self.board[0][r] == self.path:
				count += 1
				break
			r += 1

		# check left most column for path
		r = 0
                while r < self.size:
                        if self.board[r][0] == self.path:
                                count += 1
                                break
			r += 1

		# check right most column for path
                r = 0
                while r < self.size:
                        if self.board[r][self.size-1] == self.path:
                                count += 1
                                break
			r += 1

		if count == 3:
			return True
		return False

	# looks for a char at a board location above current position
	def lookUp(self, c):
		if self.board[self.currentPos[0]-1][self.currentPos[1]] == c:
			self.possibleDir[0] = 1
		else:
			self.possibleDir[0] = 0
		return

	# looks for a char at a board location to the right of current position
	def lookRight(self, c):
		if self.board[self.currentPos[0]][self.currentPos[1]+1] == c:
                        self.possibleDir[1] = 1
                else:
                        self.possibleDir[1] = 0
		return

	# looks for a char at a board location below current position
	def lookDown(self, c):
		if self.board[self.currentPos[0]+1][self.currentPos[1]] == c:
                        self.possibleDir[2] = 1
                else:
                        self.possibleDir[2] = 0
		return

	# looks for a char at a board location to the left of current position
	def lookLeft(self, c):
		if self.board[self.currentPos[0]][self.currentPos[1]-1] == c:
                        self.possibleDir[3] = 1
                else:
                        self.possibleDir[3] = 0
		return

	# syncs the previous direction vector to the current direction vector
	def syncDirVectors(self):
		self.previousMove = self.currentMove
		return

	# updates current position in maze generator if stuck in a hellish circle of unbreakable walls
	def handOfGod(self):
		while True:
			r = self.retraceCoord[0]
			while r < self.size-2:
				c = self.retraceCoord[1]
				while c < self.size-2:
					# reset on last iteration
					if self.retraceCoord[1] == self.size-3:
						self.retraceCoord[1] = 0

					if self.board[r][c] == self.wall and self.board[r][c+1] == self.path:
						self.hogHelper(r,c)
						return
					elif self.board[r][c] == self.path and self.board[r][c+1] == self.wall:
						self.hogHelper(r,c)
						return
					elif self.board[r][c] == self.wall and self.board[r+1][c] == self.path:
						self.hogHelper(r,c)
						return
					elif self.board[r][c] == self.path and self.board[r+1][c] == self.wall:
						self.hogHelper(r,c)
						return
					c += 1

				if self.retraceCoord[0] == self.size-3:
					self.retraceCoord[0] = 0
				r += 1

			# reset coordinates for re-loop
			self.retraceCoord[0] = 0
			self.retraceCoord[1] = 0

	# condenses hand of God function with repeated pattern of function calls
	def hogHelper(self, r, c):
		# update current position
		self.currentPos[0] = r
		self.currentPos[1] = c

		# update retrace coordinates
		self.retraceCoord[0] = r
		self.retraceCoord[1] = c
		
		# reset retrace count, current move
		self.consecutiveRetraces = 0
		self.currentMove = self.zeroVector
		return

	# condenses choose move function with a series of necessary update commands that get repeated
	def updateHelper(self):
		# update board with new path
		self.board[self.currentPos[0]][self.currentPos[1]] = self.path

		# check for ub wall need
		self.wallCheck()

		# sync
		self.syncDirVectors()

	# GENERATE FUNCTION
	def generate(self, count=0):
		if count == 0:
			# reset data
			self.retracing = False
                	self.consecutiveRetraces = 0 
			self.resetBoard()

			# initializations
			self.possibleDir = self.zeroVector
			self.previousMove = self.zeroVector
			self.currentMove = self.zeroVector
			self.retraceCoord = [0,0]

			# start at middle bottom
			self.currentPos = [self.size-1, self.size/2-1]
			self.board[self.currentPos[0]][self.currentPos[1]] = self.path
		
		# recursive base case
		if self.baseCheck():
			return self.board

		# generate path
		self.fillPossibleDir()
		self.chooseMove()			

		# recurse
		self.generate(1)

# main function
if __name__ == '__main__':
	maze = Maze()
	maze.generate()
	maze.display()
