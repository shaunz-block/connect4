from unittest.mock import patch

from connect4.board import Board
from connect4.player import HumanPlayer


class TestHumanPlayer:
    def test_player_has_correct_name(self):
        player = HumanPlayer("Alice")
        assert player.name == "Alice"

    def test_get_move_returns_valid_int(self):
        board = Board()
        player = HumanPlayer("Alice")
        with patch("builtins.input", return_value="3"):
            col = player.get_move(board)
        assert col == 3

    def test_get_move_with_non_numeric_then_valid(self):
        board = Board()
        player = HumanPlayer("Alice")
        # First input is invalid, second is valid
        with patch("builtins.input", side_effect=["abc", "2"]):
            col = player.get_move(board)
        assert col == 2

    def test_get_move_multiple_invalid_then_valid(self):
        board = Board()
        player = HumanPlayer("Bob")
        with patch("builtins.input", side_effect=["x", "y", "z", "5"]):
            col = player.get_move(board)
        assert col == 5
