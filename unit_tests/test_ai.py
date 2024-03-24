from src.game_logic.board import Board
from src.game_logic.game import Game
from src.misc.enums import Algorithm
import unittest


def make_move(board, x, y, direction):
    valid = board.make_move(x, y, direction)
    if valid and not board.completed_box:
        board.current_player = board.get_opponent()
    return valid


class TestDotsAndBoxesGame(unittest.TestCase):
    def test_alpha_beta_completing_box(self):
        Game.algorithm  = Algorithm.ALPHA_BETA
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")
        make_move(board, 0, 0, "down")
        make_move(board, 0, 1, "down")

        game.computer_move(0)

        self.assertEqual(str(Game.algorithm), "Alpha Beta")
        self.assertEqual(board.min_score, 1)
        self.assertEqual(board.current_player, board.min_symbol)

    def test_ida_star_completing_box(self):
        Game.algorithm  = Algorithm.IDA_STAR
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")
        make_move(board, 0, 0, "down")
        make_move(board, 0, 1, "down")

        game.computer_move(0)

        self.assertEqual(str(Game.algorithm), "IDA*")
        self.assertEqual(board.min_score, 1)
        self.assertEqual(board.current_player, board.min_symbol)


if __name__ == '__main__':
    unittest.main()
