#!/usr/bin/env python3
import random
from random import randint

# Things to change:
#  -- If computer has perfect lookahead, it decides (correctly) that perfect
#     enemy play will always lead to a draw. Therefore it considers all
#     starting moves equally valuable. This is not ideal. It should prefer
#     moves that maximally constrain the other player to playing perfectly.
#     Then, when facing a nonideal opponent, it will maximize its likelihood
#     of winning.
# -- Static board strength evaluator should weight 2 aligned pieces more
#    than 2X value of a single unblocked piece. (2 pieces force immediate
#    response in 3x3, while 1 piece gives slack.) This is a hypothesis.
#    Could check by the following point.
# -- Allow both computers to use different algorithms (not just different
#    depths). E.g., one could weight static boards differently, and we
#    could discover the best play.
# -- Extend NxN play to only need to get 3 in a row, not N-in-a-row, which
#    is almost impossible to win.


# Settings
D = 3

EX_HUMAN = False
OH_HUMAN = True


MAX_N_EVALS_X = 50000000
MAX_N_EVALS_O = 1
# e.g. 9 is perfect play for 3x3, and uses peak ~500K evals
MAX_LOOKAHEAD_MOVES_X = 10
MAX_LOOKAHEAD_MOVES_O = 10

def nEvals(nAvail, depth):
    product = 1
    for i in range(depth):
        if nAvail < 2:
            break
        product *= nAvail
        nAvail -= 1
    return product

def maxDepthAllowed(nAvail, evalsAllowed):
    product = 1
    N = 0
    while product < evalsAllowed and nAvail > 0:
        product *= nAvail
        nAvail -= 1
        N += 1
    return N


# print(maxDepthAllowed(9,5e7))
# import sys
# sys.exit()
# --------


EX = -3
OH = -5

EXWIN = D*EX
OHWIN = D*OH

EMPTY = -999
DRAW = -111
STILLGOING = -43

RESIGN = (-1, -1)



def checkForWinFull(board):

    # Rows
    for i in range(D):
        srow = sum(board[i])
        if srow == OHWIN:
            return OH
        elif srow == EXWIN:
            return EX
    # Cols
    for i in range(D):
        scol = sum(board[j][i] for j in range(D))
        if scol == OHWIN:
            return OH
        elif scol == EXWIN:
            return EX

    # Diags
    sdown = sum(board[i][i] for i in range(D))
    if sdown == OHWIN:
        return OH
    elif sdown == EXWIN:
        return EX

    sup = sum(board[i][D-i-1] for i in range(D))
    if sup == OHWIN:
        return OH
    elif sup == EXWIN:
        return EX

    if any(_ == EMPTY for row in board for _ in row):
        return STILLGOING
    else:
        return DRAW


def checkForWin(board, rowPlayed, colPlayed):
    rowSum = sum(board[rowPlayed])
    colSum = sum(board[j][colPlayed] for j in range(D))
    if rowPlayed == colPlayed:
        downSum = sum(board[i][i] for i in range(D))
    else:
        downSum = EMPTY
    if rowPlayed == D-colPlayed-1:
        upSum = sum(board[i][D-i-1] for i in range(D))
    else:
        upSum = EMPTY

    if any(_ == OHWIN for _ in (rowSum,colSum,downSum,upSum)):
        return OH
    elif any(_ == EXWIN for _ in (rowSum,colSum,downSum,upSum)):
        return EX

    if any(_ == EMPTY for row in board for _ in row):
        return STILLGOING
    else:
        return DRAW


def printBoard(board):

    for i in range(D):
        rowStr = "|".join("X" if _ == EX else ("O" if _ == OH else ("·" if _ == EMPTY else "{:.4f}".format(_))) for _ in board[i])
        print(rowStr)
        if i < D - 1:
            print("-"*(2*D-1))


def getValidMoves(board):
    validMoves = []
    for row in range(D):
        for col in range(D):
            if board[row][col] == EMPTY:
                validMoves.append((row,col))
    return validMoves


