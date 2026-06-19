class Piece:
    def __init__(self, color, position):
        # color should be 'w' or 'b', position is (row, col)
        if color not in ('w', 'b'):
            raise ValueError(f"Invalid color: {color}")
        if not (0 <= position[0] <= 7 and 0 <= position[1] <= 7):
            raise ValueError(f"Invalid position: {position}")

        self.color = color
        self.position = position
        self.has_moved = False  # for castling and pawn double-moves

    def get_symbol(self):
        # subclasses will fill this in
        raise NotImplementedError

    def get_valid_moves(self, board):
        # subclasses will fill this in
        raise NotImplementedError

    def move_to(self, new_position):
        # updates position and marks piece as moved
        self.position = new_position
        self.has_moved = True


class Pawn(Piece):
    def get_symbol(self):
        return '♙' if self.color == 'w' else '♟'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        # white moves up (row decreases), black moves down
        direction = -1 if self.color == 'w' else 1

        # forward 1 square
        new_row = row + direction
        if 0 <= new_row <= 7 and board.is_empty(new_row, col):
            moves.append((new_row, col))
            # if on starting row, also allow forward 2
            if (self.color == 'w' and row == 6) or (self.color == 'b' and row == 1):
                new_row2 = row + 2 * direction
                if board.is_empty(new_row2, col):
                    moves.append((new_row2, col))

        # diagonal captures
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                target = board.get_piece(new_row, new_col)
                # only valid if there's an enemy piece there
                if target and target.color != self.color:
                    moves.append((new_row, new_col))
        return moves


class King(Piece):
    def get_symbol(self):
        return '♔' if self.color == 'w' else '♚'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        # king moves 1 square in any direction
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    target = board.get_piece(new_row, new_col)
                    if not target or target.color != self.color:
                        moves.append((new_row, new_col))

        # castling
        if not self.has_moved:
            # kingside castling
            kingside_rook = board.get_piece(row, 7)
            if (kingside_rook and
                    type(kingside_rook).__name__ == 'Rook' and
                    not kingside_rook.has_moved and
                    board.is_empty(row, 5) and
                    board.is_empty(row, 6)):
                moves.append((row, 6))

            # queenside castling
            queenside_rook = board.get_piece(row, 0)
            if (queenside_rook and
                    type(queenside_rook).__name__ == 'Rook' and
                    not queenside_rook.has_moved and
                    board.is_empty(row, 1) and
                    board.is_empty(row, 2) and
                    board.is_empty(row, 3)):
                moves.append((row, 2))

        return moves

class Queen(Piece):
    def get_symbol(self):
        return '♕' if self.color == 'w' else '♛'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        # Queen = Rook + Bishop directions combined
        directions = [(-1,0),(1,0),(0,-1),(0,1),   # rook directions
                      (-1,-1),(-1,1),(1,-1),(1,1)]  # bishop directions
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r <= 7 and 0 <= c <= 7:
                target = board.get_piece(r, c)
                if target:
                    if target.color != self.color:
                        moves.append((r, c))  # capture and stop
                    break  # blocked either way
                moves.append((r, c))
                r += dr
                c += dc
        return moves


class Rook(Piece):
    def get_symbol(self):
        return '♖' if self.color == 'w' else '♜'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r <= 7 and 0 <= c <= 7:
                target = board.get_piece(r, c)
                if target:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
        return moves


class Bishop(Piece):
    def get_symbol(self):
        return '♗' if self.color == 'w' else '♝'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r <= 7 and 0 <= c <= 7:
                target = board.get_piece(r, c)
                if target:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr
                c += dc
        return moves


class Knight(Piece):
    def get_symbol(self):
        return '♘' if self.color == 'w' else '♞'

    def get_valid_moves(self, board):
        moves = []
        row, col = self.position
        # L-shapes
        jumps = [(-2,-1),(-2,1),(-1,-2),(-1,2),
                 (1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in jumps:
            r, c = row + dr, col + dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                target = board.get_piece(r, c)
                if not target or target.color != self.color:
                    moves.append((r, c))
        return moves