import pytest

from connect4.game import Game


class ScriptedPlayer:
    """A player that returns pre-scripted moves."""

    def __init__(self, name: str, moves: list[int]):
        self.name = name
        self._moves = iter(moves)

    def get_move(self, board):
        return next(self._moves)


class TestGameP1Win:
    def test_scripted_p1_win(self, capsys):
        """Player 1 wins by placing 4 in a row horizontally at bottom row."""
        # Turn sequence: p1->0, p2->0, p1->1, p2->1, p1->2, p2->2, p1->3
        # After this, p1 has pieces at (5,0),(5,1),(5,2),(5,3) → horizontal win
        p1 = ScriptedPlayer("Alice", [0, 1, 2, 3])
        p2 = ScriptedPlayer("Bob", [0, 1, 2])

        game = Game(p1, p2)
        game.play()

        captured = capsys.readouterr()
        assert "Alice wins!" in captured.out


class TestGameDraw:
    def test_scripted_draw(self, capsys):
        """Fill a 4x3 board with connect_n=4 (no possible winner), should draw.

        Board pattern (connect_n=4 means no 4-in-a-row possible on a 3-col board):
        O X O
        X O X
        O X O
        X O X
        Players alternate filling column by column, producing a checkerboard.
        """
        # 4 rows x 3 cols = 12 cells. Turn sequence (p1=odd turns, p2=even):
        # cols: 0,1,2,0,1,2,0,1,2,0,1,2
        # p1 plays: 0,2,1,0,2,1  p2 plays: 1,0,2,1,0,2
        p1 = ScriptedPlayer("Alice", [0, 2, 1, 0, 2, 1])
        p2 = ScriptedPlayer("Bob", [1, 0, 2, 1, 0, 2])

        game = Game(p1, p2, rows=4, cols=3, connect_n=4)
        game.play()

        captured = capsys.readouterr()
        assert "draw" in captured.out.lower()


class TestGameInvalidMove:
    def test_invalid_move_re_prompts(self, capsys):
        """Player gives an invalid move first (col 99), then valid moves."""
        # Turn sequence: p1->99 (invalid), p1->0, p2->0, p1->1, p2->1, p1->2, p2->2, p1->3
        p1 = ScriptedPlayer("Alice", [99, 0, 1, 2, 3])
        p2 = ScriptedPlayer("Bob", [0, 1, 2])

        game = Game(p1, p2)
        game.play()

        captured = capsys.readouterr()
        assert "Invalid move" in captured.out
        assert "Alice wins!" in captured.out
