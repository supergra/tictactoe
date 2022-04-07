# tictactoe
Play Tic-Tac-Toe against a computer

## Approach
Rate each possible A move:

- LOSS: *some* possible B response can guarantee a B win
- DRAW: *some* possible B response can guarantee a draw
- WIN:  for *all* possible B responses, there is a guaranteed A win

play WIN else DRAW else LOSS

To compute this:
```
foreach B response:
    Rate each as:
        LOSS:
        DRAW:
        WIN:
    play WIN else DRAW else LOSS


bestPlay(toMove, board):
    moveDict = {}
    foreach validMove:
        make move
        if GAMEOVER:
            # End of recursion!
            evaluation = WIN/LOSS/DRAW
        else:
            response, evaluation = bestPlay(enemy, newBoard)


        moveDict[move] = !evaluation # swap win/loss, keep draw

        undo move

    if any evaluation == WIN:
        return that move, WIN
    elif any evaluation == DRAW:
        return that move, DRAW
    else:
        return any move, LOSS [or resign]
```