def copyBoard(board):
    return [row[:] for row in board]

def otherPlayer(me):
    return OH if me == EX else EX

positionsEvaluated = 0

def scoreRowFlat(nOh, nEx):
    if nOh and nEx:
        return 0,0
    elif nOh:
        return nOh,0
    else:
        return 0,nEx

def scoreRowBoost(nOh, nEx):
    ''' returns oscore, xscore'''

    # 1 : 1
    # 2 : 3
    # 3 : 6 --> (N+1)*N/2
    if nOh and nEx:
        return 0,0
    elif nOh:
        return (nOh+1)*nOh/2
    else:
        return (nEx+1)*nEx/2

def evaluateStaticBoardStrength(board):
    '''
    Without looking ahead even a single move, try to determine
    the strength of player's position.
    Approach is the number of rows/cols/diags where
    only the player has played times the number of pieces played.

    x..
    oo.
    x..

    Gives:
    X score: 2*1 [2 rows with 1 piece played]
    O score: 1*2 + 1*1 [1 row with 2 pieces + 1 col with 1 piece]

    '''
    xscore = 0
    oscore = 0
    # Rows
    for row in board:
        nOh = sum(1 for _ in row if _ == OH)
        nEx = sum(1 for _ in row if _ == EX)
        if nOh and nEx:
            continue
        elif nOh:
            oscore += nOh
        elif nEx:
            xscore += nEx

    # Cols
    for i in range(D):
        nOh = sum(1 for row in board if row[i] == OH)
        nEx = sum(1 for row in board if row[i] == EX)
        if nOh and nEx:
            continue
        elif nOh:
            oscore += nOh
        elif nEx:
            xscore += nEx

    # Diags
    nOh = sum(1 for i in range(D) if board[i][i] == OH)
    nEx = sum(1 for i in range(D) if board[i][i] == EX)
    if nOh and nEx:
        pass
    elif nOh:
        oscore += nOh
    elif nEx:
        xscore += nEx

    sup = sum(board[i][D-i-1] for i in range(D))

    nOh = sum(1 for i in range(D) if board[i][D-i-1] == OH)
    nEx = sum(1 for i in range(D) if board[i][D-i-1] == EX)
    if nOh and nEx:
        pass
    elif nOh:
        oscore += nOh
    elif nEx:
        xscore += nEx

    # Returns x's advantage
    return xscore - oscore

WIN_SCORE = 10000
LOSS_SCORE = -WIN_SCORE
DRAW_SCORE = 0 # Tune this to decide whether to seek guaranteed draws

def playEval(boardIn, whoseTurn,depth=0, maxDepth=0):
    global positionsEvaluated # stats counter
    assert depth <= maxDepth

    if depth == 0:
        board = copyBoard(boardIn) # Don't modify input board
    else:
        board = boardIn

    validMoves = getValidMoves(board)

    enemyTurn = otherPlayer(whoseTurn)

    moveDict = {} # {move: score}
    for move in validMoves:
        row, col = move
        board[row][col] = whoseTurn # make the move

        winner = checkForWin(board,row,col)
        assert winner != enemyTurn # No play can cause other player to win.
        if winner == whoseTurn:
            score = WIN_SCORE
            positionsEvaluated += 1
        elif winner == DRAW:
            score = DRAW_SCORE
            positionsEvaluated += 1
        elif depth >= maxDepth:
            # Ran out of tree depth. Just take a look at the board and
            # decide how "strong" the position is
            xAdvantage = evaluateStaticBoardStrength(board)
            if whoseTurn == EX:
                score = xAdvantage
            else:
                score = -xAdvantage # X advantage hurts O
            positionsEvaluated += 1

            # Add tiny random perturbations so equally valued moves get
            # played randomly
            # score += random.random()*0.1
        else:
            # Still can search deeper. Recurse.
            response, enemyscore = playEval(board, enemyTurn, depth+1, maxDepth)
            score = -enemyscore # higher enemy's score hurts me

        # Add tiny random perturbations so equally valued moves get
        # played randomly
        score += random.random()*0.01
        moveDict[move] = score

        if positionsEvaluated > 10*max(MAX_N_EVALS_O,MAX_N_EVALS_X):
            raise Exception("WTF: ",positionsEvaluated,MAX_N_EVALS_O,MAX_N_EVALS_X)
        board[row][col] = EMPTY # undo move to keep going

    # Sort moves by score
    moves, scores = zip(*sorted(moveDict.items(), key=lambda x: -x[1]))

    if depth == 0:
        # Create ranked board for debugging
        rankedBoard = copyBoard(board)
        for i,(move,score) in enumerate(zip(moves,scores)):
            # rankedBoard[move[0]][move[1]] = i+1
            rankedBoard[move[0]][move[1]] = score
        return moves[0], scores[0], rankedBoard
    # Pick best move
    return moves[0], scores[0]





