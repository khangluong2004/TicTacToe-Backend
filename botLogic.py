"""
Tic Tac Toe Player
"""

import math
import copy
import time

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.

    Not efficient. Could have just keep a count instead of stateless function.
    """

    countX = 0
    countO = 0

    for row in board:
        for cell in row:
            if cell == X:
                countX += 1
            elif cell == O:
                countO += 1

    # Initial state
    if countX == 0 and countO == 0:
        return X 
    
    # Since X starts first, then O turn if X moves more than O
    if countX > countO:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    result = set()

    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                result.add((i, j))
    
    return result


def result(board, action, isX):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    # Check legal actions
    legalActions = actions(board)

    if action not in legalActions:
        raise ValueError("Not legal actions")
    
    # Make a deep copy, then implement the action
    newBoard = copy.deepcopy(board)
    if isX:
        newBoard[action[0]][action[1]] = X
    else:
        newBoard[action[0]][action[1]] = O

    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check rows
    for i in range(len(board)):
        for j in range(len(board) - 2):
            if not board[i][j]:
                continue

            if board[i][j] == board[i][j+1] and board[i][j+1] == board[i][j+2]:
                return board[i][j]
    
    # Check cols
    for i in range(len(board) - 2):
        for j in range(len(board[0])):
            if not board[i][j]:
                continue

            if board[i][j] == board[i+1][j] and board[i+1][j] == board[i+2][j]:
                return board[i][j]

        
    
    # Check the 2 diagonal
    # Right diagonal
    for i in range(len(board) - 2):
        for j in range(len(board) - 2):
            if not board[i][j]:
                continue
            
            if board[i][j] == board[i+1][j+1] \
                and board[i+1][j+1] == board[i+2][j+2]:
                return board[i][j]
    
    # Left diagonal
    for i in range(len(board) - 2):
        for j in range(2, len(board)):
            if not board[i][j]:
                continue

            if board[i][j] == board[i+1][j-1] \
                and board[i+1][j-1] == board[i+2][j-2]:
                return board[i][j]

    return None    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board):
        return True


    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
            
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    checkWinner = winner(board)

    if checkWinner == X:
        return 1
    elif checkWinner == O:
        return -1
    else:
        return 0


def bitmaskBoard(board):
    """
    Convert the board into a pair integer with bitmask
    """
    numberX = 0
    numberO = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == X:
                numberX += (1 << (i * len(board[0]) + j))
            elif board[i][j] == O:
                numberO += (1 << (i * len(board[0]) + j))
    return (numberX, numberO)


def unmaskBoard(numberX, numberO):
    """
    Convert from the 2 number back to the board
    """
    board = initial_state()
    totalCell = len(board) * len(board[0])
    rowLen = len(board[0])

    # Fill X
    for i in range(totalCell):
        if (numberX & (1 << i)):
            board[i // rowLen][i % rowLen] = X
        if (numberO & (1 << i)):
            board[i // rowLen][i % rowLen] = O
    
    return board

#-----------------------------------------------------
# The method is used to find the minimax utility value for each action in 
# a 3x3 square. A 4x4 board is then constructed by combining 4 overlapping
# 3x3 square, and the action with top utility is chosen.   

# The utility is calculated as: Utility = Final State * (9 - steps taken)
# Where final state is: 0 if tie, 1 if X wins and -1 if O wins

def minimax(board, isX):
    """
    Returns the optimal action for the current player on the board.
    """

    choice = (-1, -1)
    if isX:
        choice = boardMapper(board, maxPlayer, compareMax, minPlayer)
    else:
        choice = boardMapper(board, minPlayer, compareMin, maxPlayer)

    return choice


def compareMax(a, b):
    return a > b

def compareMin(a, b):
    return a < b

def calcWeightedUtil(val, level, isOpponent):
    """
    Helper function to find the weighted utility
    """

    # Deal with 1 step to victory, prioritize that step then
    # isOpponent is set, because the terminal condition is checked by the 
    # next player (with the minimax recursion), instead of the current player
    # who plays the move
    if level <= 2 and isOpponent:
        return val * (3 ** 11)

    return val * (3 ** (9 - level))


# Create a global memoization cache for the next move and utility value
# in the 3x3 region

# If cache needed, TODO: Add isX into the cache, since can't derive the turn from the board

# Format: (numberX, numberO) -> Choice, Val
# cacheNextMove = {}

# Cache for the UtilBoard during processing for player
# cacheUtilBoard = {}


def boardMapper(board, playerFunc, playerCompFunc, opponentFunc):
    """
    Map 4 3x3 squares into 1 4x4 board, and pick out the best move
    """  

    utilBoard = initial_state()

    # Initialize the "empty" states of the board, since some
    # of the 3x3 might not be affected by a move, thus the cost
    # of not moving should be included

    for i in range(len(board) - 2):
        for j in range(len(board) - 2):
            newBoard = [board[i + offset][j:j+3] for offset in range(3)]

            # CACHE:
            # numberX, numberO = bitmaskBoard(newBoard)
            # if (numberX, numberO) in  cacheNextMove:
            #     choice, opponentVal = cacheNextMove[(numberX, numberO)]
            # else:
            #     choice, opponentVal = opponentFunc(newBoard, 0, False, 1, None, 0, 0, True)
            #     # Add cache
            #     cacheNextMove[(numberX, numberO)] = (choice, opponentVal)


            choice, opponentVal = opponentFunc(newBoard, 0, False, 1, None, 0, 0, True, True)
            
            # print("Opponent score: ", opponentVal)
            # print("Before: ", utilBoard)

            # When the 3x3 region is filled
            if choice == None:
                continue            

            # Set all cells outside the square to the potential
            # opponent values if left this square unmoved
            for set_i in range(len(board)):
                for set_j in range(len(board)):
                    if (i <= set_i and set_i <= i + 2
                        and j <= set_j and set_j <= j + 2):
                        continue
                    
                    if utilBoard[set_i][set_j] != None:
                        utilBoard[set_i][set_j] += opponentVal
                    else:
                        utilBoard[set_i][set_j] = opponentVal
            
            # print("After", utilBoard)

    for i in range(len(board) - 2):
        for j in range(len(board) - 2):
            newBoard = [board[i + offset][j:j+3] for offset in range(3)]
            # print("New board")
            # print(newBoard)
            playerFunc(newBoard, 0, False, 1, utilBoard, i, j, False, False)

            # print("Util Board")
            # print(utilBoard)
    
    # print("Util Board")
    # print(utilBoard)
    
    # Find the best choice
    chosenChoice = (-1, -1)
    compareVal = None

    for action in actions(board):
        i, j = action

        if compareVal == None:
            compareVal = utilBoard[i][j]
            chosenChoice = (i, j)

        elif playerCompFunc(utilBoard[i][j], compareVal):
            compareVal = utilBoard[i][j]
            chosenChoice = (i, j)
    
    return chosenChoice

def updateUtilBoard(utilBoard, startX, startY, val, action):
    if utilBoard == None:
        return
    
    adjustX = startX + action[0]
    adjustY = startY + action[1]
    if utilBoard[adjustX][adjustY] == None:
        utilBoard[adjustX][adjustY] = val
    else:
        utilBoard[adjustX][adjustY] += val

def copyUtilBoard(curUtilBoard, cachedUtilBoard, startX, startY):
    for i in range(len(cachedUtilBoard)):
        for j in range(len(cachedUtilBoard)):
            updateUtilBoard(curUtilBoard, startX, startY, cachedUtilBoard[i][j], (i, j))


def playerTemplate(board, curOptimal, isOptimalSet, level, 
                   playerCompFunc, opponentFunc, isMax, isOpponent,
                   utilBoard = None, startX = -1, startY = -1, isPrunable = False):
    """
    Template for both max and min player.
    Returns the choice of the player, along with the utility, while updating
    the utility of all cells if at top level
    """

    # Base case
    if terminal(board):
        return (None, calcWeightedUtil(utility(board), level, isOpponent))
    
    # CACHE
    # numberX, numberO = bitmaskBoard(board)
    # if level == 1:
    #     if (numberX, numberO) in cacheUtilBoard:
    #         copyUtilBoard(utilBoard, cacheUtilBoard[(numberX, numberO)], startX, startY)
    #         return cacheNextMove[(numberX, numberO)]
    # else:
    #     if (numberX, numberO) in cacheNextMove:
    #         return cacheNextMove[((numberX, numberO))]

    # Recursive case    
    optimalVal = -1
    optimalChoice = None
    allowedActions = actions(board)

    # Allow pruning if not top 2 levels, since no need for accurate utility of all points
    if level > 2 and not isPrunable:
        isPrunable = True

    for action in allowedActions:
        newBoard = result(board, action, isMax)
        if optimalChoice == None:
            _, newVal = opponentFunc(newBoard, -1, False, level + 1, utilBoard, startX, startY, True, not isOpponent)
            optimalVal = newVal
            optimalChoice = action

        else:
            # Stop pruning to get the actual correct utility
            _, newVal = opponentFunc(newBoard, optimalVal, True, level + 1, utilBoard, startX, startY, isPrunable, not isOpponent)
            if playerCompFunc(newVal, optimalVal):
                optimalVal = newVal
                optimalChoice = action
            
        if level == 1:
            updateUtilBoard(utilBoard, startX, startY, newVal, action)
            
        # Alpha-beta prunning
        # If the minVal is set, and the current maxVal is smaller than
        # previous minVal, then return to break out, since it's irrelevant
        # anyway
        if (isPrunable and isOptimalSet and (optimalVal == curOptimal or playerCompFunc(optimalVal, curOptimal))):
            return (optimalChoice, optimalVal)

    # CACHE
    # Add to cache
    # cacheNextMove[(numberX, numberO)] = (optimalChoice, optimalVal)

    # If top level, then add the utilBoard
    # if utilBoard != None and level == 1:
    #     cacheUtilBoard[(numberX, numberO)] = [utilBoard[newX][startY: startY + 3] for newX in range(startX, startX + 3)]

    # Check if top level, then also cache
    
    return (optimalChoice, optimalVal)

def maxPlayer(board, curMin, isMinSet, level, 
              utilBoard = None, startX = -1, startY = -1, isPrunable = False, 
              isOpponent = True):
    return playerTemplate(board=board, curOptimal=curMin, isOptimalSet=isMinSet, level=level, 
                   playerCompFunc=compareMax, opponentFunc=minPlayer, isMax=True, isOpponent=isOpponent,
                   utilBoard=utilBoard, startX=startX, startY=startY, isPrunable=isPrunable)
    
def minPlayer(board, curMax, isMaxSet, level, 
              utilBoard = None, startX = -1, startY = -1, isPrunable = False, 
              isOpponent = False):
    return playerTemplate(board=board, curOptimal=curMax, isOptimalSet=isMaxSet, level=level,
                          playerCompFunc=compareMin, opponentFunc=maxPlayer, isMax=False, isOpponent=isOpponent,
                          utilBoard=utilBoard, startX=startX, startY=startY, isPrunable=isPrunable)



# Testing
def printBoard(board):
    print("Print board: ")
    for row in board:
        print(row)

def test():
    board = initial_state()
    for i in range(16):
        if i % 2 == 1:
            beforeTime = time.time()
            choice = minimax(board, False)
            board = result(board, choice, False)
            afterTime = time.time()
            print(f"Taken: {afterTime - beforeTime}s")
        else:
            x_loc = int(input("X location: "))
            y_loc = int(input("Y location: "))
            board = result(board, (x_loc, y_loc), True)
        
        printBoard(board)
    
    # with open("cacheNextMove.py", "w") as cacheNextFile:
    #     cacheNextFile.write("cacheNextMove = " + str(cacheNextMove))
    
    # with open("cacheUtilBoard.py", "w") as cachedUtilBoardFile:
    #     cachedUtilBoardFile.write("cacheUtilBoard = " + str(cacheUtilBoard))

if __name__ == '__main__':
    test()