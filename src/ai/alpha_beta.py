class Alpha_Beta:
    difficulty = "Medium"

    @staticmethod
    def alpha_beta(board, depth, alpha, beta, maximizing_player):
        # if depth is 0 or the game is finished, return the score of the current board
        if depth == 0 or board.is_finished():
            return board.estimate_score(Alpha_Beta.difficulty), None

        # if the current player is the maximizing player, maximize the score
        if maximizing_player:
            max_value = -board.limit
            best_move = None
            for move in board.get_possible_moves():
                # try to make the current move
                if not board.make_move(move[0], move[1], move[2]):
                    # in case the move is invalid
                    # probably won't happen because of the implementation of get_possible_moves
                    # but better be safe than sorry
                    continue
                if board.completed_box:
                    # if the move completes a box, keep the same player
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, True)[0]
                else:
                    # otherwise, change the player
                    board.current_player = board.get_opponent()
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, False)[0]

                    # change it back after the recursive call
                    board.current_player = board.get_opponent()

                # undo the move to keep the board state unchanged
                board.undo_move(move[0], move[1], move[2])

                # if it finds a move with a bigger score, update the best move and the max value
                if value > max_value:
                    max_value = value
                    best_move = move

                # update alpha with the maximum value between alpha and the current value
                alpha = max(alpha, value)

                # if beta is less or equal to alpha, prune the tree
                if beta <= alpha:
                    break
            return max_value, best_move
        # if the current player is the minimizing player, minimize the score
        else:
            min_value = board.limit
            best_move = None
            for move in board.get_possible_moves():
                # try to make the current move
                if not board.make_move(move[0], move[1], move[2]):
                    # in case the move is invalid
                    # probably won't happen because of the implementation of get_possible_moves
                    # but better be safe than sorry
                    continue
                if board.completed_box:
                    # if the move completes a box, keep the same player
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, False)[0]
                else:
                    # otherwise, change the player
                    board.current_player = board.get_opponent()
                    value = Alpha_Beta.alpha_beta(board, depth - 1, alpha, beta, True)[0]

                    # change it back after the recursive call
                    board.current_player = board.get_opponent()

                # undo the move to keep the board state unchanged
                board.undo_move(move[0], move[1], move[2])

                # if it finds a move with a lower score, update the best move and the min value
                if value < min_value:
                    min_value = value
                    best_move = move

                # update beta with the minimum value between beta and the current value
                beta = min(beta, value)

                # if beta is less or equal to alpha, prune the tree
                if beta <= alpha:
                    break
            return min_value, best_move

    @staticmethod
    def get_move(game_board, depth):
        board = game_board

        alpha = -board.limit - board.get_total_score() - 1
        beta = board.limit + board.get_total_score() + 1

        return Alpha_Beta.alpha_beta(board, depth, alpha, beta, board.current_player == board.max_symbol)[1]
