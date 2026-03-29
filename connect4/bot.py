import random
from math import inf

from connect4.board import Board


def evaluate(board: Board, player_id: int) -> float:
    """Module-level pure function. Only reads the board, never mutates it."""
    opponent_id = 3 - player_id
    score = 0.0

    # Center preference
    center_col = board.cols // 2
    for row in range(board.rows):
        if board.grid[row][center_col] == player_id:
            score += 6

    # Window scoring: scan all connect_n windows in 4 directions
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    n = board.connect_n

    for r in range(board.rows):
        for c in range(board.cols):
            for dr, dc in directions:
                # Check if window fits on the board
                end_r = r + dr * (n - 1)
                end_c = c + dc * (n - 1)
                if not (0 <= end_r < board.rows and 0 <= end_c < board.cols):
                    continue

                window = [board.grid[r + dr * i][c + dc * i] for i in range(n)]
                own = window.count(player_id)
                opp = window.count(opponent_id)
                empty = window.count(0)

                if own == n - 1 and empty == 1:
                    score += 25
                elif own == n - 2 and empty == 2:
                    score += 10
                elif own >= 1 and opp == 0:
                    score += 1

                if opp == n - 1 and empty == 1:
                    score -= 20

    return score


class MinimaxBot:
    def __init__(self, name: str = "Bot", depth: int = 4):
        self.name = name
        self.depth = depth
        self.player_id = 0  # set by Game before play starts
        self.opponent_id = 0  # set by Game before play starts

    def get_move(self, board: Board) -> int:
        """Run minimax on each valid column, return the column with the highest score.

        Ties broken randomly.
        """
        valid_moves = board.get_valid_moves()
        best_score = -inf
        best_cols: list[int] = []

        for col in valid_moves:
            board.drop_disc(col, self.player_id)
            score = self._minimax(board, self.depth - 1, False, -inf, +inf)
            board.undo_move(col)

            if score > best_score:
                best_score = score
                best_cols = [col]
            elif score == best_score:
                best_cols.append(col)

        return random.choice(best_cols)

    def _minimax(
        self,
        board: Board,
        depth: int,
        is_maximizing: bool,
        alpha: float,
        beta: float,
    ) -> float:
        """Recursive minimax with alpha-beta pruning."""
        winner = board.check_winner()
        if winner == self.player_id:
            return +10000
        if winner == self.opponent_id:
            return -10000
        if board.is_full():
            return 0

        if depth == 0:
            return evaluate(board, self.player_id)

        if is_maximizing:
            max_score = -inf
            for col in board.get_valid_moves():
                board.drop_disc(col, self.player_id)
                score = self._minimax(board, depth - 1, False, alpha, beta)
                board.undo_move(col)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = +inf
            for col in board.get_valid_moves():
                board.drop_disc(col, self.opponent_id)
                score = self._minimax(board, depth - 1, True, alpha, beta)
                board.undo_move(col)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return min_score
