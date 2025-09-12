"""In-memory implementation of game repository."""
from typing import Optional, List, Dict

from ...domain.entities.game_state import GameState
from ...ports.game_repository_port import GameRepositoryPort, RepositoryError


class InMemoryGameRepository(GameRepositoryPort):
    """In-memory implementation of the game repository port."""
    
    def __init__(self):
        self._games: Dict[str, GameState] = {}
    
    def save_game(self, game_state: GameState) -> None:
        """Save a game state."""
        try:
            self._games[game_state.id] = game_state
        except Exception as e:
            raise RepositoryError(f"Failed to save game: {e}")
    
    def load_game(self, game_id: str) -> Optional[GameState]:
        """Load a game state by ID."""
        try:
            return self._games.get(game_id)
        except Exception as e:
            raise RepositoryError(f"Failed to load game: {e}")
    
    def delete_game(self, game_id: str) -> bool:
        """Delete a game state."""
        try:
            if game_id in self._games:
                del self._games[game_id]
                return True
            return False
        except Exception as e:
            raise RepositoryError(f"Failed to delete game: {e}")
    
    def list_games(self) -> List[str]:
        """List all saved game IDs."""
        try:
            return list(self._games.keys())
        except Exception as e:
            raise RepositoryError(f"Failed to list games: {e}")
    
    def game_exists(self, game_id: str) -> bool:
        """Check if a game exists."""
        return game_id in self._games