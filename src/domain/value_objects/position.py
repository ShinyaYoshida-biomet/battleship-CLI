"""Position value object for battleship game coordinates."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Position:
    """Immutable value object representing a position on the game board.
    
    Attributes:
        row: The row coordinate (0-based)
        col: The column coordinate (0-based)
    """
    row: int
    col: int

    def __post_init__(self):
        """Validate position coordinates after initialization."""
        if self.row < 0 or self.col < 0:
            raise ValueError("Coordinates must be non-negative")

    def __str__(self) -> str:
        """String representation of the position."""
        return f"Position({self.row}, {self.col})"

    def to_tuple(self) -> Tuple[int, int]:
        """Convert position to tuple format."""
        return (self.row, self.col)