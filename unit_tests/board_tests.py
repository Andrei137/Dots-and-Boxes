from src.game_logic.board import Board
from src.game_logic.game import Game
import unittest


def make_move(board, x, y, direction):
    valid = board.make_move(x, y, direction)
    if valid and not board.completed_box:
        board.current_player = board.get_opponent()
    return valid


class TestDotsAndBoxesGame(unittest.TestCase):
    def test_game_instance(self):
        game = Game().get_instance()
        self.assertTrue(game)

    def test_game_board(self):
        game  = Game().get_instance()
        self.assertTrue(game.game_board)

    def test_valid_move(self):
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        self.assertTrue(make_move(board, 0, 0, "right"))
        self.assertTrue(make_move(board, 0, 0, "down"))
        self.assertTrue(make_move(board, 1, 0, "right"))
        self.assertTrue(make_move(board, 0, 1, "down"))

    def test_invalid_move(self):
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")

        self.assertFalse(make_move(board, 0, 0, "right"))
        self.assertFalse(make_move(board, 100, 0, "down"))
        self.assertFalse(make_move(board, 0, -1, "up"))

    def test_completed_box(self):
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")
        make_move(board, 0, 0, "down")
        make_move(board, 0, 1, "down")
        make_move(board, 1, 0, "right")

        self.assertEqual(board.current_player, board.min_symbol)
        self.assertEqual(board.min_score, 1)

    def test_undo_move(self):
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")
        board.undo_move(0, 0, "right")

        self.assertTrue(make_move(board, 0, 0, "right"))

    def test_finished_game(self):
        Game.game_board = Board()
        game            = Game().get_instance()
        board           = game.game_board

        make_move(board, 0, 0, "right")
        make_move(board, 0, 1, "right")
        make_move(board, 0, 2, "right")
        make_move(board, 1, 0, "right")
        make_move(board, 1, 1, "right")
        make_move(board, 1, 2, "right")
        make_move(board, 2, 0, "right")
        make_move(board, 2, 1, "right")
        make_move(board, 2, 2, "right")
        make_move(board, 3, 0, "right")
        make_move(board, 3, 1, "right")
        make_move(board, 3, 2, "right")

        make_move(board, 0, 0, "down")
        make_move(board, 0, 1, "down")
        make_move(board, 0, 2, "down")
        make_move(board, 0, 3, "down")
        make_move(board, 1, 0, "down")
        make_move(board, 1, 1, "down")
        make_move(board, 1, 2, "down")
        make_move(board, 1, 3, "down")
        make_move(board, 2, 0, "down")
        make_move(board, 2, 1, "down")
        make_move(board, 2, 2, "down")
        make_move(board, 2, 3, "down")

        self.assertTrue(board.is_finished())


if __name__ == '__main__':
    unittest.main()
