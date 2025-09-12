"""Notification port interface for game events."""
from abc import ABC, abstractmethod
from typing import Dict, Any

from ..domain.entities.player import Player
from ..domain.entities.ship import Ship
from ..domain.entities.board import CellState
from ..domain.value_objects.position import Position


class NotificationPort(ABC):
    """Port interface for game event notifications.
    
    This interface defines the contract for notification services
    that handle game events and alerts.
    """
    
    @abstractmethod
    def notify_game_started(self, player1: Player, player2: Player) -> None:
        """Notify that a game has started.
        
        Args:
            player1: First player
            player2: Second player
        """
        pass
    
    @abstractmethod
    def notify_turn_started(self, player: Player, turn_number: int) -> None:
        """Notify that a player's turn has started.
        
        Args:
            player: Player whose turn it is
            turn_number: Current turn number
        """
        pass
    
    @abstractmethod
    def notify_ship_placed(self, player: Player, ship: Ship) -> None:
        """Notify that a ship has been placed.
        
        Args:
            player: Player who placed the ship
            ship: Ship that was placed
        """
        pass
    
    @abstractmethod
    def notify_shot_fired(
        self, 
        shooter: Player, 
        target: Player, 
        position: Position, 
        result: CellState
    ) -> None:
        """Notify that a shot was fired.
        
        Args:
            shooter: Player who fired the shot
            target: Player who was targeted
            position: Position that was fired at
            result: Result of the shot (HIT or MISS)
        """
        pass
    
    @abstractmethod
    def notify_ship_hit(self, player: Player, ship: Ship, position: Position) -> None:
        """Notify that a ship was hit.
        
        Args:
            player: Player whose ship was hit
            ship: Ship that was hit
            position: Position where ship was hit
        """
        pass
    
    @abstractmethod
    def notify_ship_sunk(self, player: Player, ship: Ship) -> None:
        """Notify that a ship was sunk.
        
        Args:
            player: Player whose ship was sunk
            ship: Ship that was sunk
        """
        pass
    
    @abstractmethod
    def notify_game_over(self, winner: Player, loser: Player) -> None:
        """Notify that the game is over.
        
        Args:
            winner: Winning player
            loser: Losing player
        """
        pass
    
    @abstractmethod
    def notify_error(self, error_type: str, message: str, context: Dict[str, Any] = None) -> None:
        """Notify of an error condition.
        
        Args:
            error_type: Type of error
            message: Error message
            context: Additional context information
        """
        pass
    
    @abstractmethod
    def notify_info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Notify of an informational event.
        
        Args:
            message: Informational message
            context: Additional context information
        """
        pass