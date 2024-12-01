import tkinter as tk
from tkinter import messagebox
import random

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chess Game")
        
        # Board representation: None for empty, (color, piece) for pieces
        self.board = self.initialize_board()
        self.selected_piece = None
        self.is_player_turn = True  # True for player (white), False for bot (black)
        
        self.squares = []
        self.create_board()
        
        self.last_move = None  # For en passant
        self.castling_rights = {
            'white': {'kingside': True, 'queenside': True},
            'black': {'kingside': True, 'queenside': True}
        }
        
        self.window.mainloop()
    
    def initialize_board(self):
        # Initialize 8x8 board
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Set up pieces
        # Black pieces (bot)
        piece_order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for col in range(8):
            board[0][col] = ('black', piece_order[col])
            board[1][col] = ('black', 'P')
            
        # White pieces (player)
        for col in range(8):
            board[6][col] = ('white', 'P')
            board[7][col] = ('white', piece_order[col])
            
        return board
    
    def create_board(self):
        colors = ['white', 'gray']
        
        for row in range(8):
            row_squares = []
            for col in range(8):
                color = colors[(row + col) % 2]
                square = tk.Button(self.window, bg=color, width=5, height=2,
                                 command=lambda r=row, c=col: self.square_clicked(r, c))
                square.grid(row=row, column=col)
                row_squares.append(square)
            self.squares.append(row_squares)
        
        self.update_display()
    
    def update_display(self):
        piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    color, piece_type = piece
                    symbol = piece_symbols[piece_type.upper() if color == 'white' else piece_type.lower()]
                    self.squares[row][col].config(text=symbol)
                else:
                    self.squares[row][col].config(text='')
    
    def square_clicked(self, row, col):
        if not self.is_player_turn:
            return
            
        current_piece = self.board[row][col]
        
        if self.selected_piece:
            old_row, old_col = self.selected_piece
            if self.is_valid_move(old_row, old_col, row, col):
                self.make_move(old_row, old_col, row, col)
                self.selected_piece = None
                self.update_display()
                
                if not self.check_game_over():
                    self.is_player_turn = False
                    self.window.after(500, self.make_bot_move)
            else:
                self.selected_piece = None
        elif current_piece and current_piece[0] == 'white':
            self.selected_piece = (row, col)
    
    def is_valid_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        color, piece_type = piece
        
        # Can't capture your own pieces
        target = self.board[to_row][to_col]
        if target and target[0] == piece[0]:
            return False
        
        # Check basic move validity based on piece type
        valid_move = False
        if piece_type == 'P':
            valid_move = self.is_valid_pawn_move(from_row, from_col, to_row, to_col, color)
        elif piece_type == 'R':
            valid_move = self.is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'N':
            valid_move = self.is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'B':
            valid_move = self.is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'Q':
            valid_move = self.is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'K':
            valid_move = self.is_valid_king_move(from_row, from_col, to_row, to_col)
        
        if not valid_move:
            return False
        
        # Make temporary move to check if it puts own king in check
        temp_board = [row[:] for row in self.board]
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        # Find king position
        king_row, king_col = None, None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == color and piece[1] == 'K':
                    king_row, king_col = row, col
                    break
            if king_row is not None:
                break
        
        # Check if king is under attack
        in_check = False
        if king_row is not None:
            opponent = 'black' if color == 'white' else 'white'
            for row in range(8):
                for col in range(8):
                    piece = self.board[row][col]
                    if piece and piece[0] == opponent:
                        if self.is_basic_move_valid(row, col, king_row, king_col, piece[1]):
                            in_check = True
                            break
                if in_check:
                    break
        
        # Restore board
        self.board = temp_board
        
        return not in_check
    
    def is_basic_move_valid(self, from_row, from_col, to_row, to_col, piece_type):
        """Check if a move is valid without considering check"""
        if piece_type == 'P':
            color = self.board[from_row][from_col][0]
            return self.is_valid_pawn_move(from_row, from_col, to_row, to_col, color)
        elif piece_type == 'R':
            return self.is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'N':
            return self.is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'B':
            return self.is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'Q':
            return self.is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'K':
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        return False
    
    def is_valid_pawn_move(self, from_row, from_col, to_row, to_col, color):
        direction = 1 if color == 'black' else -1
        start_row = 1 if color == 'black' else 6
        
        # Basic one square move
        if from_col == to_col and to_row == from_row + direction:
            return self.board[to_row][to_col] is None
        
        # Initial two square move
        if from_row == start_row and from_col == to_col and to_row == from_row + 2 * direction:
            return (self.board[to_row][to_col] is None and 
                    self.board[from_row + direction][from_col] is None)
        
        # Capture moves
        if to_row == from_row + direction and abs(to_col - from_col) == 1:
            return self.board[to_row][to_col] is not None
        
        # En passant
        if self.last_move:
            last_from_row, last_from_col, last_to_row, last_to_col, last_piece = self.last_move
            if (last_piece[1] == 'P' and  # Last move was a pawn
                abs(last_from_row - last_to_row) == 2 and  # Moved two squares
                last_to_row == from_row and  # Same row as current pawn
                abs(last_to_col - from_col) == 1 and  # Adjacent column
                to_row == from_row + direction and  # Moving diagonally
                to_col == last_to_col):  # To the column of the passed pawn
                return True
        return False
    
    def is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        # Rook moves horizontally or vertically
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check if path is clear
        row_step = 0 if from_row == to_row else (to_row - from_row) // abs(to_row - from_row)
        col_step = 0 if from_col == to_col else (to_col - from_col) // abs(to_col - from_col)
        
        current_row, current_col = from_row + row_step, from_col + col_step
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        # Bishop moves diagonally
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        # Check if path is clear
        row_step = (to_row - from_row) // abs(to_row - from_row)
        col_step = (to_col - from_col) // abs(to_col - from_col)
        
        current_row, current_col = from_row + row_step, from_col + col_step
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def is_valid_queen_move(self, from_row, from_col, to_row, to_col):
        # Queen can move like a rook or bishop
        return (self.is_valid_rook_move(from_row, from_col, to_row, to_col) or
                self.is_valid_bishop_move(from_row, from_col, to_row, to_col))
    
    def is_valid_king_move(self, from_row, from_col, to_row, to_col):
        color = self.board[from_row][from_col][0]
        
        # Normal king move
        if abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1:
            return True
            
        # Castling
        if from_row == to_row and abs(to_col - from_col) == 2:
            if self.is_in_check(color):
                return False
                
            # Kingside castling
            if to_col > from_col and self.castling_rights[color]['kingside']:
                if all(self.board[from_row][col] is None for col in range(from_col + 1, 7)):
                    return not any(self.is_square_attacked(from_row, col, color) 
                                 for col in range(from_col, from_col + 3))
                                 
            # Queenside castling
            elif to_col < from_col and self.castling_rights[color]['queenside']:
                if all(self.board[from_row][col] is None for col in range(1, from_col)):
                    return not any(self.is_square_attacked(from_row, col, color) 
                                 for col in range(from_col - 2, from_col + 1))
        return False
    
    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        color, piece_type = piece
        
        # Store last move for en passant
        self.last_move = (from_row, from_col, to_row, to_col, piece)
        
        # Handle castling
        if piece_type == 'K' and abs(to_col - from_col) == 2:
            # Move rook for castling
            if to_col > from_col:  # Kingside
                self.board[to_row][to_col-1] = self.board[to_row][7]
                self.board[to_row][7] = None
            else:  # Queenside
                self.board[to_row][to_col+1] = self.board[to_row][0]
                self.board[to_row][0] = None
        
        # Update castling rights
        if piece_type == 'K':
            self.castling_rights[color]['kingside'] = False
            self.castling_rights[color]['queenside'] = False
        elif piece_type == 'R':
            if from_col == 0:  # Queenside rook
                self.castling_rights[color]['queenside'] = False
            elif from_col == 7:  # Kingside rook
                self.castling_rights[color]['kingside'] = False
        
        # Handle en passant capture
        if piece_type == 'P' and abs(from_col - to_col) == 1 and self.board[to_row][to_col] is None:
            self.board[from_row][to_col] = None  # Remove captured pawn
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Handle pawn promotion
        if piece_type == 'P' and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = (color, 'Q')  # Auto-promote to queen
    
    def make_bot_move(self):
        # Get all possible moves for black pieces
        possible_moves = []
        for row in range(8):
            for col in range(8):
                if self.board[row][col] and self.board[row][col][0] == 'black':
                    # For simplicity, consider all squares as possible destinations
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(row, col, to_row, to_col):
                                possible_moves.append((row, col, to_row, to_col))
        
        if possible_moves:
            # Make a random move
            from_row, from_col, to_row, to_col = random.choice(possible_moves)
            self.make_move(from_row, from_col, to_row, to_col)
            self.update_display()
            
        self.is_player_turn = True
        self.check_game_over()
    
    def is_in_check(self, color):
        # Find king's position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece == (color, 'K'):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
                
        return self.is_square_attacked(king_pos[0], king_pos[1], color)
    
    def is_square_attacked(self, row, col, color):
        opponent = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece[0] == opponent:
                    if self.is_basic_move_valid(r, c, row, col, piece[1]):
                        return True
        return False
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
            
        # Try all possible moves to see if any can get out of check
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece and piece[0] == color:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(from_row, from_col, to_row, to_col):
                                return False
        return True
    
    def check_game_over(self):
        for color in ['white', 'black']:
            if self.is_checkmate(color):
                winner = 'Black' if color == 'white' else 'White'
                messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
                return True
        return False

if __name__ == "__main__":
    game = ChessGame() 