# -*- coding: utf-8 -*-
"""
Ports (interfaces) for Battleship game following Hexagonal Architecture.
These define the boundaries between the application core and external adapters.
"""

from abc import ABC, abstractmethod
from typing import Tuple
from domain.models import (
    GameState, ShipPlacement, FireAction, FireResult, 
    PlacementContext, FireContext, GameResult
)


class GameInputPort(ABC):
    """
    Input port for receiving user actions.
    Implemented by CLI, Web, API adapters.
    """
    
    @abstractmethod
    async def get_ship_placement(self, context: PlacementContext) -> ShipPlacement:
        """Get ship placement from user input."""
        pass
    
    @abstractmethod
    async def get_fire_action(self, context: FireContext) -> FireAction:
        """Get fire coordinates from user input.""" 
        pass
    
    @abstractmethod
    async def get_game_mode_selection(self) -> str:
        """Get game mode selection (pvp/pvc)."""
        pass
    
    @abstractmethod
    async def get_player_names(self, game_mode: str) -> Tuple[str, str]:
        """Get player names for the game."""
        pass
    
    @abstractmethod
    async def get_ship_placement_mode(self, player_name: str) -> str:
        """Get ship placement mode (manual or random) from user interface."""
        pass


class GameOutputPort(ABC):
    """
    Output port for displaying game information.
    Implemented by CLI, Web, API adapters.
    """
    
    @abstractmethod
    async def show_welcome(self):
        """Display welcome screen."""
        pass
    
    @abstractmethod
    async def show_game_config(self, board_size: Tuple[int, int], ships: dict):
        """Display game configuration."""
        pass
    
    @abstractmethod
    async def show_game_state(self, state: GameState, 
                            firing_board: object = None, 
                            placement_board: object = None):
        """Display current game state with boards."""
        pass
    
    @abstractmethod
    async def show_placement_result(self, result: GameResult):
        """Display ship placement result."""
        pass
    
    @abstractmethod
    async def show_fire_result(self, result: FireResult):
        """Display fire action result."""
        pass
    
    @abstractmethod
    async def show_winner(self, winner: str, is_human: bool):
        """Display game winner."""
        pass
    
    @abstractmethod
    async def show_error(self, message: str):
        """Display error message."""
        pass


class GameEventPort(ABC):
    """
    Event port for game lifecycle events.
    Optional - for advanced features like spectating, logging.
    """
    
    @abstractmethod
    async def on_game_started(self, state: GameState):
        """Called when game starts."""
        pass
    
    @abstractmethod
    async def on_phase_changed(self, old_phase: str, new_phase: str):
        """Called when game phase changes."""
        pass
    
    @abstractmethod
    async def on_turn_started(self, player_name: str, turn: int):
        """Called when player turn starts."""
        pass


class AIPort(ABC):
    """
    Port for AI player decisions.
    Allows different AI implementations.
    """
    
    @abstractmethod
    async def get_ship_placement_decision(self, context: PlacementContext) -> ShipPlacement:
        """AI decision for ship placement."""
        pass
    
    @abstractmethod  
    async def get_fire_decision(self, context: FireContext) -> FireAction:
        """AI decision for fire action."""
        pass