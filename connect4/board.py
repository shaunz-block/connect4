class Board:
    def __init__(self, rows: int = 6, cols: int = 7, connect_n: int = 4):
        """Initialize empty board.

        Raises ValueError if connect_n > max(rows, cols).
        grid[0] is the TOP row, grid[rows-1] is the BOTTOM row.
        """
        if connect_n > max(rows, cols):
            raise ValueError(
                f"connect_n ({connect_n}) cannot be greater than max(rows, cols) ({max(rows, cols)})"
            )
        self.rows = rows
        self.cols = cols
        self.connect_n = connect_n
        self.grid: list[list[int]] = [[0] * cols for _ in range(rows)]

    def drop_piece(self, col: int, player: int) -> int | None:
        """Drop a piece into the given column.

        Returns the row where it landed, or None if the column is full.
        Does NOT validate col range — caller should use is_valid_move() first.
        """
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = player
                return row
        return None  # column is full

    def is_valid_move(self, col: int) -> bool:
        """Check if col is within range AND the column is not full."""
        return 0 <= col < self.cols and self.grid[0][col] == 0

    def check_winner(self) -> int | None:
        """Scan the board for connect_n in a row.

        Returns the winning player number (1 or 2), or None.
        Checks 4 directions: horizontal (0,1), vertical (1,0),
        diagonal down-right (1,1), diagonal up-right (1,-1).
        Only checks "positive" directions to avoid double-counting.
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.rows):
            for c in range(self.cols):
                player = self.grid[r][c]
                if player == 0:
                    continue
                for dr, dc in directions:
                    # Check if connect_n in a row starting at (r, c) in direction (dr, dc)
                    end_r = r + dr * (self.connect_n - 1)
                    end_c = c + dc * (self.connect_n - 1)
                    if not (0 <= end_r < self.rows and 0 <= end_c < self.cols):
                        continue
                    if all(
                        self.grid[r + dr * i][c + dc * i] == player for i in range(self.connect_n)
                    ):
                        return player
        return None

    def is_full(self) -> bool:
        """Returns True if every column is full (draw condition)."""
        return all(self.grid[0][c] != 0 for c in range(self.cols))

    def get_valid_moves(self) -> list[int]:
        """Returns list of column indices that can still accept a piece."""
        return [c for c in range(self.cols) if self.is_valid_move(c)]

    def undo_move(self, col: int) -> None:
        """Remove the topmost piece from the given column."""
        for row in range(self.rows):
            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                return

    def print_board(self) -> None:
        """Print the board to terminal with column numbers.

        Player 1 = 'X', Player 2 = 'O', Empty = '.'
        """
        symbols = {0: ".", 1: "X", 2: "O"}
        for row in self.grid:
            print(" ".join(symbols[cell] for cell in row))
        print(" ".join(str(c) for c in range(self.cols)))
