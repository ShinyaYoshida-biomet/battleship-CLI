"""Ship entity for battleship game."""
import uuid
from typing import List, Set

from ..value_objects.position import Position
from ..value_objects.ship_placement import ShipPlacement


class Ship:
    """Entity representing a ship in the battleship game.
    
    A ship has a unique identity, placement on the board, and tracks hits.
    """
    
    def __init__(self, symbol: str, name: str, size: int, placement: ShipPlacement):
        """Initialize a new ship.
        
        Args:
            symbol: Single character symbol representing the ship type
            name: Human-readable name of the ship
            size: Length of the ship in cells
            placement: Position and orientation of the ship on the board
        """
        self._id = str(uuid.uuid4())
        self.symbol = symbol
        self.name = name
        self.size = size
        self.placement = placement
        self.hits: Set[Position] = set()
    
    @property
    def id(self) -> str:
        """Unique identifier for the ship."""
        return self._id
    
    def get_positions(self) -> List[Position]:
        """Get all positions occupied by this ship.
        
        Returns:
            List of positions occupied by the ship
        """
        return self.placement.calculate_positions(self.size)
    
    def occupies_position(self, position: Position) -> bool:
        """Check if this ship occupies the given position.
        
        Args:
            position: Position to check
            
        Returns:
            True if the ship occupies this position, False otherwise
        """
        return position in self.get_positions()
    
    def hit(self, position: Position) -> None:
        """Record a hit on this ship at the given position.
        
        Args:
            position: Position where the ship was hit
            
        Raises:
            ValueError: If the position is not part of this ship
        """
        if not self.occupies_position(position):
            raise ValueError(f"Position {position} is not part of this ship")
        
        self.hits.add(position)
    
    def is_hit_at_position(self, position: Position) -> bool:
        """Check if this ship has been hit at the given position.
        
        Args:
            position: Position to check
            
        Returns:
            True if the ship has been hit at this position, False otherwise
        """
        return position in self.hits
    
    def is_sunk(self) -> bool:
        """Check if this ship is completely sunk.
        
        Returns:
            True if all positions of the ship have been hit, False otherwise
        """
        ship_positions = set(self.get_positions())
        return ship_positions.issubset(self.hits)
    
    def __eq__(self, other) -> bool:
        """Check equality based on ship ID."""
        if not isinstance(other, Ship):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ship ID."""
        return hash(self.id)