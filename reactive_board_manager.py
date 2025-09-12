# -*- coding: utf-8 -*-
"""
Reactive Board Manager using Rich Live Display
Eliminates full re-renders by updating only changed cells reactively.
"""

import pandas as pd
from typing import Dict, Any
from rich.live import Live
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from ui import ui


class ReactiveBoardManager:
    """Manages reactive board updates using Rich Live display."""
    
    def __init__(self, player_name: str, firing_board: pd.DataFrame, placement_board: pd.DataFrame):
        """Initialize reactive board manager.
        
        Args:
            player_name (str): Name of the player
            firing_board (pd.DataFrame): Player's firing board
            placement_board (pd.DataFrame): Player's placement board
        """
        self.player_name = player_name
        self.firing_board = firing_board.copy()
        self.placement_board = placement_board.copy()
        self.console = Console()
        self.live_display = None
        
    def create_board_layout(self) -> Panel:
        """Create the board layout for live display."""
        firing_table = ui.create_board_table(
            self.firing_board, 
            f"🎯 {self.player_name}'s Attack Board", 
            show_ships=False
        )
        
        placement_table = ui.create_board_table(
            self.placement_board, 
            f"🚢 {self.player_name}'s Fleet", 
            show_ships=True
        )
        
        columns = Columns([firing_table, placement_table], equal=True, expand=True)
        
        return Panel(
            columns,
            title=f"⚔️  {self.player_name}'s Battle View",
            border_style="bright_cyan",
            padding=(1, 2)
        )
    
    def start_live_display(self):
        """Start the live reactive board display."""
        self.live_display = Live(
            self.create_board_layout(), 
            console=self.console, 
            refresh_per_second=4,
            screen=False
        )
        self.live_display.__enter__()
    
    def pause_for_input(self):
        """Temporarily pause live display for user input."""
        if self.live_display:
            self.live_display.__exit__(None, None, None)
            
    def resume_after_input(self):
        """Resume live display after user input."""
        if self.live_display:
            self.live_display.__enter__()
        
    def update_firing_board(self, row: int, col: int, symbol: str):
        """Update a single cell on the firing board reactively.
        
        Args:
            row (int): Row coordinate
            col (int): Column coordinate  
            symbol (str): Symbol to place ('O' for hit, 'X' for miss)
        """
        self.firing_board.iloc[row, col] = symbol
        if self.live_display:
            self.live_display.update(self.create_board_layout())
    
    def update_placement_board(self, row: int, col: int, symbol: str):
        """Update a single cell on the placement board reactively.
        
        Args:
            row (int): Row coordinate
            col (int): Column coordinate
            symbol (str): Symbol to place
        """
        self.placement_board.iloc[row, col] = symbol  
        if self.live_display:
            self.live_display.update(self.create_board_layout())
    
    def show_message_above_board(self, message: str):
        """Show a message above the live board without disrupting the display.
        
        Args:
            message (str): Message to display
        """
        if self.live_display:
            self.live_display.console.print(message)
    
    def stop_live_display(self):
        """Stop the live display."""
        if self.live_display:
            self.live_display.__exit__(None, None, None)
            self.live_display = None


class ReactiveGameManager:
    """Manages reactive displays for both players."""
    
    def __init__(self):
        self.board_managers: Dict[str, ReactiveBoardManager] = {}
        self.current_display = None
    
    def register_player(self, player_name: str, firing_board: pd.DataFrame, placement_board: pd.DataFrame):
        """Register a player's board manager.
        
        Args:
            player_name (str): Player name
            firing_board (pd.DataFrame): Player's firing board
            placement_board (pd.DataFrame): Player's placement board
        """
        self.board_managers[player_name] = ReactiveBoardManager(
            player_name, firing_board, placement_board
        )
    
    def start_player_display(self, player_name: str):
        """Start reactive display for a specific player.
        
        Args:
            player_name (str): Player name
        """
        # Stop current display if active
        if self.current_display:
            self.current_display.stop_live_display()
            
        # Start new display
        self.current_display = self.board_managers[player_name]
        self.current_display.start_live_display()
    
    def update_firing_result(self, player_name: str, row: int, col: int, hit: bool):
        """Update firing result reactively.
        
        Args:
            player_name (str): Player who fired
            row (int): Target row
            col (int): Target column
            hit (bool): Whether shot was a hit
        """
        symbol = 'O' if hit else 'X'
        if player_name in self.board_managers:
            self.board_managers[player_name].update_firing_board(row, col, symbol)
    
    def update_ship_hit(self, player_name: str, row: int, col: int):
        """Update when player's ship is hit.
        
        Args:
            player_name (str): Player whose ship was hit
            row (int): Hit row
            col (int): Hit column
        """
        if player_name in self.board_managers:
            self.board_managers[player_name].update_placement_board(row, col, 'O')
    
    def show_message(self, message: str):
        """Show message above current display.
        
        Args:
            message (str): Message to show
        """
        if self.current_display:
            self.current_display.show_message_above_board(message)
    
    def pause_for_input(self):
        """Pause current display for user input."""
        if self.current_display:
            self.current_display.pause_for_input()
    
    def resume_after_input(self):
        """Resume current display after user input."""
        if self.current_display:
            self.current_display.resume_after_input()
    
    def cleanup(self):
        """Clean up all displays."""
        if self.current_display:
            self.current_display.stop_live_display()
        self.current_display = None


# Global reactive game manager instance
reactive_manager = ReactiveGameManager()