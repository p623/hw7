import copy
import json
import logging
import random
import webapp2
import time

# Reads json description of the board and provides simple interface.
class Game:
	# Takes json or a board directly.
	def __init__(self, body=None, board=None):
                if body:
		        game = json.loads(body)
                        self._board = game["board"]
                else:
                        self._board = board

	# Returns piece on the board.
	# 0 for no pieces, 1 for player 1, 2 for player 2.
	# None for coordinate out of scope.
	def Pos(self, x, y):
		return Pos(self._board["Pieces"], x, y)

	# Returns who plays next.
	def Next(self):
		return self._board["Next"]

	# Returns the array of valid moves for next player.
	# Each move is a dict
	#   "Where": [x,y]
	#   "As": player number
	def ValidMoves(self):
                moves = []
                for y in xrange(1,9):
                        for x in xrange(1,9):
                                move = {"Where": [x,y],
                                        "As": self.Next()}
                                if self.NextBoardPosition(move):
                                    	moves.append(move)
	
                return moves

	# Helper function of NextBoardPosition.  It looks towards
	# (delta_x, delta_y) direction for one of our own pieces and
	# flips pieces in between if the move is valid. Returns True
	# if pieces are captured in this direction, False otherwise.
	def __UpdateBoardDirection(self, new_board, x, y, delta_x, delta_y):
		player = self.Next()
		opponent = 3 - player
		look_x = x + delta_x
		look_y = y + delta_y
		flip_list = []
		while Pos(new_board, look_x, look_y) == opponent:
			flip_list.append([look_x, look_y])
			look_x += delta_x
			look_y += delta_y
		if Pos(new_board, look_x, look_y) == player and len(flip_list) > 0:
                        # there's a continuous line of our opponents
                        # pieces between our own pieces at
                        # [look_x,look_y] and the newly placed one at
                        # [x,y], making it a legal move.
			SetPos(new_board, x, y, player)
			for flip_move in flip_list:
				flip_x = flip_move[0]
				flip_y = flip_move[1]
				SetPos(new_board, flip_x, flip_y, player)
                        return True
                return False

	# Takes a move dict and return the new Game state after that move.
	# Returns None if the move itself is invalid.
	def NextBoardPosition(self, move):
		x = move["Where"][0]
		y = move["Where"][1]
                if self.Pos(x, y) != 0:
                        # x,y is already occupied.
                        return None
		new_board = copy.deepcopy(self._board)
                pieces = new_board["Pieces"]

		if not (self.__UpdateBoardDirection(pieces, x, y, 1, 0)
                        | self.__UpdateBoardDirection(pieces, x, y, 0, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, 0)
		        | self.__UpdateBoardDirection(pieces, x, y, 0, -1)
		        | self.__UpdateBoardDirection(pieces, x, y, 1, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, 1)
		        | self.__UpdateBoardDirection(pieces, x, y, 1, -1)
		        | self.__UpdateBoardDirection(pieces, x, y, -1, -1)):
                        # Nothing was captured. Move is invalid.
                        return None
                
                # Something was captured. Move is valid.
                new_board["Next"] = 3 - self.Next()
		return Game(board=new_board)


# Returns piece on the board.
# 0 for no pieces, 1 for player 1, 2 for player 2.
# None for coordinate out of scope.
#
# Pos and SetPos takes care of converting coordinate from 1-indexed to
# 0-indexed that is actually used in the underlying arrays.

def Pos(board, x, y):
	if 1 <= x and x <= 8 and 1 <= y and y <= 8:
		return board[y-1][x-1]
	return None

# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):
	if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0,1,2]:
		return False
	if isinstance(board,dict):
		board=board["Pieces"]
	board[y-1][x-1] = piece
	#logging.info('SetPos(board, %d, %d, %d) board contents: %s' % (x,y,piece,board))

# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):
	s = ""
	for row in board:
		for piece in row:
			s += str(piece)
		s += nl
	return s

def PrettyMove(move):
	m = move["Where"]
	return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])

#------------------written by Mamiko Ino----------------------------
def calculate(board):
	pointOfBlack=0
	pointOfWhite=0
	for indexForX in range(2,8):
		for indexForY in range(2,8):
			if indexForX==2 or 7 and indexForY==2 or 7 and board[indexForX-1][indexForY-1]==1:
				pointOfBlack-=10
			elif indexForX==2 or 7 and indexForY==2 or 7 and board[indexForX-1][indexForY-1]==2:	
				pointOfWhite+=10
			else:
				if board[indexForX-1][indexForY-1]==1:
					pointOfBlack+=1
				elif board[indexForX-1][indexForY-1]==2:
					pointOfWhite-=1

	for indexForX in [1,8]:
		for indexForY in range(2,8):
			if indexForY==2 or 7 and board[indexForX-1][indexForY-1]==1:
				pointOfBlack-=3
			elif indexForY==2 or 7 and board[indexForX-1][indexForY-1]==2:
				pointOfWhite+=3
			else:
				if board[indexForX-1][indexForY-1]==1:
					pointOfBlack+=6
				elif board[indexForX-1][indexForY-1]==2:
					pointOfWhite-=6
		
	for indexForY in [1,8]:
		for indexForX in range(2,8):
			if indexForX==2 or 7 and board[indexForX-1][indexForY-1]==1:
				pointOfBlack-=3
			elif indexForX==2 or 7 and board[indexForX-1][indexForY-1]==2:
				pointOfWhite+=3
			else:
				if board[indexForX-1][indexForY-1]==1:
					pointOfBlack+=6
				elif board[indexForX-1][indexForY-1]==2:
					pointOfWhite-=6
		
	for indexForX in [1,8]:
		for indexForY in [1,8]:
			if board[indexForX-1][indexForY-1]==1:
				pointOfBlack+=20
			elif board[indexForX-1][indexForY-1]==2:
				pointOfWhite-=20

	boardPoint=pointOfBlack+pointOfWhite
	return boardPoint

