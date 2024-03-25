from copy import deepcopy
from .state import State


class Ida_Star:
    difficulty = "Medium"
    computer_symbol = 'O'

    # Checks if the current state is the final state
    @staticmethod
    def final_state(state):
        # assert types
        assert isinstance(state, State), "Wrong parameter type"

        return state.board.is_finished()

    # Gets the successors of the current state
    @staticmethod
    def successors(state):
        # assert types
        assert isinstance(state, State), "Wrong parameter type"

        return state.find_successors(Ida_Star.difficulty, Ida_Star.computer_symbol)

    # Iterative Deepening A* algorithm with depth limit
    @staticmethod
    def ida_star(game_board, depth):
        # assert types
        assert isinstance(depth, int), "Wrong parameter type"

        def expand(current_state, limit, depth):
            if current_state.f > limit:
                return current_state, current_state.f, depth
            if depth == 0:
                return current_state, current_state.f, 0
            if Ida_Star.final_state(current_state):
                return current_state, float('inf'), 0
            successors = Ida_Star.successors(current_state)
            if len(successors) == 0:
                return current_state, float('inf'), 0
            minim = min([expand(succ, limit, depth - 1) for succ in successors], key=lambda s: s[1])
            return minim

        starting_state = State(game_board)
        limit = starting_state.estimate_h(Ida_Star.computer_symbol)
        state = starting_state
        while limit != float('inf') and depth != 0:
            state, limit, depth = expand(starting_state, limit, depth)
        return state

    # Gets the best move for the computer, returning the first state after the root
    @staticmethod
    def get_move(game_board, depth):
        # assert types
        assert isinstance(depth, int), "Wrong parameter type"

        best_state = Ida_Star.ida_star(game_board, depth)
        return best_state.path_to_root()[1].board.boxes
