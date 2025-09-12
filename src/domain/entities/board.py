"""Board entity for battleship game."""
from enum import Enum
from typing import Dict, List, Optional

from ..value_objects.position import Position
from .ship import Ship


class CellState(Enum):
    """State of a cell on the board."""
    WATER = "water"
    SHIP = "ship"
    HIT = "hit"
    MISS = "miss"


class BoardType(Enum):
    """Type of board."""
    PLACEMENT = "placement"  # Shows ship positions
    FIRING = "firing"       # Shows attack results


class Board:
    """Entity representing a game board.
    
    The board manages ship placement, shot tracking, and game state.
    """
    
    def __init__(self, rows: int, cols: int, board_type: BoardType):
        """Initialize a new board.
        
        Args:
            rows: Number of rows on the board
            cols: Number of columns on the board
            board_type: Type of board (placement or firing)
            
        Raises:
            ValueError: If dimensions are not positive
        """
        if rows <= 0 or cols <= 0:
            raise ValueError("Board dimensions must be positive")
            
        self.rows = rows
        self.cols = cols
        self.board_type = board_type
        
        # Initialize board state - all cells start as water
        self._cells: Dict[Position, CellState] = {}
        for row in range(rows):
            for col in range(cols):
                self._cells[Position(row, col)] = CellState.WATER
        
        # Track ships on the board (for placement boards)
        self._ships: List[Ship] = []
        self._ship_positions: Dict[Position, Ship] = {}
    
    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within board bounds.
        
        Args:
            position: Position to check
            
        Returns:
            True if position is valid, False otherwise
        """
        return (0 <= position.row < self.rows and 
                0 <= position.col < self.cols)
    
    def get_cell_state(self, position: Position) -> CellState:
        """Get the state of a cell at the given position.
        
        Args:
            position: Position to check
            
        Returns:
            State of the cell
            
        Raises:
            ValueError: If position is out of bounds
        """
        if not self.is_valid_position(position):
            raise ValueError(f"Position {position} is out of bounds")
        
        return self._cells[position]
    
    def get_ship_at_position(self, position: Position) -> Optional[Ship]:
        """Get the ship at the given position, if any.
        
        Args:
            position: Position to check
            
        Returns:
            Ship at the position, or None if no ship
        """
        return self._ship_positions.get(position)
    
    def place_ship(self, ship: Ship) -> None:
        """Place a ship on the board.
        
        Args:
            ship: Ship to place
            
        Raises:
            ValueError: If ship cannot be placed (out of bounds or overlapping)
        """
        ship_positions = ship.get_positions()
        
        # Check if all positions are valid and available
        for pos in ship_positions:
            if not self.is_valid_position(pos):
                raise ValueError(f"Cannot place ship - position {pos} is out of bounds")
            
            if self._cells[pos] != CellState.WATER:
                raise ValueError(f"Cannot place ship - position {pos} is already occupied")
        
        # Place the ship
        for pos in ship_positions:
            self._cells[pos] = CellState.SHIP
            self._ship_positions[pos] = ship
        
        self._ships.append(ship)
    
    def record_shot(self, position: Position) -> CellState:
        """Record a shot at the given position.
        
        Args:
            position: Position where shot was fired
            
        Returns:
            Result of the shot (HIT or MISS)
            
        Raises:
            ValueError: If position is invalid or already fired upon
        """
        if not self.is_valid_position(position):
            raise ValueError(f"Position {position} is out of bounds")
        
        current_state = self._cells[position]
        
        if current_state in [CellState.HIT, CellState.MISS]:
            raise ValueError(f"Position {position} has already been fired upon")
        
        if current_state == CellState.SHIP:
            # Hit a ship
            self._cells[position] = CellState.HIT
            ship = self._ship_positions[position]
            ship.hit(position)
            return CellState.HIT
        else:
            # Miss (hit water)
            self._cells[position] = CellState.MISS
            return CellState.MISS
    
    def all_ships_sunk(self) -> bool:
        """Check if all ships on the board are sunk.
        
        Returns:
            True if all ships are sunk, False otherwise
        """
        return all(ship.is_sunk() for ship in self._ships)
    
    def get_ships(self) -> List[Ship]:
        """Get all ships on the board.
        
        Returns:
            List of ships on the board
        """
        return self._ships.copy()
    
    def get_sunk_ships(self) -> List[Ship]:
        """Get all sunk ships on the board.
        
        Returns:
            List of sunk ships
        """
        return [ship for ship in self._ships if ship.is_sunk()]
    
    def get_active_ships(self) -> List[Ship]:
        """Get all active (not sunk) ships on the board.
        
        Returns:
            List of active ships
        """
        return [ship for ship in self._ships if not ship.is_sunk()]