class Box:
    def __init__(self, up=False, down=False, left=False, right=False, symbol=' '):
        self.up     = up
        self.down   = down
        self.left   = left
        self.right  = right
        self.symbol = symbol

    def __str__(self):
        return "up: " + str(self.up) \
               + ", down: " + str(self.down) \
               + ", left: " + str(self.left) \
               + ", right: " + str(self.right)

    def __repr__(self):
        # returns a bitset representation of the box
        return str(int(self.up)) + str(int(self.down)) + str(int(self.left)) + str(int(self.right))

    def available_moves(self):
        # returns a list of all available moves
        moves = []
        if self.up is False:
            moves.append('up')
        if self.down is False:
            moves.append('down')
        if self.left is False:
            moves.append('left')
        if self.right is False:
            moves.append('right')
        return moves

    def complete_box(self):
        # returns true if the box is complete
        return self.up and self.down and self.left and self.right
