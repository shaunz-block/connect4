import argparse

from connect4.bot import MinimaxBot
from connect4.game import Game
from connect4.player import HumanPlayer


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Connect N")
    parser.add_argument(
        "--bot",
        action="store_true",
        help="Play against a bot (Human vs Bot)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=4,
        help="Bot search depth (default: 4)",
    )
    parser.add_argument("--rows", type=int, default=6, help="Number of rows (default: 6)")
    parser.add_argument("--cols", type=int, default=7, help="Number of cols (default: 7)")
    parser.add_argument("--connect-n", type=int, default=4, help="Connect N to win (default: 4)")
    args = parser.parse_args()

    player1 = HumanPlayer("Player 1")
    if args.bot:
        player2 = MinimaxBot(name="Bot", depth=args.depth)
    else:
        player2 = HumanPlayer("Player 2")

    game = Game(player1, player2, rows=args.rows, cols=args.cols, connect_n=args.connect_n)
    game.play()


if __name__ == "__main__":
    main()
