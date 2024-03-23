from game_logic.game import Game
import unittest


def make_move(board, x, y, direction):
    valid = board.make_move(x, y, direction)
    if valid and not board.completed_box:
        board.current_player = board.get_opponent()
    return valid

class TestDotsAndBoxesGame(unittest.TestCase):
    def test_complted_box(self):
        game  = Game().get_instance()
        board = game.game_board

        make_move(board, 0, 0, "right")
        make_move(board, 0, 0, "down")
        make_move(board, 0, 1, "down")
        make_move(board, 1, 0, "right")

        self.assertEqual(board.current_player, board.min_symbol)
        self.assertEqual(board.min_score, 1)

    def test_invalid_move(self):
        game  = Game().get_instance()
        board = game.game_board

        make_move(board, 0, 0, "right")

        self.assertFalse(make_move(board, 0, 0, "right"))
        self.assertFalse(make_move(board, 100, 0, "down"))
        self.assertFalse(make_move(board, 0, -1, "up"))

    def test_undo_move(self):
        game  = Game().get_instance()
        board = game.game_board

        make_move(board, 0, 0, "right")
        board.undo_move(0, 0, "right")

        self.assertTrue(make_move(board, 0, 0, "right"))

if __name__ == '__main__':
    unittest.main()
