# Connect N — Design Document

## 1. Overview

A configurable Connect N game implemented as a Python package. Two players take turns dropping pieces into a vertical grid. The first player to align N pieces in a row (horizontal, vertical, or diagonal) wins.

### Scope (v1)

- Configurable board size (default 6×7)
- Configurable win condition (default Connect 4)
- Human vs Human mode
- Human vs Bot mode (Minimax AI with configurable depth)
- Terminal-based UI

---

## 2. Package Structure

```
connect4/
├── __init__.py          # Public API exports
├── board.py             # Board class — state + rules
├── player.py            # Player protocol + HumanPlayer
├── bot.py               # MinimaxBot — with configurable depth
├── game.py              # Game loop orchestration
tests/
├── __init__.py
├── test_board.py        # Unit tests for Board
├── test_player.py       # Unit tests for Player
├── test_bot.py          # Unit tests for MinimaxBot + evaluate
├── test_game.py         # Integration tests
pyproject.toml           # Package config
```

---

## 3. Module Design

### 3.1 board.py — Board Class

The Board encapsulates grid state and all rule logic. Config (rows, cols, connect_n) is bound at creation time to prevent inconsistency.

```python
class Board:
    def __init__(self, rows: int = 6, cols: int = 7, connect_n: int = 4):
        """
        Initialize empty board.
        Raises ValueError if connect_n > max(rows, cols).
        """
        self.rows = rows
        self.cols = cols
        self.connect_n = connect_n
        self.grid: list[list[int]] = [[0] * cols for _ in range(rows)]

    def drop_piece(self, col: int, player: int) -> int | None:
        """
        Drop a piece into the given column.
        Returns the row where it landed, or None if the column is full.
        Does NOT validate col range — caller should use is_valid_move() first.
        """

    def is_valid_move(self, col: int) -> bool:
        """
        Check if col is within range AND the column is not full.
        """

    def check_winner(self) -> int | None:
        """
        Scan the board for connect_n in a row.
        Returns the winning player number (1 or 2), or None.
        Checks 4 directions: horizontal, vertical, diagonal ↘, diagonal ↗.
        """

    def is_full(self) -> bool:
        """
        Returns True if every column is full (draw condition).
        """

    def get_valid_moves(self) -> list[int]:
        """
        Returns list of column indices that can still accept a piece.
        Useful for AI players later.
        """

    def undo_move(self, col: int) -> None:
        """
        Remove the topmost piece from the given column.
        Used by minimax to efficiently explore/backtrack
        without copying the entire board.
        """

    def print_board(self) -> None:
        """
        Print the board to terminal with column numbers.
        Player 1 = 'X', Player 2 = 'O', Empty = '.'
        """
```

**Design decisions:**

- `grid[0]` is the TOP row, `grid[rows-1]` is the BOTTOM row. `drop_piece` scans from bottom up.
- Player values are 1 and 2 (not 0, since 0 = empty).
- `check_winner` scans every cell as a potential starting point, checking rightward, downward, and both diagonals. Only needs to check in "positive" directions to avoid double-counting.
- `drop_piece` mutates the grid in place and returns the row. Returns None (not raises) for full column — this allows the game loop to re-prompt gracefully.

### 3.2 player.py — Player Protocol

Uses Python's Protocol for structural subtyping (duck typing with type safety).

```python
from typing import Protocol

class Player(Protocol):
    """Any object with a name and get_move method qualifies as a Player."""
    name: str

    def get_move(self, board: "Board") -> int:
        """Return the column index to drop a piece into."""
        ...

class HumanPlayer:
    def __init__(self, name: str):
        self.name = name

    def get_move(self, board: "Board") -> int:
        """
        Prompt the user for input. Keeps asking until a valid integer is entered.
        Does NOT validate whether the move is legal on the board — 
        that's the game loop's job.
        """
```

**Why Protocol over ABC:**

- No forced inheritance — any class with `name` + `get_move` works
- Better for testing — easy to create mock players
- More Pythonic (duck typing)

**Future players:**

