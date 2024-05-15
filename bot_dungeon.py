import numpy as np
import copy
import random

class node:
    def __init__(self, board_dict: dict, move_made):
        self.board_dict = board_dict
        self.children = []
        self.score = 0
        self.move_made = move_made
    
    def add_child(self, child):
        self.children.append(child)

class bot_dungeon:
    ''' 
    demonstrates the two minimal functions for an agent
    '''
    def __init__(self, name: str = 'bot_template'):
        self.name = name
        self.current_game_score = 0
        self.max_depth = 3
        
    def move(self, board_dict: dict) -> tuple:
        '''
        the keywords for board_dict are:
        board_state: a 9x9 np.array showing which squares have which markers.
                     your markers at +1 and your opponent markers are -1.
                     open squares are 0
        active_box:  the coordinate for the active mini-board (indicates which 3x3 is currently playable)
                     a value of (-1, -1) is used if the whole board is valid
        valid_moves: a list of tuples indicating which positions are valid (in the 9x9 format)
        '''
        self.current_game_score = self.count_cells_won(self.get_major_board_won_cells(board_dict))

        game_state_tree = self.create_tree(board_dict)
        self.minimax(game_state_tree, True)
        best_move = self.get_best_move(game_state_tree)
        return best_move





    # ===================================================================
    # ======================= Mini Max Algo =============================
    # ===================================================================
  
    def minimax(self, noot, maximizing_player): 
        # Compute scoring for the current node
        if len(noot.children) == 0:
            return self.eval_gamestate(noot.board_dict)
        
        scores = []
        
        for node in noot.children:
            scores.append(self.minimax(node, not maximizing_player))
            
        score = max(scores) if maximizing_player else min(scores)
        noot.score = score
        return score

    # ===================================================================
    # ======================= Eval Gamestate ============================
    # ===================================================================

    def eval_gamestate(self, board_dict: dict):
        """
        Evaluates the gamestate
        """
        
        major_board = self.get_major_board_won_cells(board_dict)
        winner = self.check_winner(major_board)
        if winner == 1:
            return 100000
        elif winner == -1:
            return -100000

        score = self.count_cells_won(major_board, multiplier=2)
        
        # Check if overall score is better than current score
        if score > self.current_game_score:
            return score
        
        # Check if the player is almost winning
        almost_won = self.count_almost_won(board_dict)
        score += almost_won[0] * 1
        score -= almost_won[1] * 1
        if score > self.current_game_score:
            return score
        
        return random.randint(-10, 10)
    
    def get_best_move(self, noot):
        best_score = -10000
        best_move = None
        for child in noot.children:
            if child.score > best_score:
                best_score = child.score
                best_move = child.move_made
        return best_move
    
    def count_cells_won(self, board: dict, multiplier: int = 1):
        """
        Counts the number of cells won by each player
        """
        cells_won = 0
        for row in board:
            cells_won += row.count(1) * multiplier
            cells_won -= row.count(-1) * multiplier
        return cells_won


    def get_major_board_won_cells(self, board_dict: dict):
        """
        Returns the cells that have been won in the major board
        """
        major_board = [[j for j in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                mini_board = self.get_miniboard_from_xy(board_dict["board_state"], (i, j))
                major_board[i][j] = self.check_winner(mini_board)
        return major_board

    def check_winner(board):
        # Check rows
        for row in board:
            if row.count(1) == 3:
                return 1
            elif row.count(-1) == 3:
                return -1

        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] == 1:
                return 1
            elif board[0][col] == board[1][col] == board[2][col] == -1:
                return -1

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] == 1 or board[0][2] == board[1][1] == board[2][0] == 1:
            return 1
        elif board[0][0] == board[1][1] == board[2][2] == -1 or board[0][2] == board[1][1] == board[2][0] == -1:
            return -1
        
        # If no winner yet
        return 0
        

    def count_almost_won(self, board_dict):
        """
        Counts the number of cells that are almost won by a player
        """
        almost_won = [0,0]
        for i in range(3):
            for j in range(3):
                mini_board = self.get_miniboard_from_xy(board_dict["board_state"], (i, j))
                almost_won[0] = 1 if self.almost_won(mini_board, 1) else 0
                almost_won[1] = 1 if self.almost_won(mini_board, -1) else 0
        
        return almost_won
            
        

    
    def almost_won(board, player):
        # Check rows
        for row in board:
            if row.count(player) == 2 and row.count(0) == 1:
                return True
        
        # Check columns
        for col in range(3):
            if [board[row][col] for row in range(3)].count(player) == 2 and [board[row][col] for row in range(3)].count(0) == 1:
                return True
        
        # Check diagonals
        if [board[i][i] for i in range(3)].count(player) == 2 and [board[i][i] for i in range(3)].count(0) == 1:
            return True
        if [board[i][2-i] for i in range(3)].count(player) == 2 and [board[i][2-i] for i in range(3)].count(0) == 1:
            return True
        
        return False

        

    # ===================================================================
    # ==========================CREATE TREE==============================
    # ===================================================================
            
    # Begin creating the tree
    def create_tree(self, board_dict: dict):
        noot = node(board_dict)
        game_state_tree = self.recursive_create_tree(noot, 0, self.max_depth, betterPlayer=True)
        return game_state_tree

    def recursive_create_tree(self, parent, cur_depth: int = 0, max_depth: int = 1, betterPlayer: bool = True):
        # Base case - If we have reached the max depth, kill it.
        if cur_depth == max_depth:
            return None
        
        # Iterate through the valid moves creating new game states
        for move in parent.board_dict["valid_moves"]:
            nnode = node(board_dict=parent.board_dict, move_made = move)
            nnode.board_dict = self.pseudo_move(nnode.board_dict, move_played=move, player=1 if betterPlayer else -1)
            self.recursive_create_tree(nnode, cur_depth + 1, max_depth,  betterPlayer = not betterPlayer)
            parent.add_child(nnode)

        return None

    # ===================================================================
    # ===================================================================
    # ===================================================================
 

    def pseudo_move(self, board_dict: dict, move_played, player: int):
        """
        Pretends to make a move
        """
        new_board_dict = copy.deepcopy(board_dict)
        new_board_dict["board_state"][move_played[0]][move_played[1]] = player
        self.update_valid_moves(new_board_dict, move_played)

        return new_board_dict
    
    def update_valid_moves(self, board_dict: dict, move_played):
        """
        Updates the valid move
        """
        '''
        the keywords for board_dict are:
        board_state: a 9x9 np.array showing which squares have which markers.
                     your markers at +1 and your opponent markers are -1.
                     open squares are 0
        active_box:  the coordinate for the active mini-board (indicates which 3x3 is currently playable)
                     a value of (-1, -1) is used if the whole board is valid
        valid_moves: a list of tuples indicating which positions are valid (in the 9x9 format)
        '''
        mini_board_index = (move_played[0] // 3, move_played[1] // 3)
        mini_board = self.get_miniboard_from_xy(board_dict["board_state"], mini_board_index)
        is_complete = self.is_mini_board_complete(mini_board)
        if (is_complete):
            board_dict["active_box"] = (-1, -1)
            board_dict["valid_moves"] = self.create_valid_moves_major(board_dict)
        else:
            board_dict["active_box"] = mini_board_index
            board_dict["valid_moves"] = self.create_valid_moves_mini(board_dict, mini_board_index)

    def create_valid_moves_major(self, board_dict):
        '''What valid moves are available if the mini board we go to is complete'''
        valid_moves = []
        for column in range(9):
            for row in range(9):
                if (board_dict["board_state"][column][row] == 0):
                    valid_moves.append((column, row))
        return valid_moves                

    def create_valid_moves_mini(self, board_dict, mini_board_index):
        '''What valid moves are available if the mini board we go to is not complete'''
        valid_moves = []
        for column in range(3):
            for row in range(3):
                actual_column = column + 3*mini_board_index[0]
                actual_row = row + 3*mini_board_index[1]
                if (board_dict["board_state"][actual_column][actual_row] == 0):
                    valid_moves.append((actual_column, actual_row))
        return valid_moves
            
    def get_miniboard_from_xy(self, board_state:list, miniboard_index:tuple)->list:
        x=miniboard_index[0]
        y=miniboard_index[1]
        
        assert(x>=0 and (x+1)*3<=9)
        assert(y>=0 and (y+1)*3<=9)
        
        return board_state[x*3:(x+1)*3,
                           y*3:(y+1)*3]
    
    
    def is_mini_board_complete(self, mini_board:list)->bool:
        # DRAW: sum( sum(abs()) := [] ) := 9
        # do this FIRST as draws are more likely
        if sum(sum(abs(mini_board)))==9:
            return True
        
        data = copy.deepcopy(mini_board)
        datarot=np.rot90(data)
        sumdata=sum(data)
        sumdatarot=sum(datarot)

        # if there exists a row or column with all 3 or -3.
        if 3 in sumdata or 3 in sumdatarot:
            return True
        if -3 in sumdata or -3 in sumdatarot:
            return True

        # check diagonals
        d1trace=data.trace()
        d2trace=datarot.trace()
        if d1trace == 3 or d1trace == -3:
            return True
        if d2trace == 3 or d2trace == -3:
            return True
            
        return False












