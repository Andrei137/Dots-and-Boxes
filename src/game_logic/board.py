from .box import Box
from random import shuffle


class Board:
    # Board details
    no_lines = no_columns = 4  # min 3, max 7
    max_symbol            = 'X'
    min_symbol            = 'O'
    limit                 = 1000

    def __init__(self, boxes=None):
        if boxes is None:
            self.boxes = [[Box() for _ in range(Board.no_columns)] for _ in range(Board.no_lines)]
        else:
            self.boxes = boxes

        self.max_score      = 0
        self.min_score      = 0
        self.completed_box  = False  # Keeps turn if True
        self.current_player = Board.max_symbol

    # The actual board representation
    def __str__(self):
        boxes_str = ''

        for i in range(Board.no_lines - 1):
            for j in range(Board.no_columns - 1):
                # checks for the up line
                boxes_str += '*---' if self.boxes[i][j].up else '*   '
            boxes_str += '*\n'

            for j in range(Board.no_columns - 1):
                # checks for the left line
                boxes_str += '|' if self.boxes[i][j].left else ' '

                boxes_str += ' ' + self.boxes[i][j].symbol + ' '

            # last column -> checks right instead of left
            boxes_str += ('|' if self.boxes[i][Board.no_columns - 2].right else ' ') + '\n'

        # last line -> checks down instead of up
        for j in range(Board.no_columns - 1):
            boxes_str += '*---' if self.boxes[Board.no_lines - 2][j].down else '*   '

        # last point
        return boxes_str + '*'

    # Bitset representation of the board
    def __repr__(self):
        boxes_repr = '\n\t[up-down-left-right]\n\n\t'
        for i in range(Board.no_lines):
            for j in range(Board.no_columns):
                boxes_repr += repr(self.boxes[i][j])
            if i != Board.no_lines - 1:
                boxes_repr += '\n\t'
            else:
                boxes_repr += '\n'
        return boxes_repr

    # Translates the box (i, j) into the point (i, j) given a position
    # The point (i, j) is the top-left point of the box (i, j)
    @staticmethod
    def translate_box_into_point(i, j, position):
        # box (i, j) up -> point (i, j) right
        if position == "up":
            return i, j, "right"
        # box (i, j) down -> point (i + 1, j) right
        if position == "down":
            return i + 1, j, "right"
        # box (i, j) left -> point (i, j) down
        if position == "left":
            return i, j, "down"
        # box (i, j) right -> point (i, j + 1) down
        if position == "right":
            return i, j + 1, "down"

        # wrong position
        return None

    # Returns True if the box position (i, j) is valid
    @staticmethod
    def valid_position(i, j):
        return 0 <= i < Board.no_lines and 0 <= j < Board.no_columns

    # Returns the total points of the game
    @staticmethod
    def get_total_points():
        return (Board.no_lines - 1) * (Board.no_columns - 1)

    # Returns True if the game is finished
    def is_finished(self):
        return self.max_score + self.min_score == Board.get_total_points()

    # Finds the symbol of the other player
    def get_opponent(self):
        return Board.max_symbol if self.current_player == Board.min_symbol else Board.min_symbol

    # Returns all possible moves from the point (i, j)
    def get_direction_options(self, i, j):
        options = ''

        # when going up from the point (i, j), add the left line of the box (i - 1, j)
        if i > 0 and not self.boxes[i - 1][j].left:
            options += "[u]p or "
        # when going down from the point (i, j), add the left line of the box (i, j)
        if i < Board.no_lines - 1 and not self.boxes[i][j].left:
            options += "[d]own or "
        # when going left from the point (i, j), add the up line of the box (i, j - 1)
        if j > 0 and not self.boxes[i][j - 1].up:
            options += "[l]eft or "
        # when going right from the point (i, j), add the up line of the box (i, j)
        if j < Board.no_columns - 1 and not self.boxes[i][j].up:
            options += "[r]ight or "

        # remove the last " or "
        return options[:-4]

    # Returns all the possible moves from the current state
    def get_possible_moves(self):
        # moves will be a list of tuples (i, j, position)
        # i, j -> coordinates of the point, not the box
        moves = []

        for i in range(Board.no_lines):
            for j in range(Board.no_columns):
                options = self.get_direction_options(i, j)
                if options:
                    directions = options.split(" or ")
                    for direction in directions:
                        # direction[1] + direction[3:] removes the []
                        direction = direction[1] + direction[3:]
                        # only keep down and right moves to avoid duplicates
                        if direction == "down" or direction == "right":
                            moves.append((i, j, direction))

        # shuffle the moves so the ai can start with random moves instead of the same one each time
        shuffle(moves)
        return moves

    # Estimate for the easy AI
    def naive_score(self, current_player):
        # the score is equal to the number of the boxes the current_player completed +
        #                       the uncompleted ones
        # in other words, the score is the total score - the other player's score
        if current_player == self.max_symbol:
            return Board.get_total_points() - self.min_score
        else:
            return Board.get_total_points() - self.max_score

    # Estimate for the medium and hard AI
    def good_score(self, current_player):
        # the score is equal to the number of the boxes the current_player completed +
        #                       the number of boxes the current player can complete
        # in other words, it's the maximum points reachable by the current player in a simulation

        moves = []

        if self.current_player == current_player:
            almost_completed_boxes = self.almost_completed_boxes()
            while almost_completed_boxes:
                i, j, direction = almost_completed_boxes.pop()
                # in case the current box got completed in the last move
                if self.boxes[i][j].side_completed(direction):
                    continue

                new_i, new_j, direction = Board.translate_box_into_point(i, j, direction)
                self.make_move(new_i, new_j, direction)
                moves.append((new_i, new_j, direction))

                # add the new almost completed boxes
                almost_completed_boxes += self.almost_completed_boxes()

        # get the score before undoing the moves
        if current_player == Board.max_symbol:
            answer = self.max_score
        else:
            answer = self.min_score

        # undo the moves
        for move in moves:
            i, j, direction = move
            self.undo_move(i, j, direction)

        # return the answer
        return answer

    # Estimate for minimax
    def estimate_score(self, difficulty):
        if self.max_score + self.min_score == Board.get_total_points():
            if self.max_score == self.min_score:
                return 0
            elif self.max_score > self.min_score:
                return Board.limit + self.max_score
            else:
                return -Board.limit - self.min_score
        else:
            # "Easy" because the enum difficulty str returns the string as title
            if difficulty == "Easy":
                return self.naive_score(Board.max_symbol) - self.naive_score(Board.min_symbol)
            else:
                # if the max player is the current player, returns max - 0
                # if the min player is the current player, returns 0 - min
                return self.good_score(Board.max_symbol) - self.good_score(Board.min_symbol)

    # Returns all almost completed boxes
    def almost_completed_boxes(self):
        boxes = []
        for i in range(Board.no_lines):
            for j in range(Board.no_columns):
                direction = self.boxes[i][j].almost_completed()
                if direction:
                    boxes.append((i, j, direction))
        return boxes

    # Checks if the box (i, j) is completed and updates the score
    def check_box_completed(self, i, j):
        if self.boxes[i][j].completed():
            self.completed_box = True
            self.boxes[i][j].symbol = self.current_player

            if self.current_player == self.max_symbol:
                self.max_score += 1
            else:
                self.min_score += 1

    # Undoes the completion of the box (i, j) and updates the score
    def undo_box_completed(self, i, j):
        if self.boxes[i][j].completed():
            self.completed_box = False
            self.boxes[i][j].symbol = ' '

            if self.current_player == self.max_symbol:
                self.max_score -= 1
            else:
                self.min_score -= 1

    # Makes a move on the board, marking both boxes and checking for completed boxes
    # For the GUI -> If the move was already made, returns False to keep the player's turn
    def make_move(self, i, j, direction):
        self.completed_box = False

        if "right".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if self.boxes[i][j].up is True:
                return False

            self.boxes[i][j].up = True
            self.check_box_completed(i, j)

            # also complete the down line of the box (i - 1, j)
            if self.valid_position(i - 1, j):
                self.boxes[i - 1][j].down = True
                self.check_box_completed(i - 1, j)
        elif "down".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if self.boxes[i][j].left is True:
                return False

            self.boxes[i][j].left = True
            self.check_box_completed(i, j)

            # also complete the right line of the box (i, j - 1)
            if self.valid_position(i, j - 1):
                self.boxes[i][j - 1].right = True
                self.check_box_completed(i, j - 1)
        elif "left".startswith(direction):
            # the up-right point (i, j) represents the box (i, j - 1)
            if self.boxes[i][j - 1].up is True:
                return False

            self.boxes[i][j - 1].up = True
            self.check_box_completed(i, j - 1)

            # also complete the down line of the box (i - 1, j - 1)
            if self.valid_position(i - 1, j - 1):
                self.boxes[i - 1][j - 1].down = True
                self.check_box_completed(i - 1, j - 1)
        elif "up".startswith(direction):
            # the down-left point (i, j) represents the box (i - 1, j)
            if self.boxes[i - 1][j].left is True:
                return False

            self.boxes[i - 1][j].left = True
            self.check_box_completed(i - 1, j)

            # also complete the right line of the box (i - 1, j - 1)
            if self.valid_position(i - 1, j - 1):
                self.boxes[i - 1][j - 1].right = True
                self.check_box_completed(i - 1, j - 1)

        # not a repeated move
        return True

    # Undoes a move on the board, keeping the score accurate
    def undo_move(self, i, j, direction):
        if "right".startswith(direction):
            self.undo_box_completed(i, j)
            self.boxes[i][j].up = False

            if self.valid_position(i - 1, j):
                self.undo_box_completed(i - 1, j)
                self.boxes[i - 1][j].down = False
        elif "down".startswith(direction):
            self.undo_box_completed(i, j)
            self.boxes[i][j].left = False

            if self.valid_position(i, j - 1):
                self.undo_box_completed(i, j - 1)
                self.boxes[i][j - 1].right = False

        elif "left".startswith(direction):
            self.undo_box_completed(i, j - 1)
            self.boxes[i][j - 1].up = False

            if self.valid_position(i - 1, j - 1):
                self.undo_box_completed(i - 1, j - 1)
                self.boxes[i - 1][j - 1].down = False
        elif "up".startswith(direction):
            self.undo_box_completed(i - 1, j)
            self.boxes[i - 1][j].left = False

            if self.valid_position(i - 1, j - 1):
                self.undo_box_completed(i - 1, j - 1)
                self.boxes[i - 1][j - 1].right = False
