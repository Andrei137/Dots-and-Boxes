class Box:
    def __init__(self, up=False, down=False, left=False, right=False, symbol=' '):
        self.up     = up
        self.down   = down
        self.left   = left
        self.right  = right
        self.symbol = symbol

    def __str__(self):
        return "up: " + (' ' if self.up is True else '') + str(self.up) + \
               " | down: " + (' ' if self.down is True else '') + str(self.down) + \
               " | left: " + (' ' if self.left is True else '') + str(self.left) + \
               " | right: " + (' ' if self.right is True else '') + str(self.right)

    # Returns a bitset representation of the box
    def __repr__(self):
        return '[' + str(int(self.up)) + str(int(self.down)) + str(int(self.left)) + str(int(self.right)) + ']'

    def __eq__(self, other):
        return self.up == other.up and \
               self.down == other.down and \
               self.left == other.left and \
               self.right == other.right and \
               self.symbol == other.symbol

    # Returns a list of all uncompleted sides
    def available_moves(self):
        moves = []
        if self.up is False:
            moves.append("up")
        if self.down is False:
            moves.append("down")
        if self.left is False:
            moves.append("left")
        if self.right is False:
            moves.append("right")
        return moves

    # Returns True if the side is completed
    def side_completed(self, position):
        if position == "up":
            return self.up
        if position == "down":
            return self.down
        if position == "left":
            return self.left
        if position == "right":
            return self.right
        return False

    # Returns which side is missing if the box is almost completed
    def almost_completed(self):
        if repr(self).count('1') == 3:
            if self.up is False:
                return "up"
            if self.down is False:
                return "down"
            if self.left is False:
                return "left"
            if self.right is False:
                return "right"
        return False

    # returns True if the box is completed
    def completed(self):
        return self.up and self.down and self.left and self.right