def getBestMove(board, whoseTurn, level=0):
    print("Thinking...")
    global positionsEvaluated
    positionsEvaluated = 0

    nAvail = len(getValidMoves(board))

    if whoseTurn == EX:
        maxDepth = min(MAX_LOOKAHEAD_MOVES_X, maxDepthAllowed(nAvail, MAX_N_EVALS_X))
    else:
        maxDepth = min(MAX_LOOKAHEAD_MOVES_O, maxDepthAllowed(nAvail, MAX_N_EVALS_O))
    print(nAvail,"Max depth is ",maxDepth, "to use about ",nEvals(nAvail,maxDepth),"tests")

    move, result, rankedBoard = playEval(board, whoseTurn, maxDepth=maxDepth)

    if True:
        printBoard(rankedBoard)

    print("Evaluated {} positions".format(positionsEvaluated))
    if result > WIN_SCORE*0.9:
        print("I'm guaranteed to win!!")
        return move
    elif result < LOSS_SCORE*0.9:
        print("I resign.")
        return RESIGN
    # elif result == DRAW_SCORE:
    #     print("Guaranteed draw!")


    return move

currentBoard = [[EMPTY for i in range(D)] for j in range(D)]

def getMove(whoseTurn):
    # Return zero-indexed row, col indices for play
    if whoseTurn == EX:
        if not EX_HUMAN:
            return getBestMove(currentBoard, EX)
        if OH_HUMAN:
            print("X move")
        else:
            print("Your move")
    elif whoseTurn == OH:
        if not OH_HUMAN:
            return getBestMove(currentBoard, OH)
        if EX_HUMAN:
            print("O move")
        else:
            print("Your move")
    while True:
        string_move = input("> ")
        if len(string_move) != 2:
            print("Invalid input [e.g. 21 plays at row 2 column 1]")
            continue
        try:
            row = int(string_move[0]) - 1 # to 0 index
            col = int(string_move[1]) - 1
        except:
            print("Invalid input [e.g. 21 plays at row 2 column 1]")
            continue
        if row >= D or col >= D or row < 0 or col < 0:
            print("Invalid square [e.g. 21 plays at row 2 column 1]")
            continue

        if currentBoard[row][col] != EMPTY:
            print("That square is already played")
            continue

        return row, col # back to zero-index

nPlays = 0

toPlay = EX
done = False
winner = STILLGOING
while not done:
    printBoard(currentBoard)
    move = getMove(toPlay)
    if move == RESIGN:
        winner = otherPlayer(toPlay)
    else:
        i,j = move
        assert currentBoard[i][j] == EMPTY
        currentBoard[i][j] = toPlay
        nPlays += 1

    if nPlays >= 5:
        winner = checkForWin(currentBoard, i,j)
        assert winner == checkForWinFull(currentBoard)

    if winner != STILLGOING:
        done = True
        if winner == EX:
            print("---> X wins!")
        elif winner == OH:
            print("---> O wins!")
        elif winner == DRAW:
            print("---> Draw.")

    toPlay = otherPlayer(toPlay)

printBoard(currentBoard)


