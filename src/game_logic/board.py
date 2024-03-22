from . import box
from copy import deepcopy
from random import shuffle


class Board:
    # Board details
    no_lines = no_columns = 4  # min 3, max 7
    max_symbol            = 'X'
    min_symbol            = 'O'
    limit                 = 1000

    def __init__(self, boxes=None):
        if boxes is None:
            self.boxes = [[box.Box() for _ in range(Board.no_columns)] for _ in range(Board.no_lines)]
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

    def is_finished(self):
        return self.max_score + self.min_score == Board.get_total_points()

    # Finds the symbol of the other player
    def get_opponent(self):
        return Board.max_symbol if self.current_player == Board.min_symbol else Board.min_symbol

    # Returns all possible moves from the point (i, j)
    def get_direction_options(self, i, j):
        options = ''

        # when going up from the point (i, j), we are adding the left line of the box (i - 1, j)
        if i > 0 and not self.boxes[i - 1][j].left:
            options += "[u]p or "
        # when going down from the point (i, j), we are adding the left line of the box (i, j)
        if i < Board.no_lines - 1 and not self.boxes[i][j].left:
            options += "[d]own or "
        # when going left from the point (i, j), we are adding the up line of the box (i, j - 1)
        if j > 0 and not self.boxes[i][j - 1].up:
            options += "[l]eft or "
        # when going right from the point (i, j), we are adding the up line of the box (i, j)
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
            return Board.total_points - self.min_score
        else:
            return Board.total_points - self.max_score

    # Estimate for the medium and hard AI
    def good_score(self, current_player):
        # the score is equal to the number of the boxes the current_player completed +
        #                       the number of boxes the current player can complete
        # in other words, it's the maximum points reachable by the current player in a simulation

        # make a copy for the simulation
        board_copy = deepcopy(self)

        if board_copy.current_player == current_player:
            almost_completed_boxes = board_copy.almost_completed_boxes()
            while almost_completed_boxes:
                i, j, direction = almost_completed_boxes.pop()
                # in case we completed this box in the last move
                if board_copy.boxes[i][j].side_completed(direction):
                    continue

                new_i, new_j, direction = Board.translate_box_into_point(i, j, direction)
                board_copy.make_move(new_i, new_j, direction)

                # add the new almost completed boxes
                almost_completed_boxes += board_copy.almost_completed_boxes()

        # the final score
        if current_player == Board.max_symbol:
            return board_copy.max_score
        else:
            return board_copy.min_score

    def estimate_score(self, difficulty):
        if self.max_score + self.min_score == Board.get_total_points():
            if self.max_score == self.min_score:
                return 0
            elif self.max_score > self.min_score:
                return Board.limit + self.max_score
            else:
                return -Board.limit - self.min_score
        else:
            # Easy because the enum difficulty str returns the string as title
            if difficulty == "Easy":
                return self.naive_score(Board.max_symbol) - self.naive_score(Board.min_symbol)
            else:
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

    def undo_box_completed(self, i, j):
        if self.boxes[i][j].completed():
            self.completed_box = False
            self.boxes[i][j].symbol = ' '

            if self.current_player == self.max_symbol:
                self.max_score -= 1
            else:
                self.min_score -= 1

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

    # Makes a move on the board, marking both boxes and checking for completed boxes
    # For the GUI -> If the move was already made, returns False so we don't change the player
    def make_move(self, i, j, direction):
        self.completed_box = False

        if "right".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if self.boxes[i][j].up is True:
                return False

            self.boxes[i][j].up = True
            self.check_box_completed(i, j)

            # we also complete the down line of the box (i - 1, j)
            if self.valid_position(i - 1, j):
                self.boxes[i - 1][j].down = True
                self.check_box_completed(i - 1, j)
        elif "down".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if self.boxes[i][j].left is True:
                return False

            self.boxes[i][j].left = True
            self.check_box_completed(i, j)

            # we also complete the right line of the box (i, j - 1)
            if self.valid_position(i, j - 1):
                self.boxes[i][j - 1].right = True
                self.check_box_completed(i, j - 1)
        elif "left".startswith(direction):
            # the up-right point (i, j) represents the box (i, j - 1)
            if self.boxes[i][j - 1].up is True:
                return False

            self.boxes[i][j - 1].up = True
            self.check_box_completed(i, j - 1)

            # we also complete the down line of the box (i - 1, j - 1)
            if self.valid_position(i - 1, j - 1):
                self.boxes[i - 1][j - 1].down = True
                self.check_box_completed(i - 1, j - 1)
        elif "up".startswith(direction):
            # the down-left point (i, j) represents the box (i - 1, j)
            if self.boxes[i - 1][j].left is True:
                return False

            self.boxes[i - 1][j].left = True
            self.check_box_completed(i - 1, j)

            # we also complete the right line of the box (i - 1, j - 1)
            if self.valid_position(i - 1, j - 1):
                self.boxes[i - 1][j - 1].right = True
                self.check_box_completed(i - 1, j - 1)

        # not a repeated move
        return True

    # def alpha_beta(self, depth, alpha, beta, maximizing_player):
    #     if depth == 0 or self.is_finished():
    #         return self.estimate_score(), None

    #     if maximizing_player:
    #         max_value = -Board.limit
    #         best_move = None
    #         for move in self.get_possible_moves():
    #             if not self.make_move(move[0], move[1], move[2]):
    #                 continue
    #             if self.completed_box:
    #                 value = self.alpha_beta(depth, alpha, beta, True)[0]
    #             else:
    #                 self.current_player = self.get_opponent()
    #                 value = self.alpha_beta(depth - 1, alpha, beta, False)[0]
    #                 self.current_player = self.get_opponent()
    #             self.undo_move(move[0], move[1], move[2])
    #             if value > max_value:
    #                 max_value = value
    #                 best_move = move
    #             alpha = max(alpha, value)
    #             if beta <= alpha:
    #                 break
    #         return max_value, best_move
    #     else:
    #         min_value = Board.limit
    #         best_move = None
    #         for move in self.get_possible_moves():
    #             if not self.make_move(move[0], move[1], move[2]):
    #                 continue
    #             if self.completed_box:
    #                 value = self.alpha_beta(depth, alpha, beta, False)[0]
    #             else:
    #                 self.current_player = self.get_opponent()
    #                 value = self.alpha_beta(depth - 1, alpha, beta, True)[0]
    #                 self.current_player = self.get_opponent()
    #             self.undo_move(move[0], move[1], move[2])
    #             if value < min_value:
    #                 min_value = value
    #                 best_move = move
    #             beta = min(beta, value)
    #             if beta <= alpha:
    #                 break
    #         return min_value, best_move

    # def get_move_from_ai(self, depth=5):
    #     return self.alpha_beta(depth, -Board.limit, Board.limit, self.current_player == Board.max_symbol)[1]

    '''
    Past approaches for good_estimate

    # Aproach 1 -> Backtracking with hashing
    # Finds the answer, but it's too slow on big sizes
    def possible_completed_boxes(self, depth):
        # if the possition is already hashed, return the value
        if repr(self) in Board.config:
            self.completed_box = False
            return Board.config[repr(self)] - self.get_actual_player_points()
        if depth == 0:
            return self.get_possible_player_points(self.current_player)
        no_boxes = 0
        possible_moves = self.get_possible_moves()
        while True:
            for move in possible_moves:
                # copy the board so we can simulate the moves
                board_copy = deepcopy(self)
                board_copy.make_move(move[0], move[1], move[2], True)

                if board_copy.completed_box:
                    if board_copy.get_possible_player_points() + board_copy.get_actual_player_points() == Board.get_total_points() - board_copy.get_actual_opponent_points():
                        return board_copy.get_possible_player_points()
                    no_boxes = max(board_copy.get_possible_player_points(), board_copy.possible_completed_boxes(depth - 1))
                    Board.config[repr(board_copy)] = no_boxes
            if not board_copy.completed_box:
                break
        board_copy.completed_box = False
        return no_boxes

    
    # Aproach 2 -> Find the max chain from the last added line
    # Decent time, but the result is not the best
    # When reaching a final position, we can also call the backtracking approach with depth 1
    # and continue the max_chain function from that new line, if it exists

    # Returns the almost completed neighbors of the box (i, j)
    def almost_completed_neighbors(self, i, j):
        # if i is the last line, we are going to the previous line
        if i == Board.no_lines - 1:
            i -= 1
        # if j is the last column, we are going to the previous column
        if j == Board.no_columns - 1:
            j -= 1
        neighbors = []
        # if i > 0, we have the up neighbor (i - 1, j)
        if i > 0:
            direction = self.boxes[i - 1][j].almost_completed()
            if direction:
                neighbors.append((i - 1, j, direction))
        # if i < no_lines - 2, we have down neighbor (i + 1, j)
        if i < Board.no_lines - 2:
            direction = self.boxes[i + 1][j].almost_completed()
            if direction:
                neighbors.append((i + 1, j, direction))
        # if j > 0, we have the left neighbor (i, j - 1)
        if j > 0:
            direction = self.boxes[i][j - 1].almost_completed()
            if direction:
                neighbors.append((i, j - 1, direction))
        # if j < no_columns - 2, we have right neighbor (i, j + 1)
        if j < Board.no_columns - 2:
            direction = self.boxes[i][j + 1].almost_completed()
            if direction:
                neighbors.append((i, j + 1, direction))
        return neighbors

    # How many boxes can the current player complete from the last point
    def max_chain(self):
        if self.last_line is None:
            return 0
        board_copy = deepcopy(self)
        point1, point2 = self.last_line
        i1, j1 = point1  # first point of the last line
        neighbors = board_copy.almost_completed_neighbors(i1, j1)
        if point2 is not None:
            i2, j2 = point2  # second point of the last line
            neighbors += board_copy.almost_completed_neighbors(i2, j2)
        while neighbors:
            i, j, position = neighbors.pop()
            if board_copy.boxes[i][j].side_completed(position):
                continue
            new_i, new_j, position = Board.translate_box_into_point(i, j, position)
            board_copy.make_move(new_i, new_j, position, True)
            neighbors += board_copy.almost_completed_neighbors(i, j)
        return board_copy.get_simulation_player_points()


    # Past approach for minimax, decent but I optimized it with alpha-beta
    # This was made before undo_move, so it still creates new board like the alpha_beta function under it
    # If one wants to use minimax instead of alpha_beta, copy the code and use undo_move instead

    def minimax(self, depth, maximizing_player):
        if depth == 0 or self.is_finished():
            return self.estimate_score(), None

        if maximizing_player:
            max_value = -100000
            best_move = None
            for move in self.get_possible_moves():
                board_copy = deepcopy(self)
                board_copy.make_move(move[0], move[1], move[2])
                if board_copy.completed_box:
                    value = board_copy.minimax(depth - 1, True)[0]
                else:
                    board_copy.current_player = board_copy.get_opponent()
                    value = board_copy.minimax(depth - 1, False)[0]
                if value > max_value:
                    max_value = value
                    best_move = move
            return max_value, best_move
        else:
            min_value = 100000
            best_move = None
            for move in self.get_possible_moves():
                board_copy = deepcopy(self)
                board_copy.make_move(move[0], move[1], move[2])
                if board_copy.completed_box:
                    value = board_copy.minimax(depth - 1, False)[0]
                else:
                    board_copy.current_player = board_copy.get_opponent()
                    value = board_copy.minimax(depth - 1, True)[0]
                if value < min_value:
                    min_value = value
                    best_move = move
            return min_value, best_move

    # Past approach for alpha_beta, creating a new board each time instead of undoing the move

    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_finished():
            return self.estimate_score(), None

        if maximizing_player:
            max_value = -Board.limit
            best_move = None
            for move in self.get_possible_moves():
                board_copy = deepcopy(self)
                if not board_copy.make_move(move[0], move[1], move[2]):
                    continue
                if board_copy.completed_box:
                    value = board_copy.alpha_beta(depth - 1, alpha, beta, True)[0]
                else:
                    board_copy.current_player = board_copy.get_opponent()
                    value = board_copy.alpha_beta(depth - 1, alpha, beta, False)[0]
                if value > max_value:
                    max_value = value
                    best_move = move
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return max_value, best_move
        else:
            min_value = Board.limit
            best_move = None
            for move in self.get_possible_moves():
                board_copy = deepcopy(self)
                if not board_copy.make_move(move[0], move[1], move[2]):
                    continue
                if board_copy.completed_box:
                    value = board_copy.alpha_beta(depth - 1, alpha, beta, False)[0]
                else:
                    board_copy.current_player = board_copy.get_opponent()
                    value = board_copy.alpha_beta(depth - 1, alpha, beta, True)[0]
                if value < min_value:
                    min_value = value
                    best_move = move
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return min_value, best_move
    '''
