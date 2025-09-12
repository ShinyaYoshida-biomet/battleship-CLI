# -*- coding: utf-8 -*-
"""
AI Adapter for Battleship game.
Implements AI port using existing computer AI logic.
"""

from typing import List, Tuple
from domain.models import ShipPlacement, FireAction, Ship, Position, PlacementContext, FireContext
from ports.game_ports import AIPort
from computer_ai import ComputerAI


class StandardAIAdapter(AIPort):
    """
    AI adapter using existing ComputerAI implementation.
    Provides intelligent ship placement and firing decisions.
    """
    
    def __init__(self, board_size: Tuple[int, int]):
        self.board_size = board_size
        self.ai_instance = ComputerAI(board_size)
        self.shots_history = []
    
    async def get_ship_placement_decision(self, context: PlacementContext) -> ShipPlacement:
        """AI decision for ship placement using existing logic."""
        
        # Get occupied positions from current board state
        occupied_positions = []
        if context.current_board_state is not None:
            board = context.current_board_state
            for x in range(board.shape[0]):
                for y in range(board.shape[1]):
                    if board.iloc[x, y] != '*':  # Not empty water
                        occupied_positions.append((x, y))
        
        # Get AI placement decision
        orientation, row, col = self.ai_instance.get_ship_placement(
            context.ship.size, 
            occupied_positions
        )
        
        return ShipPlacement(
            player_name=context.player_name,
            ship=context.ship,
            orientation=orientation,
            start_position=Position(row, col)
        )
    
    async def get_fire_decision(self, context: FireContext) -> FireAction:
        """AI decision for fire action using existing logic."""
        
        # Convert firing board state to format expected by AI
        firing_board_data = []
        if context.firing_board_state is not None:
            board = context.firing_board_state
            for x in range(board.shape[0]):
                row = []
                for y in range(board.shape[1]):
                    row.append(board.iloc[x, y])
                firing_board_data.append(row)
        
        # Get AI firing decision
        row, col = self.ai_instance.get_fire_location(
            firing_board_data,
            self.shots_history
        )
        
        # Record the shot for AI learning
        # Note: We'll need to update this with actual result later
        self.shots_history.append((row, col, 'pending'))
        
        return FireAction(
            player_name=context.player_name,
            target_position=Position(row, col)
        )
    
    def update_shot_result(self, row: int, col: int, result: str):
        """Update the result of the last shot for AI learning."""
        # Find and update the pending shot
        for i, (shot_row, shot_col, shot_result) in enumerate(self.shots_history):
            if shot_row == row and shot_col == col and shot_result == 'pending':
                self.shots_history[i] = (row, col, result)
                break


class RandomAIAdapter(AIPort):
    """
    Simple random AI adapter for testing or easier gameplay.
    Provides basic random ship placement and firing decisions.
    """
    
    def __init__(self, board_size: Tuple[int, int]):
        self.board_size = board_size
        self.fired_positions = set()
    
    async def get_ship_placement_decision(self, context: PlacementContext) -> ShipPlacement:
        """Random AI decision for ship placement."""
        import random
        
        max_row, max_col = self.board_size
        
        # Simple random placement (could be improved)
        orientation = random.choice(['h', 'v'])
        
        if orientation == 'h':
            max_start_row = max_row
            max_start_col = max_col - context.ship.size + 1
        else:
            max_start_row = max_row - context.ship.size + 1
            max_start_col = max_col
        
        row = random.randint(0, max_start_row - 1)
        col = random.randint(0, max_start_col - 1)
        
        return ShipPlacement(
            player_name=context.player_name,
            ship=context.ship,
            orientation=orientation,
            start_position=Position(row, col)
        )
    
    async def get_fire_decision(self, context: FireContext) -> FireAction:
        """Random AI decision for fire action."""
        import random
        
        max_row, max_col = self.board_size
        
        # Find unfired position
        available_positions = []
        for row in range(max_row):
            for col in range(max_col):
                if (row, col) not in self.fired_positions:
                    available_positions.append((row, col))
        
        if available_positions:
            row, col = random.choice(available_positions)
            self.fired_positions.add((row, col))
        else:
            # Fallback if all positions fired (shouldn't happen)
            row, col = 0, 0
        
        return FireAction(
            player_name=context.player_name,
            target_position=Position(row, col)
        )


# AI Factory for easy selection
class AIFactory:
    """Factory for creating different AI adapters."""
    
    @staticmethod
    def create_ai(ai_type: str, board_size: Tuple[int, int]) -> AIPort:
        """Create AI adapter based on type."""
        
        if ai_type.lower() == 'standard':
            return StandardAIAdapter(board_size)
        elif ai_type.lower() == 'random':
            return RandomAIAdapter(board_size)
        else:
            raise ValueError(f"Unknown AI type: {ai_type}")
    
    @staticmethod
    def get_available_ai_types() -> List[str]:
        """Get list of available AI types."""
        return ['standard', 'random']