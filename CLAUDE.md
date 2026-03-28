# CLAUDE.md

This file provides guidance for AI coding assistants (Claude Code, Cursor, Copilot, etc.) working in this repository.

## Project Overview

A configurable Connect N game Python package. Core logic lives in `connect4/`; tests live in `tests/`. The design spec is in `DESIGN.md` — read it first for architectural intent.

## Environment Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv venv                        # create .venv
uv pip install -e ".[dev]"     # install package + dev deps (pytest)
```

**Never use bare `pip` or `python` — always prefix with `uv run`.**

## Running Tests

```bash
uv run pytest                  # all tests
uv run pytest -v               # verbose
uv run pytest tests/test_board.py   # single file
```

All 53 tests must pass before any change is considered done.

## Architecture

```
connect4/board.py    — Board class: grid state + all rule logic (no player awareness)
connect4/player.py   — Player protocol (structural typing) + HumanPlayer
connect4/bot.py      — MinimaxBot (alpha-beta) + module-level evaluate()
connect4/game.py     — Game loop: orchestration only, no rule logic
connect4/__main__.py — CLI entry point (argparse)
```

**Separation of concerns is strict:**
- `Board` knows nothing about players or turns.
- `Player`/`Bot` knows nothing about rules — only receives a board and returns a column.
- `Game` knows nothing about how moves are decided — only validates and applies them.

## Key Conventions

- `grid[0]` = **top** row; `grid[rows-1]` = **bottom** row. Pieces fall from the bottom up.
- Player values: `1` and `2`. Empty cell = `0`.
- `drop_piece` returns `None` (not raises) when a column is full — the game loop handles re-prompting.
- `undo_move` enables minimax backtracking **without deepcopy** — do not replace with board copying.
- `evaluate()` is a **pure module-level function** — it must never mutate the board.
- `MinimaxBot.piece` and `.opponent` are set by `Game._setup_players()` before `play()` — they are `0` until then.

## Adding a New Player Type

Implement `name: str` and `get_move(board: Board) -> int`. No base class needed — `Player` is a `typing.Protocol`. The game loop handles move validation; the player only needs to return a column index (integer).

## Bot Depth

Default depth is `4` (~5 ms per move). Increase for stronger play; `8` is very strong but adds ~2 s latency. The bot vs bot test uses `depth=4` vs `depth=2` — do not raise these values or the test suite will be slow.
