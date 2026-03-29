from connect4.board import Board
from connect4.bot import MinimaxBot, evaluate

# --- evaluate() ---


class TestEvaluate:
    def test_empty_board_score_is_zero_or_near(self):
        b = Board()
        score = evaluate(b, 1)
        # Empty board: no center discs, no windows with discs -> score == 0
        assert score == 0

    def test_center_column_gives_positive_score(self):
        b = Board()
        center = b.cols // 2
        b.drop_disc(center, 1)
        score = evaluate(b, 1)
        # Center bonus of 6, plus window bonuses
        assert score > 0

    def test_three_in_a_row_with_open_end_gives_high_score(self):
        b = Board()
        # Place 3 discs in a row for player 1 (columns 0,1,2 leaving 3 open)
        for c in range(3):
            b.drop_disc(c, 1)
        score = evaluate(b, 1)
        assert score > 0

    def test_opponent_three_in_a_row_gives_negative_penalty(self):
        b = Board()
        # Place 3 discs for opponent (player 2) in columns 0,1,2
        for c in range(3):
            b.drop_disc(c, 2)
        score_for_player1 = evaluate(b, 1)
        empty_score = evaluate(Board(), 1)
        assert score_for_player1 < empty_score


# --- MinimaxBot.get_move() — Win detection ---


class TestBotWinDetection:
    def _make_bot(self, player_id: int, depth: int = 4) -> MinimaxBot:
        bot = MinimaxBot(depth=depth)
        bot.player_id = player_id
        bot.opponent_id = 3 - player_id
        return bot

    def test_bot_wins_horizontally(self):
        """Bot has 3 in a row, 4th slot open — should play winning column."""
        b = Board()
        bot = self._make_bot(player_id=1)
        # Place 3 discs for bot at columns 0,1,2 (row 5)
        b.drop_disc(0, 1)
        b.drop_disc(1, 1)
        b.drop_disc(2, 1)
        # Column 3 is the winning move
        move = bot.get_move(b)
        assert move == 3

    def test_bot_wins_vertically(self):
        """Bot has 3 in a column, should play to complete 4."""
        b = Board()
        bot = self._make_bot(player_id=1)
        # Drop 3 discs into column 0
        b.drop_disc(0, 1)
        b.drop_disc(0, 1)
        b.drop_disc(0, 1)
        # Winning move is column 0 (4th disc)
        move = bot.get_move(b)
        assert move == 0

    def test_bot_wins_diagonally(self):
        """Bot has 3 diagonal discs, should complete the diagonal."""
        b = Board()
        bot = self._make_bot(player_id=1, depth=3)
        # Build diagonal ↘: player 1 at rows 5,4,3 for cols 0,1,2
        # We need to set up so col 3 is the winning move at row 2
        b.drop_disc(0, 1)  # (5,0)
        b.drop_disc(1, 2)
        b.drop_disc(1, 1)  # (4,1)
        b.drop_disc(2, 2)
        b.drop_disc(2, 2)
        b.drop_disc(2, 1)  # (3,2)
        # Col 3 needs 3 padding discs so player 1 lands at row 2
        b.drop_disc(3, 2)
        b.drop_disc(3, 2)
        b.drop_disc(3, 2)
        # Now playing col 3 places player 1 at (2,3) completing the diagonal
        move = bot.get_move(b)
        assert move == 3


# --- MinimaxBot.get_move() — Block opponent ---


class TestBotBlocking:
    def _make_bot(self, player_id: int, depth: int = 4) -> MinimaxBot:
        bot = MinimaxBot(depth=depth)
        bot.player_id = player_id
        bot.opponent_id = 3 - player_id
        return bot

    def test_bot_blocks_horizontal_threat(self):
        """Opponent has 3 in a row horizontally, bot should block."""
        b = Board()
        bot = self._make_bot(player_id=2)
        # Opponent (player 1) has discs at columns 0,1,2
        b.drop_disc(0, 1)
        b.drop_disc(1, 1)
        b.drop_disc(2, 1)
        # Bot must play column 3 to block
        move = bot.get_move(b)
        assert move == 3

    def test_bot_blocks_vertical_threat(self):
        """Opponent has 3 in a column, bot should block on top."""
        b = Board()
        bot = self._make_bot(player_id=2)
        # Opponent (player 1) has 3 in column 0
        b.drop_disc(0, 1)
        b.drop_disc(0, 1)
        b.drop_disc(0, 1)
        # Bot must play column 0 to block
        move = bot.get_move(b)
        assert move == 0


# --- Edge cases ---


class TestBotEdgeCases:
    def _make_bot(self, player_id: int, depth: int = 4) -> MinimaxBot:
        bot = MinimaxBot(depth=depth)
        bot.player_id = player_id
        bot.opponent_id = 3 - player_id
        return bot

    def test_only_one_valid_move(self):
        """Only one column available — bot must pick it."""
        b = Board(rows=2, cols=2, connect_n=2)
        bot = self._make_bot(player_id=1, depth=2)
        # Fill column 0 completely
        b.drop_disc(0, 2)
        b.drop_disc(0, 2)
        # Only column 1 remains
        move = bot.get_move(b)
        assert move == 1

    def test_custom_connect_n_3_wins(self):
        """With connect_n=3, bot should take the immediate winning move at depth=1."""
        b = Board(rows=4, cols=4, connect_n=3)
        # Use depth=1 so bot only sees the immediate next move
        bot = MinimaxBot(depth=1)
        bot.player_id = 1
        bot.opponent_id = 2
        # Bot has 2 in a row; col 2 is the only immediate win (horizontal)
        b.drop_disc(0, 1)
        b.drop_disc(1, 1)
        move = bot.get_move(b)
        # At depth=1 the only winning move is col 2
        assert move == 2


# --- Bot vs Bot integration ---


class TestBotVsBot:
    def test_deeper_bot_wins_more(self):
        """depth=4 bot should beat depth=2 bot more often than not."""
        import random

        random.seed(42)

        NUM_GAMES = 5
        strong_wins = 0

        for _ in range(NUM_GAMES):
            b = Board()
            strong = MinimaxBot(name="Strong", depth=4)
            strong.player_id = 1
            strong.opponent_id = 2
            weak = MinimaxBot(name="Weak", depth=2)
            weak.player_id = 2
            weak.opponent_id = 1

            bots = [strong, weak]
            current = 0

            while True:
                bot = bots[current]
                col = bot.get_move(b)
                b.drop_disc(col, bot.player_id)
                winner = b.check_winner()
                if winner == strong.player_id:
                    strong_wins += 1
                    break
                if winner == weak.player_id:
                    break
                if b.is_full():
                    break
                current = 1 - current

        # Strong bot should win at least 3 out of 5 games
        assert strong_wins >= 3
