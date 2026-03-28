# Connect N

A configurable Connect N game implemented as a Python package. Two players take turns dropping pieces into a vertical grid. The first player to align N pieces in a row (horizontal, vertical, or diagonal) wins. Defaults to the classic Connect 4 rules on a 6×7 board.

## Features

- Configurable board size and win condition (default: 6×7, Connect 4)
- Human vs Human mode
- Human vs Bot mode — Minimax AI with alpha-beta pruning and configurable depth
- Terminal-based UI

## Project Structure

```
connect4/
├── __init__.py       # Public API exports
├── board.py          # Board class — grid state and all rule logic
├── player.py         # Player protocol + HumanPlayer
├── bot.py            # MinimaxBot with alpha-beta pruning + evaluate()
├── game.py           # Game loop orchestration
└── __main__.py       # CLI entry point
tests/
├── __init__.py
├── test_board.py     # Unit tests for Board (34 tests)
├── test_player.py    # Unit tests for HumanPlayer (4 tests)
├── test_bot.py       # Unit tests for MinimaxBot + evaluate (11 tests)
└── test_game.py      # Integration tests (3 tests)
pyproject.toml
DESIGN.md             # Full design document
```

## Setup

Requires Python 3.10+ and [uv](https://github.com/astral-sh/uv).

```bash
# Create virtual environment and install in editable mode with dev deps
uv venv
uv sync --extra dev
```

## Usage

### Command Line

```bash
uv run python -m connect4                       # Human vs Human (default)
uv run python -m connect4 --bot                 # Human vs Bot (depth=4)
uv run python -m connect4 --bot --depth 6       # Human vs Strong Bot
uv run python -m connect4 --rows 8 --cols 9     # Custom board size
uv run python -m connect4 --connect-n 5         # Connect 5 to win
```

Or after installing the package:

```bash
connect4 --bot --depth 6
```

### Python API

```python
from connect4 import Game, HumanPlayer, MinimaxBot

# Human vs Human
game = Game(HumanPlayer("Alice"), HumanPlayer("Bob"))
game.play()

# Human vs Bot
game = Game(HumanPlayer("Alice"), MinimaxBot("Bot", depth=4))
game.play()

# Custom board: 8×9, Connect 5
game = Game(HumanPlayer("Alice"), MinimaxBot("Bot"), rows=8, cols=9, connect_n=5)
game.play()

# Bot vs Bot
game = Game(MinimaxBot("Shallow", depth=2), MinimaxBot("Deep", depth=6))
game.play()
```

## Module Details

### `board.py` — Board

Encapsulates all grid state and rule logic. Config is bound at creation time.


| Method                    | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `drop_piece(col, player)` | Drops a piece; returns landing row or `None` if full         |
| `undo_move(col)`          | Removes the topmost piece — used by minimax for backtracking |
| `check_winner()`          | Returns winning player (1 or 2) or `None`                    |
| `is_valid_move(col)`      | `True` if column is in range and not full                    |
| `is_full()`               | `True` if every column is full (draw condition)              |
| `get_valid_moves()`       | List of playable column indices                              |
| `print_board()`           | Prints grid to terminal (`X`/`O`/`.`) with column numbers    |


Key design decisions:

- `grid[0]` is the **top** row; `grid[rows-1]` is the **bottom** row. Pieces fall from the bottom up.
- Player values are `1` and `2`; `0` means empty.
- `undo_move` enables minimax backtracking without copying the board.

### `player.py` — Player Protocol + HumanPlayer

`Player` is a `typing.Protocol` — any object with `name: str` and `get_move(board) -> int` qualifies. No inheritance required.

`HumanPlayer.get_move` prompts the terminal until a valid integer is entered. Move legality (column not full) is validated by the game loop, not the player.

### `bot.py` — MinimaxBot + evaluate()

`MinimaxBot` uses recursive minimax with alpha-beta pruning. `piece` and `opponent` are assigned by `Game._setup_players()` before the game starts.

`**evaluate(board, player)`** — module-level pure function, called at depth-limit leaf nodes:

- **Center preference**: +6 per piece in the center column
- **Window scoring**: scans every `connect_n`-length window in 4 directions:
  - `n-1` own + 1 empty → +25 (one away from winning)
  - `n-2` own + 2 empty → +10 (building a threat)
  - any own + 0 opponent → +1 (presence)
  - `n-1` opponent + 1 empty → -20 (defensive penalty)

**Bot depth guidelines:**


| depth | approx nodes | approx time | strength                      |
| ----- | ------------ | ----------- | ----------------------------- |
| 2     | ~50          | <1 ms       | Sees immediate win/block      |
| 4     | ~2,400       | ~5 ms       | Sees simple traps (default)   |
| 6     | ~120,000     | ~50 ms      | Sees most tactical combos     |
| 8     | ~5,800,000   | ~2 s        | Very strong, noticeable delay |


### `game.py` — Game

Orchestrates the game loop: setup → print board → get move → validate → drop → check win/draw → switch player.

`_setup_players()` uses `hasattr(player, 'piece')` to assign piece numbers only to bots — `HumanPlayer` is unaffected.

## Running Tests

```bash
uv run pytest
uv run pytest -v         # verbose output
uv run pytest tests/test_board.py   # single file
```

All 53 tests should pass.