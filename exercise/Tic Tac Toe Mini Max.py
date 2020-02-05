"""
Mini-max Tic-Tac-Toe Player
"""

import poc_ttt_gui
import poc_ttt_provided as provided

# Set timeout, as mini-max can take a long time
import codeskulptor
codeskulptor.set_timeout(60)

# SCORING VALUES - DO NOT MODIFY
SCORES = {provided.PLAYERX: 1,
          provided.DRAW: 0,
          provided.PLAYERO: -1}

def mm_move(board, player):
    """
    Make a move on the board.
    
    Returns a tuple with two elements.  The first element is the score
    of the given board and the second element is the desired move as a
    tuple, (row, col).
    """
    # base case
    if board.check_win() != None:
        return SCORES[board.check_win()], (-1, -1)
        
    # recursive case
    score_list = []
    move_list = []
    for square in board.get_empty_squares():
        child = board.clone()
        child.move(square[0], square[1], player)
        score = mm_move(child, provided.switch_player(player))[0]
        score_list.append(score)
        move_list.append(square)
        if player == provided.PLAYERX and score == 1:
            break
        elif player == provided.PLAYERO and score == -1:
            break

    if player == provided.PLAYERX:
        best_score = max(score_list)
    else:
        best_score = min(score_list)
        
    best_move = move_list[score_list.index(best_score)]

    return best_score, best_move
    

def move_wrapper(board, player, trials):
    """
    Wrapper to allow the use of the same infrastructure that was used
    for Monte Carlo Tic-Tac-Toe.
    """
    move = mm_move(board, player)
    assert move[1] != (-1, -1), "returned illegal move (-1, -1)"
    return move[1]

# provided.play_game(move_wrapper, 1, False)        
# poc_ttt_gui.run_gui(3, provided.PLAYERO, move_wrapper, 1, False)
