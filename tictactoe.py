"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    player = X
    x_count = o_count = 0
    for row in board:
        for cell in row:
            if cell == X:
                x_count+=1
            if cell == O:
                o_count+=1

    if x_count > o_count: player = O
    return player



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    actions = set()
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == EMPTY:
                actions.add((row,col))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i,j = action
    new_board = copy.deepcopy(board)

    if(board[i][j] != EMPTY):
        raise ValueError("Invalid move: cell is not empty")
    else:
        new_board[i][j] = player(board)
        return new_board



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Verificar Filas
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]

    # Verificar columnas
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]

    # Verificar diagonales
    if board[0][0] == board[1][1] == board[2][2] != EMPTY or board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    game_over = True

    # Empate
    for row in board:
        for cell in row:
            if cell == EMPTY:
                game_over = False
                continue

    # Verificar Filas
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return True

    # Verificar columnas
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return True

    # Verificar diagonales
    if board[0][0] == board[1][1] == board[2][2] != EMPTY or board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return True

    return game_over



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        print("terminal")
        return None

    best_value = math.inf
    best_action = None

    for action in actions(board):
        v = maxValue(result(board, action))
        if v < best_value:
            best_value = v
            best_action = action

    return best_action


def maxValue(board):
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, minValue(result(board, action)))
    return v


def minValue(board):
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, maxValue(result(board, action)))
    return v