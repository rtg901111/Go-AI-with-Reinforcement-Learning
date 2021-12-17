from copy import deepcopy

import read_write

best_moves = [(2,2), (1,1), (1,3), (3,1), (3,3), (2,1), (1,2), (2,3), (3, 2)]
   
#IMPORTANT:
#This Class GO has been referenced from the given host.py file. 
  
class GO:
    def __init__(self, n):
        self.size = n

        self.died_pieces = [] 
        self.n_move = 0 
        self.max_move = n * n - 1 
        self.komi = n/2 

    def init_board(self, n):
        board = [[0 for x in range(n)] for y in range(n)]  
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        self.previous_board = previous_board
        self.board = board

    def compare_board(self, x, y):
        for i in range(self.size):
            for j in range(self.size):
                if x[i][j] != y[i][j]:
                    return False
        return True

    def copy_board(self):
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        board = self.board
        neighbors = []
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        board = self.board
        neighbors = self.detect_neighbor(i, j)  
        group_allies = []
        
        for piece in neighbors:
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        
        stack = [(i, j)]  
        ally_members = []  
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                
                if board[piece[0]][piece[1]] == 0:
                    return True
       
        return False

    def find_died_pieces(self, piece_type):
       
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                
                if board[i][j] == piece_type:
                   
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        
        return True

    def valid_place_check(self, i, j, piece_type):
       
        board = self.board
 
        if not (i >= 0 and i < len(board)):          
            return False
        if not (j >= 0 and j < len(board)): 
            return False
        
        if board[i][j] != 0:    
            return False
        
        test_go = self.copy_board()
        test_board = test_go.board

        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            
            return False

        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                return False
        return True
         
    def update_board(self, new_board):
       
        self.board = new_board

    def game_end(self, piece_type, action="MOVE"):
        
        if self.n_move >= self.max_move:
            return True

        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt          

def return_valid_moves(go, piece_type):
    
    possible_moves = []
    for i in range(go.size):
        for j in range(go.size):
            if go.valid_place_check(i, j, piece_type):
                possible_moves.append((i,j))

    if possible_moves == []:
        return "PASS"
    return possible_moves
 
def minimax(possible_moves, go, depth, alpha, beta, maximizing_player, piece_type):
    if depth == 0 or go.game_end(piece_type) == True:
        
        return go.score(piece_type) - go.score(3 - piece_type), 'Dummy'
        

    if possible_moves == 'PASS': #When opponent moves are None
        return go.score(3 - piece_type) - go.score(piece_type), 'Dummy2'

    if maximizing_player == True:
        max_score_diff = -999999999999
        for move in possible_moves:
            test_go = go.copy_board()
            test_board = test_go.board

            test_go.place_chess(move[0], move[1], piece_type)
            test_go.died_pieces = test_go.remove_died_pieces(3 - piece_type)
            test_go.n_move += 1
 
            #Child
            child_possible_moves = return_valid_moves(test_go, 3 - piece_type)
            score_diff, _ = minimax(child_possible_moves, test_go, depth - 1, alpha, beta, False, 3 - piece_type)

            if score_diff > max_score_diff:
                max_score_diff = score_diff
                return_move = move

            #max_score_diff = max(max_score_diff, score_diff)
            
            #alpha = max(alpha, max_score_diff)
            #if beta <= alpha:
            #    break

        return max_score_diff, return_move

    else:
        min_score_diff = 999999999999
        for move in possible_moves:
            test_go = go.copy_board()
            test_board = test_go.board

            test_go.place_chess(move[0], move[1], piece_type)
            test_go.died_pieces = test_go.remove_died_pieces(3 - piece_type)
            test_go.n_move += 1

            #Child
            child_possible_moves = return_valid_moves(test_go, 3 - piece_type)
            score_diff, _ = minimax(child_possible_moves, test_go, depth - 1, alpha, beta, True, 3 - piece_type)

            if score_diff < min_score_diff:
                min_score_diff = score_diff
                return_move = move

            #min_score_diff = min(min_score_diff, score_diff)
            
            #beta = min(beta, min_score_diff)
            #if beta <= alpha:
            #    break
        
        return min_score_diff, return_move


def main(go, piece_type, n):  
   
    depth = 2 
    
    if piece_type == 1: #If black
        limit = 5
    elif piece_type == 2: #If white
        limit = 3
    
    maximizing_player = True
    
    alpha = -9999999
    beta = 9999999
  
    #My turn        
    
    possible_moves = []
    for move in best_moves:
        is_valid = go.valid_place_check(move[0], move[1], piece_type)
        if is_valid == True:
            possible_moves.append(move)
    
    if possible_moves != [] and len(possible_moves) > limit:
        
        _, my_action = minimax(possible_moves, go, depth, alpha, beta, maximizing_player, piece_type)
        go.place_chess(my_action[0], my_action[1], piece_type)
        go.died_pieces = go.remove_died_pieces(3 - piece_type)
        go.n_move += 1
    #No best moves
    else:
        #possible_moves = return_valid_moves(go, piece_type)
        #if piece_type == 1 and len(possible_moves) < 3: #Only when I'm black and best moves < 3 are available. 
        #    possible_moves = return_valid_moves(go, piece_type)
        #else:
        possible_moves = possible_moves + return_valid_moves(go, piece_type)
            
        if possible_moves != 'PASS':
            #my_action = random.choice(possible_moves)
            _, my_action = minimax(possible_moves, go, depth, alpha, beta, maximizing_player, piece_type)
            go.place_chess(my_action[0], my_action[1], piece_type)
            go.died_pieces = go.remove_died_pieces(3 - piece_type)
            go.n_move += 1
        else:
            my_action = 'PASS'
            go.previous_board = deepcopy(go.board)
            go.n_move += 1
    
    return my_action
 
if __name__ == '__main__':
     
    piece_type, prev_board, current_board, n = read_write.read_input('input.txt')
    N = 5
    go = GO(N)
    
    go.init_board(N)
    go.previous_board = prev_board
    go.board = current_board
    go.n_move = n
    go.died_pieces = go.remove_died_pieces(3 - piece_type)

    my_action = main(go, piece_type, n)
 
    read_write.write_output('output.txt', my_action)

