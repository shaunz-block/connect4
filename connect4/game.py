from connect4.board import Board
from connect4.player import Player


class Game:
    def __init__(
        self, player1: Player, player2: Player, rows: int = 6, cols: int = 7, connect_n: int = 4
    ):
        self.board = Board(rows, cols, connect_n)
        self.players = [player1, player2]
        self.current_turn = 0

    def _setup_players(self) -> None:
        for i, player in enumerate(self.players):
            if hasattr(player, "piece"):
                player.piece = i + 1  # 1 or 2
                player.opponent = 2 - i  # 2 or 1

    def play(self) -> None:
        """Run the game loop."""
        # 0. Setup bot players
        self._setup_players()

        while True:
            # 1. Print board
            self.board.print_board()

            player = self.current_player
            piece = self.current_piece

            # 2. Get move from current player
            col = player.get_move(self.board)

            # 3. Validate move (re-prompt if invalid)
            # For bots, we trust their output but still guard against invalid moves
            while not self.board.is_valid_move(col):
                print(f"Invalid move: column {col}. Try again.")
                col = player.get_move(self.board)

            # 4. Drop piece
            self.board.drop_piece(col, piece)

            # 5. Check for winner → announce and stop
            winner = self.board.check_winner()
            if winner is not None:
                self.board.print_board()
                print(f"{player.name} wins!")
                return

            # 6. Check for full board → announce draw and stop
            if self.board.is_full():
                self.board.print_board()
                print("It's a draw!")
                return

            # 7. Switch player, repeat
            self._switch_player()

    def _switch_player(self) -> None:
        self.current_turn = 1 - self.current_turn

    @property
    def current_player(self):
        return self.players[self.current_turn]

    @property
    def current_piece(self) -> int:
        return self.current_turn + 1
