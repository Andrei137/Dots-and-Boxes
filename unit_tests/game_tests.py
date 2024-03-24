from src.game_logic.board import Board
from src.game_logic.game import Game
from copy import deepcopy
import unittest


class TestDotsAndBoxesGame(unittest.TestCase):
    def test_game_initial_state(self):
        Game.reset()
        game = Game().get_instance()
        board = game.game_board

        self.assertEqual(board, Board())
        self.assertEqual(board.current_player, Board.max_symbol)
        self.assertEqual(board.min_score, 0)
        self.assertEqual(board.max_score, 0)
        self.assertEqual(board.completed_box, False)

        self.assertEqual(game.match_number, 1)
        self.assertEqual(str(game.algorithm), "Alpha Beta")
        self.assertEqual(str(game.difficulty), "Medium")
        self.assertEqual(game.player_symbol, Board.max_symbol)
        self.assertEqual(game.pvp, False)
        self.assertEqual(game.gui, True)


if __name__ == '__main__':
    unittest.main()
