"""GameState entity for battleship game."""
import uuid
from enum import Enum
from typing import List, Optional, Dict, Any

from .player import Player


class GamePhase(Enum):
    """Phases of the game."""
    SETUP = "setup"
    SHIP_PLACEMENT = "ship_placement"
    BATTLE = "battle"
    GAME_OVER = "game_over"


class GameState:
    """Entity representing the overall state of a battleship game.
    
    Manages players, turns, game phase, and win conditions.
    """
    
    def __init__(self, players: List[Player]):
        """Initialize a new game state.
        
        Args:
            players: List of players (must be exactly 2)
            
        Raises:
            ValueError: If player count is not 2
        """
        if len(players) != 2:
            raise ValueError("Game requires exactly 2 players")
            
        self._id = str(uuid.uuid4())
        self.players = players.copy()
        self.current_player = players[0]
        self.phase = GamePhase.SETUP
        self.turn_number = 1
        self.winner: Optional[Player] = None
    
    @property
    def id(self) -> str:
        """Unique identifier for the game."""
        return self._id
    
    def get_opponent(self, player: Player) -> Player:
        """Get the opponent of the given player.
        
        Args:
            player: Player whose opponent to find
            
        Returns:
            The opponent player
            
        Raises:
            ValueError: If player is not in this game
        """
        if player not in self.players:
            raise ValueError(f"Player {player.name} is not in this game")
        
        return self.players[0] if self.players[1] == player else self.players[1]
    
    def switch_turn(self) -> None:
        """Switch to the next player's turn."""
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]
        self.turn_number += 1
    
    def advance_phase(self) -> None:
        """Advance to the next game phase.
        
        Raises:
            ValueError: If trying to advance from GAME_OVER
        """
        phase_order = [GamePhase.SETUP, GamePhase.SHIP_PLACEMENT, GamePhase.BATTLE, GamePhase.GAME_OVER]
        
        try:
            current_index = phase_order.index(self.phase)
            if current_index >= len(phase_order) - 1:
                raise ValueError("Cannot advance from GAME_OVER phase")
            self.phase = phase_order[current_index + 1]
        except ValueError as e:
            if "Cannot advance" in str(e):
                raise
            raise ValueError(f"Unknown phase: {self.phase}")
    
    def set_winner(self, winner: Player) -> None:
        """Set the winner and end the game.
        
        Args:
            winner: The winning player
            
        Raises:
            ValueError: If winner is not one of the game players
        """
        if winner not in self.players:
            raise ValueError("Winner must be one of the players in the game")
        
        self.winner = winner
        self.phase = GamePhase.GAME_OVER
    
    def is_game_over(self) -> bool:
        """Check if the game is over.
        
        Returns:
            True if game is over, False otherwise
        """
        return self.phase == GamePhase.GAME_OVER or self.winner is not None
    
    def check_win_condition(self) -> Optional[Player]:
        """Check if any player has won the game.
        
        Returns:
            The winning player, or None if no winner yet
        """
        for player in self.players:
            opponent = self.get_opponent(player)
            if opponent.has_lost():
                return player
        return None
    
    def is_setup_complete(self) -> bool:
        """Check if game setup is complete (all players have ships).
        
        Returns:
            True if setup is complete, False otherwise
        """
        return all(len(player.get_ships()) > 0 for player in self.players)
    
    def get_game_summary(self) -> Dict[str, Any]:
        """Get a summary of the current game state.
        
        Returns:
            Dictionary containing game state information
        """
        return {
            "game_id": self.id,
            "phase": self.phase.value,
            "current_player": self.current_player.name,
            "turn_number": self.turn_number,
            "winner": self.winner.name if self.winner else None,
            "players": [
                {
                    "name": player.name,
                    "type": player.player_type.value,
                    "ships_count": len(player.get_ships()),
                    "active_ships_count": len(player.get_active_ships()),
                    "has_lost": player.has_lost()
                }
                for player in self.players
            ]
        }
    
    def __eq__(self, other) -> bool:
        """Check equality based on game ID."""
        if not isinstance(other, GameState):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on game ID."""
        return hash(self.id)