import sys
import random
import timeit
import math
import argparse
from collections import Counter
from copy import deepcopy

import numpy as np
    
import json

REWARD = [[-1, 0, 0, 0, -1],
          [0, 2, 2, 2, 0],
          [0, 2, 4, 2, 0],
          [0, 2, 2, 2, 0],
          [-1, 0, 0, 0, -1]]

class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        #self.previous_board = None # Store the previous board
        self.X_move = True # X chess plays first
        self.died_pieces = [] # Intialize died pieces to be empty
        self.n_move = 0 # Trace the number of moves
        self.max_move = n * n - 1 # The max movement of a Go game
        self.komi = n/2 # Komi rule
        self.verbose = False # Verbose only when there is a manual player

    def init_board(self, n):
        '''
        Initialize a board with size n*n.

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)] for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_died_pieces(self, piece_type):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''   
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False
        
        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False
        
        # Copy the board for testing
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True
        
    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''   
        self.board = new_board

    def visualize_board(self):
        '''
        Visualize the board.

        :return: None
        '''
        board = self.board

        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)

    def game_end(self, piece_type, action="MOVE"):
        '''
        Check if the game should end.

        :param piece_type: 1('X') or 2('O').
        :param action: "MOVE" or "PASS".
        :return: boolean indicating whether the game should end.
        '''

        # Case 1: max move reached
        if self.n_move >= self.max_move:
            return True
        # Case 2: two players all pass the move.
        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):
        '''
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt          

    def judge_winner(self):
        '''
        Judge the winner of the game by number of pieces for each player.

        :param: None.
        :return: piece type of winner of the game (0 if it's a tie).
        '''        

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi: return 1
        elif cnt_1 < cnt_2 + self.komi: return 2
        else: return 0
        
    def play(self, player1, player2, verbose=False):
        '''
        The game starts!

        :param player1: Player instance.
        :param player2: Player instance.
        :param verbose: whether print input hint and error information
        :return: piece type of winner of the game (0 if it's a tie).
        '''
        self.init_board(self.size)
        # Print input hints and error message if there is a manual player
        if player1.type == 'manual' or player2.type == 'manual':
            self.verbose = True
            print('----------Input "exit" to exit the program----------')
            print('X stands for black chess, O stands for white chess.')
            self.visualize_board()
        
        verbose = self.verbose
        # Game starts!
        while 1:
            piece_type = 1 if self.X_move else 2

            # Judge if the game should end
            if self.game_end(piece_type):       
                result = self.judge_winner()
                if verbose:
                    print('Game ended.')
                    if result == 0: 
                        print('The game is a tie.')
                    else: 
                        print('The winner is {}'.format('X' if result == 1 else 'O'))
                return result

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(player + " makes move...")

            # Game continues
            if piece_type == 1: action = player1.get_input(self, piece_type)
            else: action = player2.get_input(self, piece_type)

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(action)

            if action != "PASS":
                # If invalid input, continue the loop. Else it places a chess on the board.
                if not self.place_chess(action[0], action[1], piece_type):
                    if verbose:
                        self.visualize_board() 
                    continue

                self.died_pieces = self.remove_died_pieces(3 - piece_type) # Remove the dead pieces of opponent
            else:
                self.previous_board = deepcopy(self.board)

            if verbose:
                self.visualize_board() # Visualize the board again
                print()

            self.n_move += 1
            self.X_move = not self.X_move # Players take turn

class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''        
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

def return_valid_moves(go, piece_type):
    possible_placements = []
    for i in range(go.size):
        for j in range(go.size):
            if go.valid_place_check(i, j, piece_type, test_check = True):
                possible_placements.append((i,j))

    if not possible_placements:
        return "PASS"
    return possible_placements

