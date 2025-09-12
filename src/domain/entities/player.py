"""Player entity for battleship game."""
import uuid
from enum import Enum
from typing import List

from ..value_objects.position import Position
from .board import Board, BoardType, CellState
from .ship import Ship


class PlayerType(Enum):
    """Type of player."""
    HUMAN = "human"
    COMPUTER = "computer"


class Player:
    """Entity representing a player in the battleship game.
    
    A player has a unique identity, two boards (placement and firing),
    and manages their ships and shots.
    """
    
    def __init__(self, name: str, player_type: PlayerType, board_rows: int = 7, board_cols: int = 7):
        """Initialize a new player.
        
        Args:
            name: Name of the player
            player_type: Type of player (human or computer)
            board_rows: Number of rows on the boards (default 7)
            board_cols: Number of columns on the boards (default 7)
        """
        self._id = str(uuid.uuid4())
        self.name = name
        self.player_type = player_type
        
        # Create the two boards
        self.placement_board = Board(board_rows, board_cols, BoardType.PLACEMENT)
        self.firing_board = Board(board_rows, board_cols, BoardType.FIRING)
    
    @property
    def id(self) -> str:
        """Unique identifier for the player."""
        return self._id
    
    def is_computer(self) -> bool:
        """Check if this player is a computer player.
        
        Returns:
            True if computer player, False if human
        """
        return self.player_type == PlayerType.COMPUTER
    
    def place_ship(self, ship: Ship) -> None:
        """Place a ship on the player's placement board.
        
        Args:
            ship: Ship to place
            
        Raises:
            ValueError: If ship cannot be placed
        """
        self.placement_board.place_ship(ship)
    
    def record_incoming_shot(self, position: Position) -> CellState:
        """Record an incoming shot on the player's placement board.
        
        Args:
            position: Position where the shot was received
            
        Returns:
            Result of the shot (HIT or MISS)
            
        Raises:
            ValueError: If position is invalid or already shot
        """
        return self.placement_board.record_shot(position)
    
    def record_outgoing_shot(self, position: Position, result: CellState) -> None:
        """Record an outgoing shot on the player's firing board.
        
        Args:
            position: Position where the shot was fired
            result: Result of the shot (HIT or MISS)
            
        Raises:
            ValueError: If position is invalid or already recorded
        """
        if not self.firing_board.is_valid_position(position):
            raise ValueError(f"Position {position} is out of bounds")
        
        current_state = self.firing_board.get_cell_state(position)
        if current_state != CellState.WATER:
            raise ValueError(f"Position {position} has already been fired upon")
        
        # Manually set the cell state for firing board (no ships to hit)
        self.firing_board._cells[position] = result
    
    def can_fire_at_position(self, position: Position) -> bool:
        """Check if the player can fire at the given position.
        
        Args:
            position: Position to check
            
        Returns:
            True if position can be fired at, False otherwise
        """
        if not self.firing_board.is_valid_position(position):
            return False
        
        return self.firing_board.get_cell_state(position) == CellState.WATER
    
    def has_lost(self) -> bool:
        """Check if the player has lost (all ships sunk).
        
        Returns:
            True if all ships are sunk, False otherwise
        """
        return self.placement_board.all_ships_sunk()
    
    def get_ships(self) -> List[Ship]:
        """Get all ships belonging to this player.
        
        Returns:
            List of player's ships
        """
        return self.placement_board.get_ships()
    
    def get_active_ships(self) -> List[Ship]:
        """Get all active (non-sunk) ships belonging to this player.
        
        Returns:
            List of active ships
        """
        return self.placement_board.get_active_ships()
    
    def get_sunk_ships(self) -> List[Ship]:
        """Get all sunk ships belonging to this player.
        
        Returns:
            List of sunk ships
        """
        return self.placement_board.get_sunk_ships()
    
    def __eq__(self, other) -> bool:
        """Check equality based on player ID."""
        if not isinstance(other, Player):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on player ID."""
        return hash(self.id)