class Move:
    def __init__(self, start, end, piece_type, color, move_type="normal", **kwargs):
        if not self._is_valid_pos(start):
            raise ValueError(f"Invalid start position: {start}")
        if not self._is_valid_pos(end):
            raise ValueError(f"Invalid end position: {end}")
        self.start = start          # Tuple (row, col)
        self.end = end              # Tuple (row, col)
        self.piece_type = piece_type # String: 'P', 'N', 'R', 'B', 'Q', 'K'
        self.color = color          # String: 'w' or 'b'
        self.move_type = move_type  # String: 'normal', 'capture', 'castle', etc.
        self.captured_piece = kwargs.get('captured_piece')
        self.promotion_to = kwargs.get('promotion_to')
        self.castle_rook_start = kwargs.get('castle_rook_start')
        self.castle_rook_end = kwargs.get('castle_rook_end')

    def _is_valid_pos(self, pos):
        #check if position is valid
        if not isinstance(pos, tuple):
            return False
        if len(pos) != 2:
            return False
        row, col = pos
        return 0 <= row <= 7 and 0 <= col <= 7
    
    def to_algebraic(self): #makes the files be in alphabetical order
        files = 'abcdefgh'
        start_sq = "{}{}".format(files[self.start[1]], 8 - self.start[0])
        end_sq = "{}{}".format(files[self.end[1]], 8 - self.end[0])
        return start_sq + end_sq
    
    # Placeholder
    def __repr__(self):
        return f"Move({self.start}->{self.end}, {self.piece_type}, {self.color})"