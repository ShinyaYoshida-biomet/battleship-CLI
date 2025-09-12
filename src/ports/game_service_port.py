"""Game service port interface - main application interface."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from ..domain.entities.game_state import GameState
from ..domain.entities.player import Player, PlayerType
from ..domain.entities.ship import Ship
from ..domain.entities.board import CellState
from ..domain.value_objects.position import Position
from ..domain.value_objects.ship_placement import ShipPlacement


class GameServicePort(ABC):
    """Primary port interface for the game service.
    
    This is the main interface that external adapters (CLI, Web) use
    to interact with the game application.
    """
    
    @abstractmethod
    def create_game(
        self, 
        player1_name: str, 
        player1_type: PlayerType,
        player2_name: str, 
        player2_type: PlayerType,
        board_size: tuple = (7, 7)
    ) -> GameState:
        """Create a new game.
        
        Args:
            player1_name: Name of player 1
            player1_type: Type of player 1 (human/computer)
            player2_name: Name of player 2
            player2_type: Type of player 2 (human/computer)
            board_size: Size of the game boards (rows, cols)
            
        Returns:
            New GameState instance
        """
        pass
    
    @abstractmethod
    def place_ship(
        self, 
        game_state: GameState, 
        player: Player, 
        ship_symbol: str, 
        ship_name: str, 
        ship_size: int,
        placement: ShipPlacement
    ) -> None:
        """Place a ship on a player's board.
        
        Args:
            game_state: Current game state
            player: Player placing the ship
            ship_symbol: Symbol representing the ship
            ship_name: Name of the ship
            ship_size: Size of the ship
            placement: Position and orientation of the ship
            
        Raises:
            GameError: If ship cannot be placed
        """
        pass
    
    @abstractmethod
    def fire_shot(
        self, 
        game_state: GameState, 
        shooter: Player, 
        position: Position
    ) -> CellState:
        """Fire a shot at the opponent.
        
        Args:
            game_state: Current game state
            shooter: Player taking the shot
            position: Position to fire at
            
        Returns:
            Result of the shot (HIT or MISS)
            
        Raises:
            GameError: If shot cannot be taken
        """
        pass
    
    @abstractmethod
    def check_game_over(self, game_state: GameState) -> Optional[Player]:
        """Check if the game is over and return winner if any.
        
        Args:
            game_state: Current game state
            
        Returns:
            Winning player if game is over, None otherwise
        """
        pass
    
    @abstractmethod
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            GameState if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save_game(self, game_state: GameState) -> None:
        """Save current game state.
        
        Args:
            game_state: Game state to save
            
        Raises:
            GameError: If save operation fails
        """
        pass
    
    @abstractmethod
    def advance_turn(self, game_state: GameState) -> None:
        """Advance to the next player's turn.
        
        Args:
            game_state: Current game state
        """
        pass
    
    @abstractmethod
    def get_valid_ship_placements(
        self, 
        player: Player, 
        ship_size: int
    ) -> List[ShipPlacement]:
        """Get all valid ship placements for a player.
        
        Args:
            player: Player to check placements for
            ship_size: Size of the ship to place
            
        Returns:
            List of valid ship placements
        """
        pass
    
    @abstractmethod
    def get_valid_fire_positions(self, player: Player) -> List[Position]:
        """Get all valid firing positions for a player.
        
        Args:
            player: Player to check positions for
            
        Returns:
            List of valid firing positions
        """
        pass
    
    @abstractmethod
    def get_game_summary(self, game_state: GameState) -> Dict[str, Any]:
        """Get a summary of the current game state.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary containing game summary information
        """
        pass


class GameError(Exception):
    """Exception raised by game service operations."""
    pass