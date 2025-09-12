"""UI port interface for user interaction."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

from ..domain.entities.game_state import GameState
from ..domain.entities.player import Player
from ..domain.entities.ship import Ship
from ..domain.entities.board import CellState
from ..domain.value_objects.position import Position
from ..domain.value_objects.ship_placement import ShipPlacement


class UIPort(ABC):
    """Port interface for user interaction adapters.
    
    This interface defines the contract for UI implementations (CLI, Web, etc.)
    that need to interact with users for input and display game information.
    """
    
    @abstractmethod
    def display_welcome_screen(self) -> None:
        """Display the welcome screen."""
        pass
    
    @abstractmethod
    def prompt_game_mode(self) -> str:
        """Prompt user for game mode selection.
        
        Returns:
            Game mode ('pvp' for Player vs Player, 'pvc' for Player vs Computer)
        """
        pass
    
    @abstractmethod
    def prompt_player_names(self, mode: str) -> Tuple[str, str]:
        """Prompt for player names.
        
        Args:
            mode: Game mode ('pvp' or 'pvc')
            
        Returns:
            Tuple of (player1_name, player2_name)
        """
        pass
    
    @abstractmethod
    def display_game_config(self, board_size: Tuple[int, int], ships: Dict[str, int]) -> None:
        """Display game configuration.
        
        Args:
            board_size: (rows, cols) of the board
            ships: Dictionary of ship symbol to size
        """
        pass
    
    @abstractmethod
    def prompt_ship_placement_mode(self, player_name: str) -> str:
        """Prompt player for ship placement mode.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Placement mode ('manual' or 'random')
        """
        pass
    
    @abstractmethod
    def prompt_ship_placement(
        self, 
        player_name: str, 
        ship_symbol: str, 
        ship_size: int,
        board_size: Tuple[int, int]
    ) -> ShipPlacement:
        """Prompt player for ship placement.
        
        Args:
            player_name: Name of the player placing the ship
            ship_symbol: Symbol of the ship being placed
            ship_size: Size of the ship
            board_size: (rows, cols) of the board
            
        Returns:
            ShipPlacement object with position and orientation
        """
        pass
    
    @abstractmethod
    def prompt_fire_location(
        self, 
        player_name: str, 
        board_size: Tuple[int, int]
    ) -> Position:
        """Prompt player for firing location.
        
        Args:
            player_name: Name of the player firing
            board_size: (rows, cols) of the board
            
        Returns:
            Position to fire at
        """
        pass
    
    @abstractmethod
    def display_placement_board(self, player: Player) -> None:
        """Display player's placement board (showing their ships).
        
        Args:
            player: Player whose board to display
        """
        pass
    
    @abstractmethod
    def display_firing_board(self, player: Player) -> None:
        """Display player's firing board (showing their attack history).
        
        Args:
            player: Player whose firing board to display
        """
        pass
    
    @abstractmethod
    def display_boards_side_by_side(
        self, 
        player: Player, 
        opponent: Player
    ) -> None:
        """Display both placement and firing boards side by side.
        
        Args:
            player: Current player
            opponent: Opponent player
        """
        pass
    
    @abstractmethod
    def display_turn_header(self, player_name: str, turn_number: int) -> None:
        """Display turn header information.
        
        Args:
            player_name: Name of the current player
            turn_number: Current turn number
        """
        pass
    
    @abstractmethod
    def display_fire_result(
        self, 
        shooter: str, 
        target: str, 
        position: Position, 
        result: CellState,
        ship_symbol: str = None
    ) -> None:
        """Display the result of a firing action.
        
        Args:
            shooter: Name of the player who fired
            target: Name of the target player
            position: Position that was fired at
            result: Result of the shot (HIT or MISS)
            ship_symbol: Symbol of the ship that was hit (if any)
        """
        pass
    
    @abstractmethod
    def display_ship_sunk(self, player_name: str, ship: Ship) -> None:
        """Display notification that a ship was sunk.
        
        Args:
            player_name: Name of the player whose ship was sunk
            ship: The ship that was sunk
        """
        pass
    
    @abstractmethod
    def display_game_winner(self, winner: Player, is_human: bool) -> None:
        """Display the game winner.
        
        Args:
            winner: The winning player
            is_human: Whether the winner is a human player
        """
        pass
    
    @abstractmethod
    def display_error(self, message: str) -> None:
        """Display an error message.
        
        Args:
            message: Error message to display
        """
        pass
    
    @abstractmethod
    def display_info(self, message: str) -> None:
        """Display an informational message.
        
        Args:
            message: Info message to display
        """
        pass
    
    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen/display."""
        pass