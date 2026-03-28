import pytest

from connect4.board import Board

# --- __init__ ---


class TestBoardInit:
    def test_default_board_dimensions(self):
        b = Board()
        assert b.rows == 6
        assert b.cols == 7
        assert b.connect_n == 4

    def test_default_board_all_zeros(self):
        b = Board()
        for row in b.grid:
            assert all(cell == 0 for cell in row)

    def test_custom_board_dimensions(self):
        b = Board(rows=3, cols=3, connect_n=3)
        assert b.rows == 3
        assert b.cols == 3

    def test_custom_board_all_zeros(self):
        b = Board(rows=3, cols=3, connect_n=3)
        for row in b.grid:
            assert all(cell == 0 for cell in row)

    def test_connect_n_too_large_raises_value_error(self):
        with pytest.raises(ValueError):
            Board(rows=3, cols=3, connect_n=4)

    def test_connect_n_equals_max_is_valid(self):
        b = Board(rows=3, cols=3, connect_n=3)
        assert b.connect_n == 3

    def test_rows_are_independent(self):
        b = Board(rows=3, cols=3, connect_n=3)
        b.grid[0][0] = 99
        assert b.grid[1][0] == 0
        assert b.grid[2][0] == 0


# --- drop_piece ---


class TestDropPiece:
    def test_drop_into_empty_column_lands_at_bottom(self):
        b = Board()
        row = b.drop_piece(0, 1)
        assert row == b.rows - 1
        assert b.grid[b.rows - 1][0] == 1

    def test_drop_two_pieces_same_column(self):
        b = Board()
        b.drop_piece(0, 1)
        row = b.drop_piece(0, 2)
        assert row == b.rows - 2
        assert b.grid[b.rows - 2][0] == 2

    def test_fill_column_then_drop_returns_none(self):
        b = Board(rows=3, cols=3, connect_n=3)
        b.drop_piece(0, 1)
        b.drop_piece(0, 2)
        b.drop_piece(0, 1)
        result = b.drop_piece(0, 2)
        assert result is None

    def test_player_value_correctly_placed(self):
        b = Board()
        b.drop_piece(3, 2)
        assert b.grid[b.rows - 1][3] == 2


# --- is_valid_move ---


class TestIsValidMove:
    def test_empty_column_is_valid(self):
        b = Board()
        assert b.is_valid_move(0) is True

    def test_full_column_is_invalid(self):
        b = Board(rows=3, cols=3, connect_n=3)
        for _ in range(3):
            b.drop_piece(0, 1)
        assert b.is_valid_move(0) is False

    def test_negative_col_is_invalid(self):
        b = Board()
        assert b.is_valid_move(-1) is False

    def test_col_out_of_range_is_invalid(self):
        b = Board()
        assert b.is_valid_move(b.cols) is False


# --- check_winner ---


