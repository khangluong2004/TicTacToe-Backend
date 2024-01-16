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
    newBoard[action[0]][action[1]] = X if isX else O

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
                numberX += (1 << (i + j * len(board[0])))
            elif board[i][j] == O:
                numberO += (1 << (i + j * len(board[0])))
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
        if (numberX & (1 << totalCell)):
            board[i % rowLen][i // rowLen] = X
        if (numberO & (1 << totalCell)):
            board[i % rowLen][i // rowLen] = O
    
    return board
    

# Create a global memoization cache
# Format: (numberX, numberO) -> Choice, Val
cache = {}


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    curPlayer = player(board)

    choice = (-1, -1)
    if curPlayer == X:
        choice = maxPlayer(board, 1, False)[0]
    else:
        choice = minPlayer(board, -1, False)[0]

    return choice  
  

def maxPlayer(board, curMin, isMinSet) -> tuple:
    """
    Returns the choice of max player X, along with the utility
    """

    # Base case
    if terminal(board):
        return (None, utility(board))
    
    # Check cache
    numberX, numberO = bitmaskBoard(board)
    if (numberX, numberO) in cache:
        return cache[(numberX, numberO)]

    # Recursive case    
    maxVal = -1
    maxChoice = None
    allowedActions = actions(board)

    for action in allowedActions:
        newBoard = result(board, action)
        if maxChoice == None:
            _, maxVal = minPlayer(newBoard, -1, False)
            maxChoice = action
        else:
            _, newVal = minPlayer(newBoard, maxVal, True)
            if (newVal > maxVal):
                maxVal = newVal
                maxChoice = action
            
        # Alpha-beta prunning
        # If the minVal is set, and the current maxVal is smaller than
        # previous minVal, then return to break out, since it's irrelevant
        # anyway
        if (isMinSet and maxVal >= curMin):
            return (maxChoice, maxVal)

    # Add to cache
    cache[(numberX, numberO)] = (maxChoice, maxVal)
    
    return (maxChoice, maxVal)


def minPlayer(board, curMax, isMaxSet) -> tuple:
    """
    Returns the choice of min player O, along with the utility
    """

    # Base case
    if terminal(board):
        return (None, utility(board))
    
    # Check cache
    numberX, numberO = bitmaskBoard(board)
    if (numberX, numberO) in cache:
        return cache[(numberX, numberO)]
    
    # Recursive case
    minVal = 1
    minChoice = None
    allowedActions = actions(board)

    for action in allowedActions:
        newBoard = result(board, action)
        if minChoice == None:
            _, minVal = maxPlayer(newBoard, -1, False)
            minChoice = action
        else:
            _, newVal = maxPlayer(newBoard, minVal, True)
            if (newVal < minVal):
                minVal = newVal
                minChoice = action
        
        # Alpha-beta prunnning
        # If the maxVal is set, and the minVal is lower than curMax, 
        # then this search is irrelevant (as the maxPlayer would choose the 
        # curMax previously), so return to break out
        
        if (isMaxSet and minVal <= curMax):
            return (minChoice, minVal)
    
    # Add cache
    cache[(numberX, numberO)] = (minChoice, minVal)
    
    return (minChoice, minVal)