Any class implementing `name` + `get_move` can be plugged in.

### 3.3 bot.py — MinimaxBot

A single bot class that uses minimax search with alpha-beta pruning. The `depth` parameter controls strength: low depth behaves like a heuristic bot, high depth plays near-optimally.

```python
class MinimaxBot:
    def __init__(self, name: str = "Bot", depth: int = 4):
        self.name = name
        self.depth = depth
        self.piece = 0        # set by Game before play starts
        self.opponent = 0     # set by Game before play starts

    def get_move(self, board: "Board") -> int:
        """
        Run minimax on each valid column, return the column
        with the highest score. Ties broken randomly.
        """

    def _minimax(self, board: "Board", depth: int,
                 is_maximizing: bool, alpha: float, beta: float) -> float:
        """
        Recursive minimax with alpha-beta pruning.
        - Maximizing player = bot (wants highest score)
        - Minimizing player = opponent (wants lowest score)
        """

    def evaluate(board: "Board", player: int) -> float:
        """
        Pure static evaluation of a board position. Module-level function.
        Does NOT simulate any moves — only reads current grid state.
        Called at minimax leaf nodes (depth == 0, game not over).

        Scoring components:
          - Center preference: pieces near center columns score higher
          - Window scoring: scan all connect_n windows in 4 directions
        """
```

#### Why one class instead of separate Heuristic + Minimax bots

Minimax naturally subsumes heuristic evaluation:

```
depth=0  →  evaluate(board) only            (pure static)
depth=2  →  ≈ heuristic bot (win/block detection emerges from search)
depth=4  →  strong AI (sees traps 2 moves ahead)
depth=6+ →  very strong AI (near-optimal play)
```

#### Minimax algorithm

```python
def _minimax(board, depth, is_maximizing, alpha, beta):
    # Terminal checks
    winner = board.check_winner()
    if winner == self.piece:    return +10000
    if winner == self.opponent: return -10000
    if board.is_full():         return 0

    # Depth limit — use static evaluation
    if depth == 0:
        return evaluate(board, self.piece)

    if is_maximizing:
        max_score = -inf
        for col in board.get_valid_moves():
            board.drop_piece(col, self.piece)
            score = _minimax(board, depth - 1, False, alpha, beta)
            board.undo_move(col)           # backtrack, no deepcopy needed
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break                      # β cutoff
        return max_score

    else:  # minimizing
        min_score = +inf
        for col in board.get_valid_moves():
            board.drop_piece(col, self.opponent)
            score = _minimax(board, depth - 1, True, alpha, beta)
            board.undo_move(col)
            min_score = min(min_score, score)
            beta = min(beta, score)
            if alpha >= beta:
                break                      # α cutoff
        return min_score
```

Key points:
- Uses `board.undo_move()` instead of deepcopy — much faster.
- Alpha-beta pruning cuts branches that can't affect the final decision.
- Terminal states (+10000/-10000/0) are exact; evaluate() is an approximation.
- `get_move()` calls `_minimax(depth-1, False, ...)` for each valid column and picks the max.

#### evaluate() — Static board evaluation

A module-level pure function. Only reads the board, never mutates it.

```python
def evaluate(board, player) -> float:
    opponent = 3 - player  # if player=1 then opponent=2, vice versa
    score = 0

    # Center preference
    center_col = board.cols // 2
    for row in range(board.rows):
        if board.grid[row][center_col] == player:
            score += 6

    # Window scoring: scan all connect_n windows in 4 directions
    for each window of length connect_n on the board:
        own   = count of player pieces in window
        opp   = count of opponent pieces in window
        empty = count of empty cells in window

        if own == connect_n - 1 and empty == 1:
            score += 25     # one away from winning
        elif own == connect_n - 2 and empty == 2:
            score += 10     # building a threat
        elif own >= 1 and opp == 0:
            score += 1      # some presence

        if opp == connect_n - 1 and empty == 1:
            score -= 20     # opponent one away (defensive)

    return score
```

