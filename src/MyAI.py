# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
# AI IMPLEMENTED BY: 	Raffay Rashed
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
import random
from Action import Action

front = []
superFront = []
frontAdj = set([])

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self._rowDimension = colDimension
		self._colDimension = rowDimension
		self._totalMines = totalMines
		self._startLoc = (startX, startY)
		self._totLocs = []
		self._remLocs = []
		self._moveCount = 0
		self._prevLoc = (startX, startY)
		self._toExploreSafe = []
		self._moveCount = 0
		self._board = []
		self._nicetoexactlocations = {}
		self._moveCount = 0
		self._mineAdjLocs = []
		self._locNumDict = {}
		self._mineLocs = []
		self._debug = False
		for i in range(colDimension):
			for j in range(rowDimension):
				to_append = (i, j)
				self._totLocs.append(to_append)
				self._remLocs.append(to_append)
		
		#print(self._totLocs)
		self.generateBoard()
		#self.displayBoard()


	def getAction(self, number: int) -> "Action Object":

		#if self._moveCount > 140:
			#return Action(AI.Action.LEAVE)

		# Update Board then print iteration information (DEBUGGING PURPOSES)
		if self._debug:
			self.debugGetAction(number)


		# Remove peviously uncovered location from frontier and remaining locations lists
		self.removePrevLoc()


		# If previously selected location has no adjacent mines add its adjacent locations to toExploreSafe
		if number == 0:
			adj = self.getAdjacentRem(self._prevLoc)
			self._toExploreSafe.extend(adj)


		# If peviously selected location has adjacent mines add its location to  mineAdjLocs and adjust its number by checking if its next to any already found mines
		if number > 0 and self._prevLoc not in self._mineAdjLocs and self._prevLoc not in self._locNumDict.keys():
			self._mineAdjLocs.append(self._prevLoc)
			self._locNumDict[self._prevLoc] = number
			if len(self._mineLocs) > 0:
				if self._debug:
					self.nextToFoundMineDEBUG()
				else:
					self.nextToFoundMine()


		# Check for possible mines and add any new safe locations to toExploreSafe and update info of mineadjacent locations if toExploreSafe is empty
		if len(self._toExploreSafe) < 1 and len(self._mineAdjLocs) > 0:
			if self._debug:
				self.checkForMinesDEBUG()
			else:
				self.checkForMines()


		# Check to see if game is finished or not if finished then leave game
		if len(self._mineLocs) == self._totalMines and len(self._remLocs) == 0:
			return Action(AI.Action.LEAVE)


		# If last location is mine
		if (self._totalMines - len(self._mineLocs)) == len(self._remLocs):
			if self._debug:
				print("LAST LOC IS MINE")
			return Action(AI.Action.LEAVE)


		# If all mines are found just uncover remaining locations
		if len(self._mineLocs) == self._totalMines and len(self._remLocs) > 0:
			if self._debug:
				print("ALL MINES FOUND UNCOVERING REMAINING LOCS")
			x = self._remLocs[0]
			self._prevLoc = x
			return Action(AI.Action.UNCOVER, x[0], x[1])


		# World Checker Algorithm
		if len(self._toExploreSafe) < 1 and len(self._mineAdjLocs) > 0:
			if self._debug: 
				wcMines, wcSafeLocs = self.worldCheckingDEBUG()
			else:
				wcMines, wcSafeLocs = self.worldChecking()
			if len(wcMines) > 0:
				for mine in wcMines:
					if not mine in self._mineLocs:
						self._mineLocs.append(mine)
					if mine in self._remLocs:
						self._remLocs.remove(mine)
					for uAdjLoc in self.getMineAdjacentUnmarked(mine):
						self._locNumDict[uAdjLoc] -= 1
						if self._locNumDict[uAdjLoc] == 0:
							self._mineAdjLocs.remove(uAdjLoc)
							for i in self.getAdjacentRem(uAdjLoc):
								if i not in self._toExploreSafe:
									self._toExploreSafe.append(i)

			if len(wcSafeLocs) > 0:
				for i in wcSafeLocs:
					if i not in self._toExploreSafe:
						self._toExploreSafe.append(i)
		

		# If there are safe locations uncover them first
		if len(self._toExploreSafe) > 0:
			element = self._toExploreSafe[0]
			x = element[0]
			y = element[1]
			self._prevLoc = ((x, y))
			self._moveCount += 1
			if self._debug:
				print("EXPLORING LOC:", self._prevLoc)
			return Action(AI.Action.UNCOVER, x, y)

		# If there are no more safe locations do this:
		else:
			if self._debug:
				print("LAST RESORT")
				#print("REMAINING LOCS:", self._remLocs)
				#print("MINEADJDICT:", self._locNumDict)
			self._moveCount += 1
			xy = random.choice(self._remLocs)
			if self._debug:
				print("REMAINING LOCS:", self._remLocs, "RANDOM CHOICE:", xy)
			self._prevLoc = ((xy[0], xy[1]))
			return Action(AI.Action.UNCOVER, xy[0], xy[1])


	def isAdjacent(self, locA, locB):
		LocBAdjacent = [(locB[0]-1, locB[1]+1), (locB[0], locB[1]+1), (locB[0]+1, locB[1]+1), (locB[0]+1, locB[1]), (locB[0]+1, locB[1]-1), (locB[0], locB[1]-1), (locB[0]-1, locB[1]-1), (locB[0]-1, locB[1])]
		if locA in LocBAdjacent:
			return True
		else:
			return False


	def getAdjacentRem(self, xy) -> "Adjecent Locations":
		toRet = [(xy[0]-1, xy[1]+1), (xy[0], xy[1]+1), (xy[0]+1, xy[1]+1), (xy[0]+1, xy[1]), (xy[0]+1, xy[1]-1), (xy[0], xy[1]-1), (xy[0]-1, xy[1]-1), (xy[0]-1, xy[1])]
		x = []
		for i in toRet:
			if i in self._remLocs and i not in self._toExploreSafe:
				x.append(i)
		return x
	

	def getMineAdjacentUnmarked(self, xy) -> "Unmarked Mine Adjecent Locations":
		toRet = [(xy[0]-1, xy[1]+1), (xy[0], xy[1]+1), (xy[0]+1, xy[1]+1), (xy[0]+1, xy[1]), (xy[0]+1, xy[1]-1), (xy[0], xy[1]-1), (xy[0]-1, xy[1]-1), (xy[0]-1, xy[1])]
		x = []
		for i in toRet:
			if i in self._mineAdjLocs:
				x.append(i)
		return x


	def generateBoard(self):
		for i in range(self._colDimension + 1):
			if i == self._colDimension:
				self._board.append([])
				for j in range((self._rowDimension*2)+1):
					if j == 0:
						self._board[i].append(["  ", "  "])
					elif j % 2 != 0:
						self._board[i].append([" ", " "])
					else:
						self._board[i].append([j//2-1, j//2-1])
			else:
				self._board.append([])
				for k in range((self._rowDimension*2)+1):
					if k == 0:
						self._board[i].append([self._colDimension-i-1, self._colDimension-i-1])
					elif k == 1 and (self._colDimension-i-1) < 10:
						self._board[i].append(["  ", "  "])
					elif k > 1 and k % 2 != 0 and k > 18+1:
						self._board[i].append(["  ", "  "])
					elif k % 2 != 0:
						self._board[i].append([" ", " "])
					else:
						self._board[i].append(["-", "-"])
						self._nicetoexactlocations[(k//2-1, self._colDimension-i-1)] = (i, k)


	def displayBoard(self):
		for i in self._board:
			for j in i:
				print(j[0], end='')
			print('')
		#print('')

	
	def updateBoard(self, num):
		brd_loc = self._nicetoexactlocations[self._prevLoc]
		self._board[brd_loc[0]][brd_loc[1]][0] = str(num)
		for i in self._locNumDict:
			brd_loc = self._nicetoexactlocations[i]
			self._board[brd_loc[0]][brd_loc[1]][0] = self._locNumDict[i]
		for i in self._mineLocs:
			brd_loc = self._nicetoexactlocations[i]
			self._board[brd_loc[0]][brd_loc[1]][0] = 'M'
	

	def removePrevLoc(self):
		if self._prevLoc in self._remLocs:
			self._remLocs.remove(self._prevLoc)
		if self._prevLoc in self._toExploreSafe:
			self._toExploreSafe.remove(self._prevLoc)

	
	def debugGetAction(self, number):
		self.updateBoard(number)
		print("\n____________________________________________________________________________________________")
		print("ITERATION INFO:")
		print("SAFE_LOCATIONS:", self._toExploreSafe)
		print("MOVE NUM:", self._moveCount, "\tLOC:", self._prevLoc, "NUM:", number, "\t adjacent to:", self.getAdjacentRem(self._prevLoc))
		self.displayBoard()
		print("____________________________________________________________________________________________\n")


	def checkForMinesDEBUG(self):
		print("\n__________________________________STARTING RULESE OF THUMB__________________________________")

		# print("NUMLOCDICT", self._locNumDict)
		# print("lst:", self._mineAdjLocs)
		# print("Remlocs", self._remLocs)

		print("MineAdjLocs List:", self._mineAdjLocs, "\n")
		for loc in self._mineAdjLocs:
			mines = self.getAdjacentRem(loc)
			#print("\nCURRENT LOC:", loc, "  Possible Mine Locs:", mines, "  Num of mines adjacent to Loc:", self._locNumDict[loc])
			if len(mines) == self._locNumDict[loc]:
				print("CUR LOC:", loc, "FOUND MINE LOCS:", mines)
				self._locNumDict[loc] = 0
				self._mineAdjLocs.remove(loc)
				for i in mines:
					if i not in self._mineLocs:
						self._mineLocs.append(i)
				for mine in mines:
					print("UPDATING UADJ LOCS:",self.getMineAdjacentUnmarked(mine), "  OF FOUND MINE:", mine)
					self._remLocs.remove(mine)
					for uAdjLoc in self.getMineAdjacentUnmarked(mine):
						self._locNumDict[uAdjLoc] -= 1
						print("CUR UADJ LOC:", uAdjLoc, "UPDATED NUM:", self._locNumDict[uAdjLoc])
						if self._locNumDict[uAdjLoc] == 0:
							self._mineAdjLocs.remove(uAdjLoc)
							self._toExploreSafe.extend(self.getAdjacentRem(uAdjLoc))
				print('')
		print("\nRESULT:\nSAFE SPACES:", self._toExploreSafe)
		print("\n___________________________________ENDING RULESE OF THUMB___________________________________\n")


	def checkForMines(self):
		for loc in self._mineAdjLocs:
			mines = self.getAdjacentRem(loc)
			if len(mines) == self._locNumDict[loc]:
				self._locNumDict[loc] = 0
				self._mineAdjLocs.remove(loc)
				for i in mines:
					if i not in self._mineLocs:
						self._mineLocs.append(i)
				for mine in mines:
					self._remLocs.remove(mine)
					for uAdjLoc in self.getMineAdjacentUnmarked(mine):
						self._locNumDict[uAdjLoc] -= 1
						if self._locNumDict[uAdjLoc] == 0:
							self._mineAdjLocs.remove(uAdjLoc)
							self._toExploreSafe.extend(self.getAdjacentRem(uAdjLoc))


	def nextToFoundMineDEBUG(self):
		print("\n__________________________________ADJUSTING PREV LOC NUMBER_________________________________")
		print("CEHCKING IF PREV LOC:", self._prevLoc, "  IS NEXT TO FOUND MINES:", self._mineLocs)
		for mine in self._mineLocs:
			for mineAdjLoc in self.getMineAdjacentUnmarked(mine):
				if mineAdjLoc == self._prevLoc:
					self._locNumDict[self._prevLoc] -= 1
					print("PREV", self._prevLoc, " IS ADJACENT TO MINE:", mine, "NUM OF PREV NOW:", self._locNumDict[self._prevLoc])
					if self._locNumDict[self._prevLoc] == 0:
						self._mineAdjLocs.remove(self._prevLoc)
						for i in self.getAdjacentRem(mineAdjLoc):
							if i not in self._toExploreSafe:
								self._toExploreSafe.append(i)
		print("THIS IS NEW SAFE SPACES:", self._toExploreSafe, "\n")
		print("____________________________________________________________________________________________\n")


	def nextToFoundMine(self):
		for mine in self._mineLocs:
			for mineAdjLoc in self.getMineAdjacentUnmarked(mine):
				if mineAdjLoc == self._prevLoc:
					self._locNumDict[self._prevLoc] -= 1
					if self._locNumDict[self._prevLoc] == 0:
						self._mineAdjLocs.remove(self._prevLoc)
						for i in self.getAdjacentRem(mineAdjLoc):
							if i not in self._toExploreSafe:
								self._toExploreSafe.append(i)


	def getUMAL(self, xy, front) -> "Unmarked Mine Adjecent Locations":
		toRet = [(xy[0]-1, xy[1]+1), (xy[0], xy[1]+1), (xy[0]+1, xy[1]+1), (xy[0]+1, xy[1]), (xy[0]+1, xy[1]-1), (xy[0], xy[1]-1), (xy[0]-1, xy[1]-1), (xy[0]-1, xy[1])]
		x = []
		for i in toRet:
			if i in self._mineAdjLocs and not i in front:
				x.append(i)
		return x


	def recurAdj(self, start):
		global frontAdj
		global front
		global superFront
		#print("RECUR", start, getMineAdjacentUnmarked(start, front))
		x = self.getUMAL(start, superFront)
		if len(x) == 0:
			if start not in front:
				front.append(start)
				superFront.append(start)
				frontAdj.union(set(self.getAdjacentRem(start)))
			return
		else:
			for i in x:
				umal = set(self.getAdjacentRem(i))
				test =  frontAdj.copy().union(umal)
				if len(test) <= 10:
					front.append(i)
					superFront.append(i)
					frontAdj = test
				else:
					return
			for i in x:
				self.recurAdj(i)	


	def getFrontiers(self):
		global frontAdj
		global front
		global superFront
		sortedMineAdjLocs = sorted(self._mineAdjLocs, key=lambda element: (element[1], element[0]))
		templist = sortedMineAdjLocs.copy()
		frontiers = []
		superFront = []

		while len(templist) > 0:
			front = []
			frontAdj = set(self.getAdjacentRem(templist[0]))
			front.append(templist[0])
			superFront.append(templist[0])
			self.recurAdj(templist[0])
			front = sorted(front, key=lambda element: (element[1], element[0]))
			frontAdj = sorted(list(frontAdj), key=lambda element: (element[1], element[0]))
			frontiers.append((front, frontAdj))
			temp = []
			for i in templist:
				if not i in front:
					temp.append(i)
			templist = temp
		return frontiers	


	def worldCheckingDEBUG(self):
		print("\n___________________________________STARTING WORLD CHECKER___________________________________")
		frontiers = self.getFrontiers()
		for i in frontiers:
			print("front:", i[0])
			print("frontAdj:", i[1])
			print("\n")
		
		definite_mines = []
		safeLocs = []
	
		for curFront in frontiers:
			worlds = [[int(x) for x in list(('{0:0'+str(len(curFront[1]))+'b}').format(y))] for y in range(pow(2,len(curFront[1])))][1:]
			solutions = []
			superworld = []
		
			for world in worlds:
				# GETTING MINES FROM BINARY WORLD
				mines = []
				for idx, mine in enumerate(world):
					if mine == 1:
						mines.append(curFront[1][idx])
	
				# CREATING LOC/NUM DICT OF CURRENT FRONTIER LOCS
				curFrontNumLocDict = {}    
				for loc in curFront[0]:
					curFrontNumLocDict[loc] = self._locNumDict[loc]
	
				# REDUCING NUM OF LOCS TO SEE IF CUR WORLD IS A POSSIBLE SOLUTION
				for mine in mines:
					for loc in curFront[0]:
						if self.isAdjacent(loc, mine):
							curFrontNumLocDict[loc] -= 1
	
				# STORING SOLUTIONS
				if all(v == 0 for v in curFrontNumLocDict.values()):
					solutions.append([world,  mines])
		
					# ADDIGN SOLUTION VALUES TO SUPERWORLD
					if superworld == []:
						superworld = world
					else:
						for idx, i in enumerate(superworld):
							if i + world[idx] >= 1:
								superworld[idx] = 1
							else:
		 						superworld[idx] = superworld[idx] + world[idx]
					print("CUR FRONT:", curFront[0], "CUR WORLD:", world, "CUR FRONT ADJ:", curFront[1], "MINES:", mines)
					print("UPDATED CURRENT FRONT LOCNUMDICT", curFrontNumLocDict, "\n")
	
			if len(solutions) == 1:
				definite_mines.extend(solutions[0][1])
			for idx, i in enumerate(superworld):
				if i == 0:
					safeLocs.append(curFront[1][idx])
			print("SUPERWORLD:", superworld)
			print("------------------------------------------------------------------------------------------------")
		print("FOUND MINES:", definite_mines)
		print("FOUND SAFELOCS:", safeLocs)
		print("____________________________________ENDING WORLD CHECKER____________________________________\n")
		return definite_mines, safeLocs


	def worldChecking(self):
		frontiers = self.getFrontiers()
		
		definite_mines = []
		safeLocs = []
	
		for curFront in frontiers:
			worlds = [[int(x) for x in list(('{0:0'+str(len(curFront[1]))+'b}').format(y))] for y in range(pow(2,len(curFront[1])))][1:]
			solutions = []
			superworld = []
		
			for world in worlds:
				# GETTING MINES FROM BINARY WORLD
				mines = []
				for idx, mine in enumerate(world):
					if mine == 1:
						mines.append(curFront[1][idx])
	
				# CREATING LOC/NUM DICT OF CURRENT FRONTIER LOCS
				curFrontNumLocDict = {}    
				for loc in curFront[0]:
					curFrontNumLocDict[loc] = self._locNumDict[loc]
	
				# REDUCING NUM OF LOCS TO SEE IF CUR WORLD IS A POSSIBLE SOLUTION
				for mine in mines:
					for loc in curFront[0]:
						if self.isAdjacent(loc, mine):
							curFrontNumLocDict[loc] -= 1
	
				# STORING SOLUTIONS
				if all(v == 0 for v in curFrontNumLocDict.values()):
					solutions.append([world,  mines])
		
					# ADDIGN SOLUTION VALUES TO SUPERWORLD
					if superworld == []:
						superworld = world
					else:
						for idx, i in enumerate(superworld):
							if i + world[idx] >= 1:
								superworld[idx] = 1
							else:
		 						superworld[idx] = superworld[idx] + world[idx]
	
			if len(solutions) == 1:
				definite_mines.extend(solutions[0][1])
			for idx, i in enumerate(superworld):
				if i == 0:
					safeLocs.append(curFront[1][idx])
		return definite_mines, safeLocs

