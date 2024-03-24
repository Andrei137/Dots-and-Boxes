from copy import deepcopy


class State:
    def __init__(self, board, parent=None, g=0, h=0, successors=[]):
        self.board      = deepcopy(board)
        self.parent     = parent
        self.g          = g
        self.h          = h
        self.f          = g + h
        self.successors = successors

    def __eq__(self, other):
        return self.board == other.board

    def __lt__(self, other):
        if self.f == other.f:
            return self.g < other.g
        return self.f < other.f

    # The actual board representation
    def __str__(self):
        return str(self.board)

    # Bitset representation of the board
    def __repr__(self):
        return repr(self.board)

    # The path from the current state to the root
    def path_to_root(self):
        path  = [self]
        state = self

        while state.parent is not None:
            path = [state.parent] + path
            state = state.parent

        return path

    # Checks if the current state is visited
    def is_visited(self):
        return len([1 for state in self.path_to_root() if state == self]) > 1

    # Calculates the heuristic value of the current state
    def estimate_h(self, computer_symbol):
        # get the remaining edges
        remaining_edges = len(self.board.get_possible_moves())

        # get the player and opponent scores
        player_symbol  = self.board.max_symbol if computer_symbol == self.board.min_symbol else self.board.min_symbol
        player_score   = self.board.get_player_score(player_symbol)
        computer_score = self.board.get_player_score(computer_symbol)

        if self.board.current_player == computer_symbol:
            # if the computer is the current player
            # remaining_edges / 4 -> the aproximate number of boxes left
            # player_score - computer_score -> the difference between the player and the opponent scores, the lower the better
            # we also subtract the number of boxes that the computer can chain, so the computer prefers that path
            score = remaining_edges / 4 + player_score - computer_score - self.board.good_score(computer_symbol)
        else:
            # if the opponent is the current player
            # remaining_edges / 4 -> the aproximate number of boxes left
            # computer_score - player_score -> the difference between the computer and the player scores, the higher the better
            # we also add the number of boxes that the the player can chain, so the computer avoids that path
            score = remaining_edges / 4 - player_score + computer_score + self.board.good_score(player_symbol)
        return score

    def find_successors(self, difficulty, computer_symbol):
        self.successors = []
        moves = self.board.get_possible_moves()
        for move in moves:
            new_board = deepcopy(self.board)
            new_board.make_move(move[0], move[1], move[2])

            if not new_board.completed_box:
                new_board.current_player = self.board.get_opponent()

            if difficulty != "Easy" and new_board.current_player == computer_symbol:
                # If the computer can chain more than 1 box, it will prefer to do so
                if new_board.good_score(computer_symbol) >= 2:
                    g = self.g
                else:
                    # prefer to complete a box
                    g = self.g + (not new_board.completed_box)
            else:
                g = self.g + 1

            new_state = State(new_board, self, g, self.estimate_h(computer_symbol))

            self.successors.append(new_state)

        return self.successors