Note: evaluate scores from `player`'s perspective. A positive score means the position favors `player`. The window scan covers the entire board, not just the last move — this is correct for a static evaluation where we don't know which move led here.

#### Depth selection guidelines

| depth | nodes (approx) | time   | strength                          |
|-------|----------------|--------|-----------------------------------|
| 2     | ~50            | <1ms   | Basic: sees immediate win/block   |
| 4     | ~2,400         | ~5ms   | Good: sees simple traps           |
| 6     | ~120,000       | ~50ms  | Strong: sees most tactical combos |
| 8     | ~5,800,000     | ~2s    | Very strong, noticeable delay     |

Default depth=4 balances speed and strength for casual play.

### 3.4 game.py — Game Orchestration

```python
class Game:
    def __init__(self, player1: Player, player2: Player,
                 rows: int = 6, cols: int = 7, connect_n: int = 4):
        self.board = Board(rows, cols, connect_n)
        self.players = [player1, player2]
        self.current_turn = 0  # index into self.players

    def _setup_players(self) -> None:
        """
        Assign piece/opponent info to MinimaxBots.
        Called once before the game loop starts.
        Uses hasattr check — HumanPlayers don't need this.
        """
        for i, player in enumerate(self.players):
            if hasattr(player, 'piece'):
                player.piece = i + 1        # 1 or 2
                player.opponent = 2 - i      # 2 or 1

    def play(self) -> None:
        """
        Main game loop:
        0. Setup bot players (assign piece numbers)
        1. Print board
        2. Get move from current player
        3. Validate move (re-prompt if invalid)
        4. Drop piece
        5. Check for winner → announce and stop
        6. Check for full board → announce draw and stop
        7. Switch player, repeat
        """

    def _switch_player(self) -> None:
        self.current_turn = 1 - self.current_turn

    @property
    def current_player(self) -> Player:
        return self.players[self.current_turn]

    @property
    def current_piece(self) -> int:
        return self.current_turn + 1  # 1 or 2
```

**Separation of concerns:**

| Responsibility       | Owner       |
|----------------------|-------------|
| Grid state + rules   | Board       |
| Choosing a move      | Player/Bot  |
| Search + pruning     | MinimaxBot  |
| Static evaluation    | evaluate()  |
| Validating + looping | Game        |

The Game doesn't know how a player decides. The Player doesn't know the rules. The Board doesn't know about players or turns.

---

## 4. Key Algorithms

### 4.1 drop_piece — Gravity Simulation

```
scan from row = rows-1 (bottom) up to row = 0 (top):
    if grid[row][col] == 0:
        grid[row][col] = player
        return row
return None  # column is full
```

### 4.2 check_winner — Direction Scanning

For each cell (r, c) that is non-zero:
- Check 4 directions: right (0,1), down (1,0), diagonal-down-right (1,1), diagonal-down-left (1,-1)
- For each direction, count consecutive same-player pieces
- If count >= connect_n, that player wins

Only checking "positive" directions avoids double-counting. We don't need to check left, up, etc.

### 4.3 is_valid_move

```
return 0 <= col < self.cols and self.grid[0][col] == 0
```

Checking `grid[0][col]` (top row) is sufficient — if the top is empty, there's room.

### 4.4 undo_move

```
scan from row = 0 (top) down to row = rows-1 (bottom):
    if grid[row][col] != 0:
        grid[row][col] = 0
        return
```

The inverse of `drop_piece`. Finds the topmost piece in a column and removes it.

### 4.5 Minimax — Recursive Search

The minimax tree alternates between maximizing (bot's turn) and minimizing (opponent's turn). At each node:

```
                     bot picks max
                    /      |      \
                col 0    col 3    col 6
                /          |          \
          opp picks min  opp picks min  opp picks min
          /    \          /    \         /    \
       col 0  col 1   col 0  col 1   col 0  col 1
         |      |       |      |       |      |
       leaf   leaf    leaf   leaf    leaf   leaf
       eval   eval    eval   eval    eval   eval
```

