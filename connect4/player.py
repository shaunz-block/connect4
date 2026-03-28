from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from connect4.board import Board


class Player(Protocol):
    name: str

    def get_move(self, board: "Board") -> int: ...


class HumanPlayer:
    def __init__(self, name: str):
        self.name = name

    def get_move(self, board: "Board") -> int:
        """Prompt the user for input. Keeps asking until a valid integer is entered.

        Does NOT validate whether the move is legal on the board.
        """
        while True:
            try:
                col = int(input(f"{self.name}, enter column: "))
                return col
            except ValueError:
                print("Invalid input. Please enter a number.")