def train(piece_type, epsilon, alpha, gamma, q_table, result_dict, learn):
    #Piece_type : My piece type; 1 = black; 2 = white

    N = 5
    go = GO(N)
    go.init_board(N)
    #Board initialized

    #Open and read the Q_table json file

    opponent_random = RandomPlayer()

    if piece_type == 1:
        my_piece_type = 1
        opponent_piece_type = 2
    else:
        my_piece_type = 2
        opponent_piece_type = 1

    is_first = True
    
    while go.game_end(my_piece_type) != True:

        #When I play White and get the first move from opponent
        if is_first == True and my_piece_type == 2:
            opponent_move = opponent_random.get_input(go, opponent_piece_type)
            go.place_chess(opponent_move[0], opponent_move[1], opponent_piece_type)
            go.remove_died_pieces(3 - opponent_piece_type)
            go.n_move += 1
            is_first = False
        
        #Now I make a move
        prev_score_diff = go.score(my_piece_type) - go.score(opponent_piece_type)
        my_turn_board = deepcopy(go.board)

        if str(go.board) not in q_table:
            possible_moves = return_valid_moves(go, my_piece_type)
            if possible_moves != 'PASS':
                q_table[str(go.board)] = dict()
                for move in possible_moves:
                    q_table[str(go.board)][str(move)] = 0
                my_action = str(random.choice(possible_moves))

            else:
                my_action = 'PASS'
        
        else:
            if random.uniform(0, 1) < epsilon:
                my_action = random.choice(list(q_table[str(go.board)].keys()))
            else:
                my_action = max(q_table[str(go.board)], key = q_table[str(go.board)].get)

            #epsilon = epsilon * 1.04
        
        if my_action != 'PASS':
            go.place_chess(int(my_action[1]), int(my_action[4]), my_piece_type)
            go.died_pieces = go.remove_died_pieces(3 - my_piece_type)
            go.n_move += 1
        
        else:
            go.previous_board = deepcopy(go.board)
            go.n_move += 1

        #go.visualize_board()
        
        after_score_diff = go.score(my_piece_type) - go.score(opponent_piece_type)
        #Check if the game ended
        if go.game_end(opponent_piece_type) == True:
            break

        #Now opponent make a move
        opponent_move = opponent_random.get_input(go, opponent_piece_type)
        if opponent_move != 'PASS':
            go.place_chess(opponent_move[0], opponent_move[1], opponent_piece_type)
            go.died_pieces = go.remove_died_pieces(3 - opponent_piece_type)
            go.n_move += 1
        
        else:
            go.previous_board = deepcopy(go.board)
            go.n_move += 1
        
        #go.visualize_board()

        #Both players passed so game ends
        if my_action == 'PASS' and opponent_move == 'PASS':
            break

        #Update the q_value
        if learn == True:
            if my_action != 'PASS':
                if str(go.board) in q_table:
                    #q_max_next_state = max(q_table[str(go.board)], key = q_table[str(go.board)].get)
                    q_max_next_state = max(list(q_table[str(go.board)].values()))
                else:
                    q_max_next_state = 0 
                score_diff = after_score_diff - prev_score_diff
                if score_diff != 0:
                    score_diff = score_diff * 2
                #my_reward = REWARD[int(my_action[1])][int(my_action[4])] + (after_score_diff - prev_score_diff)
                my_reward = REWARD[int(my_action[1])][int(my_action[4])] + score_diff             
                q_table[str(my_turn_board)][my_action] =  ((1-alpha) * q_table[str(my_turn_board)][my_action]) + alpha * (my_reward + (gamma * q_max_next_state))
 
    #The game ended
    #print('Player 1 score:', str(go.score(my_piece_type)), '\n', 'Player 2 score:', str(go.score(opponent_piece_type) + go.komi))
    #print('Player', str(go.judge_winner()), 'has won!')
    if go.judge_winner() == 1:
        result_dict['black'] += 1
    elif go.judge_winner() == 2:
        result_dict['white'] += 1
    else:
        result_dict['draw'] += 1

    return q_table, result_dict

def main():
    my_piece_type = 1 #black = 1; white = 2
    alpha = 0.1
    gamma = 0.99
    epsilon = 0.8
    max_exp_rate = 0.8
    min_exp_rate = 0.01
    exp_decay_rate = 0.000025#0.000004 
    result_dict = {'black': 0, 'white': 0, 'draw': 0}

    learn = True
    # Black Training
    black_file_name = 'q_table_black.json'
    black_q_file = open(black_file_name, 'r')
    black_q_table = json.load(black_q_file)
    black_q_file.close() 

    i = 0
    while i < 100000:#800000:
        black_q_table, result_dict = train(my_piece_type, epsilon, alpha, gamma, black_q_table, result_dict, learn)
        #epsilon = epsilon * 1.00065
        i += 1
        if learn == True:
            epsilon = min_exp_rate + (max_exp_rate - min_exp_rate) * np.exp(-exp_decay_rate * i)
        if i % 10000 == 0:
            print('Game result from', str(i-10000), 'to', str(i) + ": Black won", str(result_dict['black']), 'White won', str(result_dict['white']), 'draw =', str(result_dict['draw']))

    if learn == True:
        updated_q_file = open(black_file_name, 'w')
        json.dump(black_q_table, updated_q_file)
        updated_q_file.close()

    # White Training 
    my_piece_type = 2
    epsilon = 0.8
    result_dict = {'black': 0, 'white': 0, 'draw': 0}
    white_file_name = 'q_table_white.json'
    white_q_file = open(white_file_name, 'r')
    white_q_table = json.load(white_q_file)
    white_q_file.close()

    i = 0
    while i < 100000:#800000:
        white_q_table, result_dict = train(my_piece_type, epsilon, alpha, gamma, white_q_table, result_dict, learn)
        #epsilon = epsilon * 1.00065
        i += 1
        if learn == True:
            epsilon = min_exp_rate + (max_exp_rate - min_exp_rate) * np.exp(-exp_decay_rate * i)
        if i % 10000 == 0:
            print('Game result from', str(i-10000), 'to', str(i) + ": Black won", str(result_dict['black']), 'White won', str(result_dict['white']), 'draw =', str(result_dict['draw']))

    if learn == True:
        updated_q_file = open(white_file_name, 'w')
        json.dump(white_q_table, updated_q_file)
        updated_q_file.close()
 

if __name__ == '__main__':
    main()






    