class TestCheckWinner:
    def test_horizontal_winner(self):
        b = Board()
        for c in range(4):
            b.drop_piece(c, 1)
        assert b.check_winner() == 1

    def test_vertical_winner(self):
        b = Board()
        for _ in range(4):
            b.drop_piece(0, 1)
        assert b.check_winner() == 1

    def test_diagonal_down_right_winner(self):
        # Build diagonal ↘: player 1 at (2,0),(3,1),(4,2),(5,3)
        b = Board()
        # Fill cells below the diagonal with player 2 as "padding"
        # col 0: drop 4 times so player 1 lands at row 2
        for _ in range(3):
            b.drop_piece(0, 2)
        b.drop_piece(0, 1)  # row 2
        # col 1: drop 3 times so player 1 lands at row 3
        for _ in range(2):
            b.drop_piece(1, 2)
        b.drop_piece(1, 1)  # row 3
        # col 2: drop 2 times so player 1 lands at row 4
        b.drop_piece(2, 2)
        b.drop_piece(2, 1)  # row 4
        # col 3: drop 1 time so player 1 lands at row 5
        b.drop_piece(3, 1)  # row 5
        assert b.check_winner() == 1

    def test_diagonal_up_right_winner(self):
        # Build diagonal ↗: player 1 at (5,0),(4,1),(3,2),(2,3)
        b = Board()
        b.drop_piece(0, 1)  # row 5
        b.drop_piece(1, 2)
        b.drop_piece(1, 1)  # row 4
        b.drop_piece(2, 2)
        b.drop_piece(2, 2)
        b.drop_piece(2, 1)  # row 3
        b.drop_piece(3, 2)
        b.drop_piece(3, 2)
        b.drop_piece(3, 2)
        b.drop_piece(3, 1)  # row 2
        assert b.check_winner() == 1

    def test_only_three_in_a_row_returns_none(self):
        b = Board()
        for c in range(3):
            b.drop_piece(c, 1)
        assert b.check_winner() is None

    def test_win_at_board_edge(self):
        # Top row win
        b = Board(rows=4, cols=5, connect_n=4)
        # Fill columns 0-3 so player 1 can get to top row
        for col in range(4):
            for _ in range(3):
                b.drop_piece(col, 2)
            b.drop_piece(col, 1)  # top row
        assert b.check_winner() == 1

    def test_custom_connect_n_3_wins(self):
        b = Board(rows=4, cols=4, connect_n=3)
        for c in range(3):
            b.drop_piece(c, 1)
        assert b.check_winner() == 1

    def test_custom_connect_n_5_with_only_4_returns_none(self):
        b = Board(rows=6, cols=7, connect_n=5)
        for c in range(4):
            b.drop_piece(c, 1)
        assert b.check_winner() is None

    def test_empty_board_returns_none(self):
        b = Board()
        assert b.check_winner() is None

    def test_player_2_wins(self):
        b = Board()
        for c in range(4):
            b.drop_piece(c, 2)
        assert b.check_winner() == 2


# --- is_full ---


class TestIsFull:
    def test_empty_board_not_full(self):
        b = Board()
        assert b.is_full() is False

    def test_partially_filled_not_full(self):
        b = Board()
        b.drop_piece(0, 1)
        assert b.is_full() is False

    def test_completely_filled_is_full(self):
        b = Board(rows=2, cols=2, connect_n=2)
        for c in range(2):
            for _ in range(2):
                b.drop_piece(c, 1)
        assert b.is_full() is True


# --- get_valid_moves ---


class TestGetValidMoves:
    def test_empty_board_all_columns(self):
        b = Board()
        assert b.get_valid_moves() == list(range(b.cols))

    def test_one_column_full(self):
        b = Board(rows=3, cols=3, connect_n=3)
        for _ in range(3):
            b.drop_piece(0, 1)
        valid = b.get_valid_moves()
        assert 0 not in valid
        assert 1 in valid
        assert 2 in valid

    def test_all_columns_full_returns_empty(self):
        b = Board(rows=2, cols=2, connect_n=2)
        for c in range(2):
            for _ in range(2):
                b.drop_piece(c, 1)
        assert b.get_valid_moves() == []


# --- undo_move ---


class TestUndoMove:
    def test_drop_then_undo_is_empty(self):
        b = Board()
        b.drop_piece(0, 1)
        b.undo_move(0)
        assert b.grid[b.rows - 1][0] == 0

    def test_drop_two_undo_one_removes_top(self):
        b = Board()
        b.drop_piece(0, 1)
        b.drop_piece(0, 2)
        b.undo_move(0)
        # Top piece (row rows-2) should be gone, bottom (row rows-1) still there
        assert b.grid[b.rows - 2][0] == 0
        assert b.grid[b.rows - 1][0] == 1

    def test_drop_undo_drop_lands_same_row(self):
        b = Board()
        row1 = b.drop_piece(0, 1)
        b.undo_move(0)
        row2 = b.drop_piece(0, 2)
        assert row1 == row2
