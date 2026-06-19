from board import Board
import random
from move import Move

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'w'
        self.move_history = []
        self.status = 'ongoing'  # ongoing, checkmate, stalemate

    def switch_turn(self):
        self.current_turn = 'b' if self.current_turn == 'w' else 'w' #switching white -black after move

    def check_promotion(self, pos):
        row, col = pos
        piece = self.board.get_piece(row, col)
        if piece and type(piece).__name__ == 'Pawn':
            # white pawn reaches row 0, black pawn reaches row 7
            if (piece.color == 'w' and row == 0) or (piece.color == 'b' and row == 7):
                from pieces import Queen
                self.board.grid[row][col] = Queen(piece.color, (row, col))

    def _would_be_in_check(self, from_pos, to_pos): #king checker check
        r1, c1 = from_pos
        r2, c2 = to_pos

        piece = self.board.grid[r1][c1]
        captured = self.board.grid[r2][c2]
        old_pos = piece.position
        old_has_moved = piece.has_moved

        # try the move
        self.board.grid[r2][c2] = piece
        self.board.grid[r1][c1] = None
        piece.position = to_pos
        piece.has_moved = True

        in_check = self.is_in_check(piece.color)

        # undo the move
        self.board.grid[r1][c1] = piece
        self.board.grid[r2][c2] = captured
        piece.position = old_pos
        piece.has_moved = old_has_moved

        return in_check

    def make_move(self, from_pos, to_pos):
        piece = self.board.get_piece(*from_pos)

        if not piece:
            print("No piece at that position!")
            return False

        if piece.color != self.current_turn:
            print("It's not your turn!")
            return False

        valid_moves = piece.get_valid_moves(self.board)
        if to_pos not in valid_moves:
            print("Invalid move!")
            return False

        # prevent move if it leaves king in check
        if self._would_be_in_check(from_pos, to_pos):
            print("Move would leave king in check!")
            return False

        self.board.move_piece(from_pos, to_pos)
        self.move_history.append(Move(from_pos, to_pos, type(piece).__name__, piece.color))
        self.check_promotion(to_pos)
        self.move_history.append((from_pos, to_pos))
        self.switch_turn()
        self.update_game_status()
        return True

    def update_game_status(self): #note: check this
        if self.is_checkmate():
            self.status = 'checkmate'
        elif self.is_stalemate():
            self.status = 'stalemate'
        else:
            self.status = 'ongoing'

    def get_all_valid_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color:
                    for move in piece.get_valid_moves(self.board):
                        moves.append(((row, col), move))
        return moves

    def king_exists(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color and type(piece).__name__ == 'King':
                    return True
        return False

    def is_in_check(self, color):
        # find the king's position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color and type(piece).__name__ == 'King': #note: check this
                    king_pos = (row, col)
                    break

        if not king_pos:
            return True  # king is gone

        # check if any enemy piece can attack the king
        enemy_color = 'b' if color == 'w' else 'w'
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == enemy_color:
                    if king_pos in piece.get_valid_moves(self.board):
                        return True
        return False

    def is_checkmate(self):
        # must be in check first
        if not self.is_in_check(self.current_turn):
            return False

        # try every possible move and see if any gets out of check
        for from_pos, to_pos in self.get_all_valid_moves(self.current_turn):
            if not self._would_be_in_check(from_pos, to_pos):
                return False  # found a legal move

        return True  # no escape found = checkmate

    def is_stalemate(self):
        # stalemate: not in check but no legal moves
        if self.is_in_check(self.current_turn):
            return False

        for from_pos, to_pos in self.get_all_valid_moves(self.current_turn):
            if not self._would_be_in_check(from_pos, to_pos):
                return False  # found a legal move

        return True  # no legal moves and not in check = stalemate

    def __str__(self):
        turn = "White" if self.current_turn == 'w' else "Black"
        return f"Turn: {turn} | Moves played: {len(self.move_history)} | Status: {self.status}"


class ChessBot:
    def __init__(self, color='b', elo=200):
        self.color = color
        self.elo = elo

    def get_random_move(self, game):
        # get all valid moves for the bots color
        all_moves = game.get_all_valid_moves(self.color)

        if not all_moves:
            print("Bot has no valid moves!")
            return None

        #filter out moves that would leave bot s king in check
        legal_moves = [
            (from_pos, to_pos) for from_pos, to_pos in all_moves
            if not game._would_be_in_check(from_pos, to_pos)
        ]

        if not legal_moves:
            return None

        from_pos, to_pos = random.choice(legal_moves)
        return from_pos, to_pos

    def make_move(self, game):
        move = self.get_random_move(game)
        if move:
            from_pos, to_pos = move #note: check this func in the fdeks if its connected
            game.make_move(from_pos, to_pos)
            print(f"Bot moved from {from_pos} to {to_pos}")