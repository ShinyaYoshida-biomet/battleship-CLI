# -*- coding: utf-8 -*-
"""
Domain models for Battleship game.
Pure business entities without any infrastructure dependencies.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import pandas as pd


class GamePhase(Enum):
    SHIP_PLACEMENT = "ship_placement"
    BATTLE = "battle"
    FINISHED = "finished"


class PlayerType(Enum):
    HUMAN = "human"
    COMPUTER = "computer"


@dataclass
class Position:
    row: int
    col: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.row, self.col)


@dataclass
class Ship:
    symbol: str
    size: int
    name: str


@dataclass
class ShipPlacement:
    player_name: str
    ship: Ship
    orientation: str  # 'h' or 'v'
    start_position: Position


@dataclass
class FireAction:
    player_name: str
    target_position: Position


@dataclass
class FireResult:
    hit: bool
    ship_symbol: Optional[str] = None
    ship_destroyed: bool = False
    winner: Optional[str] = None


@dataclass
class PlayerInfo:
    name: str
    player_type: PlayerType


@dataclass
class GameState:
    phase: GamePhase
    current_player: str
    players: List[PlayerInfo]
    board_size: Tuple[int, int]
    ships_config: Dict[str, int]
    turn_counter: int = 0
    winner: Optional[str] = None


@dataclass
class PlacementContext:
    """Context information for ship placement requests."""
    player_name: str
    ship: Ship
    board_size: Tuple[int, int]
    current_board_state: Optional[pd.DataFrame] = None


@dataclass
class FireContext:
    """Context information for fire action requests."""
    player_name: str
    board_size: Tuple[int, int]
    firing_board_state: Optional[pd.DataFrame] = None


@dataclass
class GameResult:
    """Result of a game action."""
    success: bool
    message: str
    game_state: Optional[GameState] = None
    fire_result: Optional[FireResult] = None