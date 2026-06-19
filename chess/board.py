from pieces import Pawn, Rook, Knight, Bishop, Queen, King


class Board:
    def __init__(self):
        # Creates an 8x8 GRID
        self.grid = [[None] * 8 for _ in range(8)]
        self.setup_pieces()

    def setup_pieces(self):
        # places the pawns
        for col in range(8):
            self.grid[6][col] = Pawn('w', (6, col))
            self.grid[1][col] = Pawn('b', (1, col))

        #br row
        #order: Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, PieceClass in enumerate(order):
            self.grid[7][col] = PieceClass('w', (7, col))
            self.grid[0][col] = PieceClass('b', (0, col))
    #        # checker ensure coordinates are on board

    def get_piece(self, row, col):
        if not (0 <= row <= 7 and 0 <= col <= 7):
            return None
        return self.grid[row][col]

    def is_empty(self, row, col):
        return self.get_piece(row, col) is None

    def move_piece(self, from_pos, to_pos): #moving piece logic
        r1, c1 = from_pos
        r2, c2 = to_pos

        piece = self.grid[r1][c1]
        captured_piece = self.grid[r2][c2]

        self.grid[r2][c2] = piece
        self.grid[r1][c1] = None

        if piece:
            piece.move_to(to_pos)

        # handle castling = move the rook too
        if piece and type(piece).__name__ == 'King': #KING CASTLE
            if c2 - c1 == 2:
                rook = self.grid[r1][7]
                self.grid[r1][5] = rook
                self.grid[r1][7] = None
                if rook:
                    rook.move_to((r1, 5))
            #queenside castling
            elif c1 - c2 == 2:
                rook = self.grid[r1][0]
                self.grid[r1][3] = rook
                self.grid[r1][0] = None
                if rook:
                    rook.move_to((r1, 3))

        return captured_piece