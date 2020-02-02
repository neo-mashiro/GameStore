"""
Monte Carlo Tic-Tac-Toe Player
"""

import random
import poc_ttt_gui
import poc_ttt_provided as provided

# http://www.codeskulptor.org/#poc_ttt_gui.py
# http://www.codeskulptor.org/#poc_ttt_provided.py

NTRIALS = 10      # Number of trials to run
SCORE_CURRENT = 1.0 # Score for squares played by the current player
SCORE_OTHER = 1.0   # Score for squares played by the other player
    
def mc_trial(board, player):
    """
    simulate 1 trial of game on the board and update the board status
    """
    while board.check_win() == None:
        empty_squares = board.get_empty_squares()
        random_square = random.choice(empty_squares)
        board.move(random_square[0], random_square[1], player)
        player = provided.switch_player(player)
    
def mc_update_scores(scores, board, player):
    """
    updates scores based on the score grid of the board
    """
    if board.check_win() == provided.DRAW:
        return None
                    
    for row in range(board.get_dim()):
        for col in range(board.get_dim()):
            if board.square(row, col) == player:
                if board.check_win() == player:
                    scores[row][col] += SCORE_CURRENT
                else:
                    scores[row][col] -= SCORE_CURRENT
            elif board.square(row, col) == provided.switch_player(player):
                if board.check_win() == provided.switch_player(player):
                    scores[row][col] += SCORE_OTHER
                else:
                    scores[row][col] -= SCORE_OTHER

def get_best_move(board, scores):
    """
    returns the best move tuple (row, col) that has the highest score in scores
    """
    max_squares = []
    empty_squares = board.get_empty_squares()
    
    # find max score
    max_score = -999
    for square in empty_squares:
        if scores[square[0]][square[1]] >= max_score:
            max_score = scores[square[0]][square[1]]
            
    # find empty squares with max scores
    for square in empty_squares:
        if scores[square[0]][square[1]] == max_score:
            max_squares.append((square[0], square[1]))
            
    return random.choice(max_squares)
    
def mc_move(board, player, trials):
    """
    make a best move based on Monto Carlo simulation
    """
    scores = [[0 for row in range(board.get_dim())]
                 for col in range(board.get_dim())
             ]
    for _ in range(NTRIALS):
        sim_board = board.clone()
        mc_trial(sim_board, player)
        mc_update_scores(scores, sim_board, player)
        
    return get_best_move(board, scores)


# provided.play_game(mc_move, NTRIALS, False)        
# poc_ttt_gui.run_gui(3, provided.PLAYERX, mc_move, NTRIALS, False)

