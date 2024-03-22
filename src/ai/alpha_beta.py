from copy import deepcopy
from time import sleep


class Alpha_Beta:
    difficulty = ' '

    @staticmethod
    def set_difficulty(difficulty):
        Alpha_Beta.difficulty = difficulty

    @staticmethod
    def alpha_beta(board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_finished():
            return board.estimate_score(Alpha_Beta.difficulty), None

        if maximizing_player:
            max_value = -board.limit
            best_move = None
            for move in board.get_possible_moves():
                if not board.make_move(move[0], move[1], move[2]):
                    continue
                if board.completed_box:
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, True)[0]
                else:
                    board.current_player = board.get_opponent()
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, False)[0]
                    board.current_player = board.get_opponent()
                board.undo_move(move[0], move[1], move[2])
                if value > max_value:
                    max_value = value
                    best_move = move
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return max_value, best_move
        else:
            min_value = board.limit
            best_move = None
            for move in board.get_possible_moves():
                if not board.make_move(move[0], move[1], move[2]):
                    continue
                if board.completed_box:
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, False)[0]
                else:
                    board.current_player = board.get_opponent()
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, True)[0]
                    board.current_player = board.get_opponent()
                board.undo_move(move[0], move[1], move[2])
                if value < min_value:
                    min_value = value
                    best_move = move
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return min_value, best_move

    @staticmethod
    def get_move(game_board, depth=5):
        board = deepcopy(game_board)
        return Alpha_Beta.alpha_beta(board, depth, -board.limit - 10, board.limit + 10, board.current_player == board.max_symbol)[1]
