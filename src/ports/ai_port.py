"""AI port interface for computer opponents."""
from abc import ABC, abstractmethod
from typing import List, Tuple

from ..domain.entities.board import Board
from ..domain.value_objects.position import Position
from ..domain.value_objects.ship_placement import ShipPlacement


class AIPort(ABC):
    """Port interface for AI implementations.
    
    This interface defines the contract for AI adapters that provide
    computer opponent functionality.
    """
    
    @abstractmethod
    def get_ship_placement(
        self, 
        ship_size: int, 
        board: Board,
        existing_ships: List[Position]
    ) -> ShipPlacement:
        """Get AI decision for ship placement.
        
        Args:
            ship_size: Size of the ship to place
            board: Current board state
            existing_ships: List of positions already occupied by ships
            
        Returns:
            ShipPlacement with position and orientation
        """
        pass
    
    @abstractmethod
    def get_fire_location(
        self, 
        opponent_board: Board,
        firing_history: List[Tuple[Position, str]]
    ) -> Position:
        """Get AI decision for firing location.
        
        Args:
            opponent_board: The opponent's board (from AI's perspective)
            firing_history: History of previous shots (position, result)
            
        Returns:
            Position to fire at
        """
        pass
    
    @abstractmethod
    def update_shot_result(self, position: Position, result: str) -> None:
        """Update AI with the result of its last shot.
        
        Args:
            position: Position that was fired at
            result: Result of the shot ('hit' or 'miss')
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset AI state for a new game."""
        pass