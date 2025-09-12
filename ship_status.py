#!/usr/bin/env python3
"""
Ship status enumeration for consistent status display across Fleet Status and Enemy Intel.
"""

from enum import Enum
from typing import Dict, Tuple

class ShipStatus(Enum):
    """Enumeration for ship status with display information."""
    
    INTACT = ("INTACT", "✅", "green")
    DAMAGED = ("DAMAGED", "⚠️", "yellow") 
    DESTROYED = ("DESTROYED", "💥", "red")
    UNKNOWN = ("UNKNOWN", "❓", "blue")
    HIT_DAMAGED = ("HIT/DAMAGED", "⚠️", "yellow")
    
    def __init__(self, display_name: str, emoji: str, color: str):
        self.display_name = display_name
        self.emoji = emoji
        self.color = color
    
    def format_status(self, ship_name: str, current_cells: int = None, total_cells: int = None) -> str:
        """Format the ship status for display."""
        if current_cells is not None and total_cells is not None:
            if self == ShipStatus.INTACT:
                return f"  [{self.color}]{self.emoji} {ship_name}: {self.display_name} ({current_cells}/{total_cells})[/{self.color}]"
            elif self == ShipStatus.DAMAGED:
                return f"  [{self.color}]{self.emoji} {ship_name}: {self.display_name} ({current_cells}/{total_cells})[/{self.color}]"
            else:
                return f"  [{self.color}]{self.emoji} {ship_name}: {self.display_name}[/{self.color}]"
        else:
            return f"  [{self.color}]{self.emoji} {ship_name}: {self.display_name}[/{self.color}]"


def determine_ship_status(current_cells: int, total_cells: int, is_enemy: bool = False) -> ShipStatus:
    """Determine ship status based on remaining cells."""
    if current_cells == 0:
        return ShipStatus.DESTROYED
    elif current_cells < total_cells:
        if is_enemy:
            return ShipStatus.HIT_DAMAGED
        else:
            return ShipStatus.DAMAGED
    else:
        if is_enemy:
            return ShipStatus.UNKNOWN
        else:
            return ShipStatus.INTACT


def get_ship_names() -> Dict[str, str]:
    """Get standardized ship names mapping."""
    return {
        'C': 'Carrier',
        'B': 'Battleship', 
        'D': 'Destroyer',
        'S': 'Submarine',
        'P': 'Patrol boat'
    }