Three types of leaf nodes:
- **Terminal win/loss**: `check_winner()` returns a player → ±10000
- **Terminal draw**: `is_full()` → 0
- **Depth limit**: game still going → `evaluate(board, player)`

### 4.6 Alpha-Beta Pruning

Alpha = best score the maximizer can guarantee so far.
Beta = best score the minimizer can guarantee so far.

When `alpha >= beta`, we know this branch cannot produce a better outcome than what's already found — prune it. In the best case, this reduces search from O(b^d) to O(b^(d/2)), where b = branching factor (~7) and d = depth.

### 4.7 evaluate() — Window Scoring

Scans all possible connect_n windows across the entire board in 4 directions (horizontal, vertical, two diagonals).

```
    # Window scoring: scan all connect_n windows in 4 directions
    for each window of length connect_n on the board:
        own   = count of player pieces in window
        opp   = count of opponent pieces in window
        empty = count of empty cells in window

        if own == connect_n - 1 and empty == 1:
            score += 25     # one away from winning
        elif own == connect_n - 2 and empty == 2:
            score += 10     # building a threat
        elif own >= 1 and opp == 0:
            score += 1      # some presence

        if opp == connect_n - 1 and empty == 1:
            score -= 20     # opponent one away (defensive)

    return score
```

The key insight: a window containing both players' pieces is useless to either side, so we skip it. Only "pure" windows (one player + empty cells) have strategic value.

---

## 5. Testing Strategy

### 5.1 test_board.py — Unit Tests (highest coverage)

**create_board / __init__:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Default 6×7 board                  | 6 rows, 7 cols, all zeros         |
| Custom 3×3 board                   | 3 rows, 3 cols, all zeros         |
| connect_n > max(rows, cols)        | Raises ValueError                 |
| Each row is independent (not same ref) | Modify one row, others unchanged |

**drop_piece:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Drop into empty column             | Lands at bottom row (rows-1)      |
| Drop two pieces same column        | Second piece at rows-2            |
| Fill entire column, drop one more  | Returns None                      |
| Player value is correctly placed   | grid[row][col] == player          |

**is_valid_move:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Empty column                       | True                              |
| Full column                        | False                             |
| col = -1 (below range)            | False                             |
| col = cols (above range)          | False                             |

**check_winner:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Horizontal 4-in-a-row              | Returns winning player            |
| Vertical 4-in-a-row                | Returns winning player            |
| Diagonal ↘ 4-in-a-row             | Returns winning player            |
| Diagonal ↗ 4-in-a-row             | Returns winning player            |
| Only 3-in-a-row                    | Returns None                      |
| Win at board edge (top/bottom/side)| Returns winning player            |
| Custom connect_n=3 with 3 in a row | Returns winning player            |
| Custom connect_n=5 with 4 in a row | Returns None                      |
| Empty board                        | Returns None                      |

**is_full:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Empty board                        | False                             |
| Partially filled                   | False                             |
| Completely filled                  | True                              |

**get_valid_moves:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Empty board                        | All columns [0..cols-1]           |
| One column full                    | All except that column            |
| All columns full                   | Empty list []                     |

**undo_move:**

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Drop then undo                     | Cell is empty again               |
| Drop two, undo one                 | Only top piece removed            |
| Drop, undo, drop again             | Piece lands at same row           |

### 5.2 test_player.py — Unit Tests

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| HumanPlayer returns valid int      | Mocked input returns correct col  |
| HumanPlayer with non-numeric input | Keeps prompting (mock sequence)   |
| Player has correct name attribute  | player.name == given name         |

### 5.3 test_bot.py — Unit Tests

Tests for both MinimaxBot behavior and the evaluate() function.

**evaluate():**

| Test Case                                    | Expected                           |
|----------------------------------------------|------------------------------------|
| Empty board                                  | score ≈ 0                          |
| Center column has player pieces              | Positive score (center bonus)      |
| Player has 3-in-a-row with open end          | High positive score                |
| Opponent has 3-in-a-row with open end        | Negative score (defensive penalty) |
| Board with equal positions for both          | score ≈ 0                          |

