from connect4.board import Board
from connect4.player import Player


class Game:
    def __init__(
        self, player1: Player, player2: Player, rows: int = 6, cols: int = 7, connect_n: int = 4
    ):
        self.board = Board(rows, cols, connect_n)
        self.players = [player1, player2]
        self.current_turn = 0

    def _setup_bot_players(self) -> None:
        for i, player in enumerate(self.players):
            if hasattr(player, "player_id"):
                player.player_id = i + 1  # 1 or 2
                player.opponent_id = 2 - i  # 2 or 1

    def play(self) -> None:
        """Run the game loop."""
        # 0. Assign player_id / opponent_id for bot players (e.g. MinimaxBot)
        self._setup_bot_players()

        while True:
            # 1. Print board
            self.board.print_board()

            player = self.current_player
            player_id = self.current_player_id

            # 2. Get move from current player
            col = player.get_move(self.board)

            # 3. Validate move (re-prompt if invalid)
            # For bots, we trust their output but still guard against invalid moves
            while not self.board.is_valid_move(col):
                print(f"Invalid move: column {col}. Try again.")
                col = player.get_move(self.board)

            # 4. Drop disc
            self.board.drop_disc(col, player_id)

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
    def current_player_id(self) -> int:
        return self.current_turn + 1
