"""
Tic Tac Toe Player
"""

import math
import copy

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

# Create a global memoization cache
# Format: (numberX, numberO) -> Choice, Val
cache = {}


def minimax(board, isX):
    """
    Returns the optimal action for the current player on the board.
    """

    choice = (-1, -1)
    if isX:
        choice = boardMapper(board, maxPlayer, compareMax)
    else:
        choice = boardMapper(board, minPlayer, compareMin)

    return choice


def compareMax(a, b):
    return a > b

def compareMin(a, b):
    return a < b

def calcWeightedUtil(val, level):
    """
    Helper function to find the weighted utility
    """
    return val * (9 - level)

# TODO: Factor in the util of not moving
def boardMapper(board, playerFunc, compareFunc):
    """
    Map 4 3x3 squares into 1 4x4 board, and pick out the best move
    """  

    utilBoard = initial_state()

    for i in range(len(board) - 2):
        for j in range(len(board) - 2):
            newBoard = [board[i + offset][j:j+3] for offset in range(3)]
            print("New board")
            print(newBoard)
            playerFunc(newBoard, 0, False, 1, utilBoard, i, j)

            print("Util Board")
            print(utilBoard)
    
    print("Util Board")
    print(utilBoard)
    
    # Find the best choice
    chosenChoice = (-1, -1)
    compareVal = None

    for action in actions(board):
        i, j = action

        if compareVal == None:
            compareVal = utilBoard[i][j]
            chosenChoice = (i, j)

        elif compareFunc(utilBoard[i][j], compareVal):
            compareVal = utilBoard[i][j]
            chosenChoice = (i, j)
    
    return chosenChoice


def maxPlayer(board, curMin, isMinSet, level, utilBoard, startX, startY) -> tuple:
    """
    Returns the choice of max player X, along with the utility
    """

    # Base case
    if terminal(board):
        return (None, utility(board))
    
    # Check cache
    # numberX, numberO = bitmaskBoard(board)
    # if (numberX, numberO) in cache:
    #     return cache[(numberX, numberO)]

    # Recursive case    
    maxVal = -1
    maxChoice = None
    allowedActions = actions(board)

    for action in allowedActions:
        newBoard = result(board, action, True)
        if maxChoice == None:
            _, maxVal = minPlayer(newBoard, -1, False, level + 1, utilBoard, startX, startY)
            maxChoice = action

            if level == 1:
                adjustX = startX + action[0]
                adjustY = startY + action[1]
                if utilBoard[adjustX][adjustY] == None:
                    utilBoard[adjustX][adjustY] = calcWeightedUtil(maxVal, level)
                else:
                    utilBoard[adjustX][adjustY] += calcWeightedUtil(maxVal, level)

        else:
            _, newVal = minPlayer(newBoard, maxVal, True, level + 1, utilBoard, startX, startY)
            if (newVal > maxVal):
                maxVal = newVal
                maxChoice = action
            
            if level == 1:
                adjustX = startX + action[0]
                adjustY = startY + action[1]
                if utilBoard[adjustX][adjustY] == None:
                    utilBoard[adjustX][adjustY] = calcWeightedUtil(newVal, level)
                else:
                    utilBoard[adjustX][adjustY] += calcWeightedUtil(newVal, level)
            
        # Alpha-beta prunning
        # If the minVal is set, and the current maxVal is smaller than
        # previous minVal, then return to break out, since it's irrelevant
        # anyway
        if (isMinSet and maxVal >= curMin):
            return (maxChoice, maxVal)

    # Add to cache
    # cache[(numberX, numberO)] = (maxChoice, maxVal)
    
    return (maxChoice, maxVal)


def minPlayer(board, curMax, isMaxSet, level, utilBoard, startX, startY) -> tuple:
    """
    Returns the choice of min player O, along with the utility
    """

    # Base case
    if terminal(board):
        return (None, utility(board))
    
    # Check cache
    # numberX, numberO = bitmaskBoard(board)
    # if (numberX, numberO) in cache:
    #     return cache[(numberX, numberO)]
    
    # Recursive case
    minVal = 1
    minChoice = None
    allowedActions = actions(board)

    for action in allowedActions:
        newBoard = result(board, action, False)
        if minChoice == None:
            _, minVal = maxPlayer(newBoard, -1, False, level + 1, utilBoard, startX, startY)
            minChoice = action

            if level == 1:
                adjustX = startX + action[0]
                adjustY = startY + action[1]
                if utilBoard[adjustX][adjustY] == None:
                    utilBoard[adjustX][adjustY] = calcWeightedUtil(minVal, level)
                else:
                    utilBoard[adjustX][adjustY] += calcWeightedUtil(minVal, level)

        else:
            _, newVal = maxPlayer(newBoard, minVal, True, level + 1, utilBoard, startX, startY)
            if (newVal < minVal):
                minVal = newVal
                minChoice = action

            if level == 1:
                adjustX = startX + action[0]
                adjustY = startY + action[1]
                if utilBoard[adjustX][adjustY] == None:
                    utilBoard[adjustX][adjustY] = calcWeightedUtil(newVal, level)
                else:
                    utilBoard[adjustX][adjustY] += calcWeightedUtil(newVal, level)
        
        # Alpha-beta prunnning
        # If the maxVal is set, and the minVal is lower than curMax, 
        # then this search is irrelevant (as the maxPlayer would choose the 
        # curMax previously), so return to break out
        
        if (isMaxSet and minVal <= curMax):
            return (minChoice, minVal)
    
    # Add cache
    # cache[(numberX, numberO)] = (minChoice, minVal)
    
    return (minChoice, minVal)



# Testing
def printBoard(board):
    print("Print board: ")
    for row in board:
        print(row)

def test():
    board = initial_state()
    for i in range(16):
        if i % 2 == 1:
            choice = minimax(board, False)
            board = result(board, choice, False)
        else:
            x_loc = int(input("X location: "))
            y_loc = int(input("Y location: "))
            board = result(board, (x_loc, y_loc), True)
        
        printBoard(board)

test()
        