**MinimaxBot.get_move() — Win detection (emerges from search):**

| Test Case                              | Expected                          |
|----------------------------------------|-----------------------------------|
| Bot has 3 in a row, 4th slot open      | Bot plays the winning column      |
| Bot can win vertically                 | Bot plays the winning column      |
| Bot can win diagonally                 | Bot plays the winning column      |

**MinimaxBot.get_move() — Block opponent (emerges from search):**

| Test Case                              | Expected                          |
|----------------------------------------|-----------------------------------|
| Opponent has 3 in a row horizontally   | Bot blocks the 4th slot           |
| Opponent has 3 in a row vertically     | Bot blocks on top                 |
| Both bot and opponent can win          | Bot prefers its own win           |

**MinimaxBot.get_move() — Depth comparison:**

| Test Case                              | Expected                          |
|----------------------------------------|-----------------------------------|
| Trap setup: depth=2 falls for it       | depth=2 picks the trap column     |
| Same trap: depth=4 avoids it           | depth=4 picks the safe column     |
| Empty board                            | Picks center column               |

**MinimaxBot.get_move() — Edge cases:**

| Test Case                              | Expected                          |
|----------------------------------------|-----------------------------------|
| Only one valid move left               | Picks it                          |
| Custom connect_n=3                     | Wins/blocks at 3 correctly        |

**Bot vs Bot (integration-level):**

| Test Case                              | Expected                          |
|----------------------------------------|-----------------------------------|
| depth=4 vs depth=2, 100 games          | depth=4 wins significantly more   |

### 5.4 test_game.py — Integration Tests

| Test Case                          | Expected                          |
|------------------------------------|-----------------------------------|
| Scripted game ending in P1 win     | Game announces P1 wins            |
| Scripted game ending in draw       | Game announces draw               |
| Invalid move → re-prompts          | Game asks again, doesn't crash    |

Use mock players that return pre-scripted move sequences.

---

## 6. Implementation Order

Build bottom-up, test each layer before moving on:

```
Phase 1: Board (foundation)
  ├── Implement Board class (including undo_move)
  ├── Write test_board.py
  └── All tests green ✓

Phase 2: Player
  ├── Define Player protocol
  ├── Implement HumanPlayer
  ├── Write test_player.py
  └── All tests green ✓

Phase 3: Bot
  ├── Implement evaluate() function
  ├── Implement MinimaxBot with alpha-beta pruning
  ├── Write test_bot.py
  ├── All tests green ✓
  └── Verify depth=4 beats depth=2 in bot-vs-bot

Phase 4: Game (integration)
  ├── Implement Game class
  ├── Wire up piece assignment for MinimaxBot
  ├── Write test_game.py
  ├── All tests green ✓
  └── Manual play-test (Human vs Human, Human vs Bot)

Phase 5: Packaging
  ├── __init__.py exports
  ├── pyproject.toml
  └── Entry point (python -m connect4)
```

---

## 7. Usage (target API)

```python
from connect4 import Game, HumanPlayer, MinimaxBot

# Human vs Human
p1 = HumanPlayer("Alice")
p2 = HumanPlayer("Bob")
game = Game(p1, p2, rows=6, cols=7, connect_n=4)
game.play()

# Human vs Bot (default depth=4)
p1 = HumanPlayer("Alice")
p2 = MinimaxBot("Bot")
game = Game(p1, p2)
game.play()

# Human vs Strong Bot
p1 = HumanPlayer("Alice")
p2 = MinimaxBot("StrongBot", depth=6)
game = Game(p1, p2)
game.play()

# Bot vs Bot — compare depths (for testing/analysis)
p1 = MinimaxBot("Shallow", depth=2)
p2 = MinimaxBot("Deep", depth=6)
game = Game(p1, p2)
game.play()
```

Or from command line:

```bash
python -m connect4                  # Human vs Human (default)
python -m connect4 --bot            # Human vs Bot (depth=4)
python -m connect4 --bot --depth 6  # Human vs Strong Bot
```
