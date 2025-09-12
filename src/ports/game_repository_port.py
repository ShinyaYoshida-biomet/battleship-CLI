"""Game repository port interface for data persistence."""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..domain.entities.game_state import GameState


class GameRepositoryPort(ABC):
    """Port interface for game state persistence.
    
    This interface defines the contract for repositories that handle
    saving and loading game state data.
    """
    
    @abstractmethod
    def save_game(self, game_state: GameState) -> None:
        """Save a game state.
        
        Args:
            game_state: Game state to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    def load_game(self, game_id: str) -> Optional[GameState]:
        """Load a game state by ID.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            GameState if found, None otherwise
            
        Raises:
            RepositoryError: If load operation fails
        """
        pass
    
    @abstractmethod
    def delete_game(self, game_id: str) -> bool:
        """Delete a game state.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RepositoryError: If delete operation fails
        """
        pass
    
    @abstractmethod
    def list_games(self) -> List[str]:
        """List all saved game IDs.
        
        Returns:
            List of game IDs
            
        Raises:
            RepositoryError: If list operation fails
        """
        pass
    
    @abstractmethod
    def game_exists(self, game_id: str) -> bool:
        """Check if a game exists.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            True if game exists, False otherwise
        """
        pass


class RepositoryError(Exception):
    """Exception raised by repository operations."""
    pass