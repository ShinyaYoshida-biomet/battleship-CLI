# -*- coding: utf-8 -*-
"""
CLI Adapter for Battleship game using Rich UI.
Implements Hexagonal Architecture ports for CLI interface.
"""

from typing import Tuple
from domain.models import (
    GameState, ShipPlacement, FireAction, Ship, Position,
    PlacementContext, FireContext, GameResult, FireResult
)
from ports.game_ports import GameInputPort, GameOutputPort
from ui import ui


class CLIInputAdapter(GameInputPort):
    """CLI implementation of GameInputPort using Rich UI."""
    
    async def get_ship_placement(self, context: PlacementContext) -> ShipPlacement:
        """Get ship placement from CLI user input."""
        
        # Use existing Rich UI method
        orientation, row, col = ui.prompt_ship_placement(
            context.player_name,
            context.ship.symbol, 
            context.ship.size,
            context.board_size
        )
        
        return ShipPlacement(
            player_name=context.player_name,
            ship=context.ship,
            orientation=orientation,
            start_position=Position(row, col)
        )
    
    async def get_fire_action(self, context: FireContext) -> FireAction:
        """Get fire coordinates from CLI user input."""
        
        # Use existing Rich UI method
        row, col = ui.prompt_fire_location(context.player_name, context.board_size)
        
        return FireAction(
            player_name=context.player_name,
            target_position=Position(row, col)
        )
    
    async def get_game_mode_selection(self) -> str:
        """Get game mode selection from CLI."""
        return ui.prompt_game_mode()
    
    async def get_player_names(self, game_mode: str) -> Tuple[str, str]:
        """Get player names from CLI."""
        return ui.prompt_player_names(game_mode)


class CLIOutputAdapter(GameOutputPort):
    """CLI implementation of GameOutputPort using Rich UI."""
    
    async def show_welcome(self):
        """Display welcome screen."""
        ui.show_welcome_screen()
    
    async def show_game_config(self, board_size: Tuple[int, int], ships: dict):
        """Display game configuration."""
        ui.show_game_config(board_size, ships)
    
    async def show_game_state(self, state: GameState, 
                            firing_board: object = None, 
                            placement_board: object = None):
        """Display current game state with boards."""
        
        if state.phase.value == "ship_placement":
            # During ship placement, show placement board
            if placement_board is not None:
                board_table = ui.create_board_table(
                    placement_board, 
                    f"🚢 {state.current_player}'s Ships", 
                    show_ships=True
                )
                ui.console.print(board_table)
        else:
            # During battle, show both boards side by side with ship status
            if firing_board is not None and placement_board is not None:
                ui.display_boards_side_by_side(
                    state.current_player,
                    firing_board,
                    placement_board,
                    state.ships_config
                )
            
        # Show turn information
        if state.phase.value == "battle":
            ui.show_turn_header(state.current_player, state.turn_counter)
    
    async def show_placement_result(self, result: GameResult):
        """Display ship placement result."""
        if result.success:
            ui.console.print(f"[green]🎉 {result.message}[/green]")
        else:
            ui.console.print(f"[red]❌ {result.message}[/red]")
    
    async def show_fire_result(self, result: FireResult):
        """Display fire action result."""
        # Use existing Rich UI method
        ship_symbol = result.ship_symbol if result.hit else None
        # Note: We'll need to extract opponent name from context
        # For now, use generic "opponent"
        ui.show_fire_result("Player", "Opponent", 0, 0, result.hit, ship_symbol, result.ship_destroyed)
    
    async def show_winner(self, winner: str, is_human: bool):
        """Display game winner."""
        ui.show_game_winner(winner, is_human)
    
    async def show_error(self, message: str):
        """Display error message."""
        ui.console.print(f"[red]❌ Error: {message}[/red]")


class CLIAdapter(CLIInputAdapter, CLIOutputAdapter):
    """
    Combined CLI adapter that implements both input and output ports.
    Convenient for CLI applications where the same object handles both.
    """
    pass