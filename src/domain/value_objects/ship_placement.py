"""Ship placement value objects for battleship game."""
from dataclasses import dataclass
from enum import Enum
from typing import List

from .position import Position


class Orientation(Enum):
    """Orientation of a ship on the board."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True)
class ShipPlacement:
    """Immutable value object representing ship placement on the board.
    
    Attributes:
        start_position: The starting position of the ship
        orientation: The orientation of the ship (horizontal or vertical)
    """
    start_position: Position
    orientation: Orientation

    def __str__(self) -> str:
        """String representation of the ship placement."""
        return f"ShipPlacement({self.start_position}, {self.orientation.value})"

    def calculate_positions(self, ship_size: int) -> List[Position]:
        """Calculate all positions occupied by a ship with this placement.
        
        Args:
            ship_size: The size (length) of the ship
            
        Returns:
            List of positions occupied by the ship
            
        Raises:
            ValueError: If ship_size is not positive
        """
        if ship_size <= 0:
            raise ValueError("Ship size must be positive")
            
        positions = []
        
        for i in range(ship_size):
            if self.orientation == Orientation.HORIZONTAL:
                pos = Position(self.start_position.row, self.start_position.col + i)
            else:  # VERTICAL
                pos = Position(self.start_position.row + i, self.start_position.col)
            positions.append(pos)
            
        return positions