def calculateAsGreedy(board):
	pointOfBlack=0
	pointOfWhite=0
	for indexForX in range(1,9):
		for indexForY in range(1,9):
			if board[indexForX-1][indexForY-1]==1:
				pointOfBlack+=1
			elif board[indexForX-1][indexForY-1]==2:
				pointOfWhite-=1
	boardPoint=pointOfBlack+pointOfWhite
	return boardPoint

def calculateNextMove(g,board,blackOrWhite):
	g._board["Pieces"]=board
	valid_moves=g.ValidMoves()
	if blackOrWhite==1:
		boardPoint=-1*len(valid_moves)
	else:
		boardPoint=len(valid_moves)
	return boardPoint


def moveCount(board):#for checking the number of play by the end of the game
	moveCount=0
	for indexForX in range(1,9):
		for indexForY in range(1,9):
			if board[indexForX-1][indexForY-1]==1 or board[indexForX-1][indexForY-1]==2:
				moveCount+=1
	return moveCount

def score(g,board,depth, blackOrWhite,timeManager):
	startTime=time.time()
	firstDepth=depth
	if depth==0:
		listForScore=[]
		g._board["Pieces"]=board
		valid_moves=g.ValidMoves()
		for move in valid_moves:
			g.NextBoardPosition(move)#g,move
			if moveCount(g._board["Pieces"])<60: #and moveCount(g._board["Pieces"])>=14: #perform as greedy if about 5 pieces left to move
				listForScore.append(calculate(g._board["Pieces"]))
			#elif moveCount(g._board["Pieces"])<14:
				#listForScore.append(calculateNextMove(g,g._board["Pieces"],blackOrWhite))#to be inside at the starting game
			else:
				listForScore.append(calculateAsGreedy(g._board["Pieces"]))

			usedTime=time.time()-startTime
			timeManager-=usedTime

		if blackOrWhite==1 and firstDepth%2==0 or blackOrWhite==2 and firstDepth%2==1:
			return max(listForScore)
		else:
			return min(listForScore)

	else:
		listPointStock=[]
		g._board["Pieces"]=board
		valid_moves=g.ValidMoves()
		for move in valid_moves:
			usedTime=time.time()-startTime
			if timeManager-usedTime<=0:
				break
			g.NextBoardPosition(move)#g,move
			listPointStock.append(score(g,g._board["Pieces"],depth-1,blackOrWhite,timeManager-usedTime)) 
		if blackOrWhite==1 and (firstDepth-depth)%2==0 or blackOrWhite==2 and (firstDepth-depth)%2==1:
			return max(listPointStock)
		else:
			return min(listPointStock)
				
def minMax(g):
	startTime=time.time()
	print(startTime)
	timeManager=6
	valid_moves=g.ValidMoves()
	depth=1
	blackOrWhite=valid_moves[0]["As"]
	moveStockStock={}
	pointMoveStock=[]
	while True:
		moveStock={}
		pointOfMove=[]
		for move in valid_moves:
			g.NextBoardPosition(move)#g,move
			scoreOfThisMove=score(g,g._board["Pieces"],depth,3-blackOrWhite,timeManager)
			if time.time()-startTime>timeManager:
				print(time.time())
				break
			pointOfMove.append(scoreOfThisMove)
			moveStock[scoreOfThisMove]=move
		if time.time()-startTime>timeManager:
			print(time.time())
			break
		print("depth: "+str(depth))
		print(moveStock)
		depth+=1
		moveStockStock=moveStock#stock for break
		pointMoveStock=pointOfMove#stock for break

	if pointOfMove==[]:
		pointOfMove=pointMoveStock
		moveStock=moveStockStock	

	if blackOrWhite==1:
		choicedPoint=max(pointOfMove)
		return moveStock[choicedPoint]
	else:
		choicedPoint=min(pointOfMove)
		return moveStock[choicedPoint]

	
	
#-----------------------written by Mamiko Ino--------------------------


class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.
    def get(self):
        if not self.request.get('json'):
          self.response.write("""
<body><form method=get>
Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
<p/><input type=submit>
</form>
</body>
""")
          return
        else:
          g = Game(self.request.get('json'))
          self.pickMove(g)

	
    def post(self):
    	# Reads JSON representation of the board and store as the object.
    	g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)


    def pickMove(self, g):
    	# Gets all valid moves.
    	valid_moves = g.ValidMoves()
    	if len(valid_moves) == 0:
    		# Passes if no valid moves.
    		self.response.write("PASS")
    	else:
    		# Chooses a valid move randomly if available.
                # TO STEP STUDENTS:
                # You'll probably want to change how this works, to do something
                # more clever than just picking a random move.
    		self.response.write(PrettyMove(minMax(g)))

# ver 201807102220


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)