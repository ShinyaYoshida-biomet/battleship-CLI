"""Computer AI adapter implementation."""
import random
from typing import List, Tuple, Set

from ...domain.entities.board import Board, CellState
from ...domain.value_objects.position import Position
from ...domain.value_objects.ship_placement import ShipPlacement, Orientation
from ...ports.ai_port import AIPort


class ComputerAIAdapter(AIPort):
    """Computer AI implementation with intelligent hunting strategy."""
    
    def __init__(self, board_rows: int = 7, board_cols: int = 7):
        self.board_rows = board_rows
        self.board_cols = board_cols
        self.hit_positions: Set[Position] = set()
        self.hunt_targets: List[Position] = []
        self.last_hit: Position = None
        self.hunt_direction: str = None  # 'horizontal' or 'vertical'
        
    def get_ship_placement(
        self, 
        ship_size: int, 
        board: Board,
        existing_ships: List[Position]
    ) -> ShipPlacement:
        """Get AI decision for ship placement using smart positioning."""
        max_attempts = 1000
        
        for _ in range(max_attempts):
            # Choose random orientation
            orientation = random.choice([Orientation.HORIZONTAL, Orientation.VERTICAL])
            
            # Choose random starting position
            if orientation == Orientation.HORIZONTAL:
                max_row = self.board_rows - 1
                max_col = self.board_cols - ship_size
                if max_col < 0:
                    continue
                start_pos = Position(
                    random.randint(0, max_row),
                    random.randint(0, max_col)
                )
            else:  # VERTICAL
                max_row = self.board_rows - ship_size
                max_col = self.board_cols - 1
                if max_row < 0:
                    continue
                start_pos = Position(
                    random.randint(0, max_row),
                    random.randint(0, max_col)
                )
            
            # Check if this placement is valid
            placement = ShipPlacement(start_pos, orientation)
            ship_positions = placement.calculate_positions(ship_size)
            
            # Check if any position is already occupied
            if not any(pos in existing_ships for pos in ship_positions):
                return placement
        
        # Fallback: return a simple placement (should rarely happen)
        return ShipPlacement(Position(0, 0), Orientation.HORIZONTAL)
    
    def get_fire_location(
        self, 
        opponent_board: Board,
        firing_history: List[Tuple[Position, str]]
    ) -> Position:
        """Get AI decision for firing location using hunt/target strategy."""
        
        # Update internal state based on firing history
        self._update_from_history(firing_history)
        
        # If we have hunt targets (from previous hits), prioritize them
        if self.hunt_targets:
            return self._get_hunt_target()
        
        # Otherwise, use search pattern
        return self._get_search_target(opponent_board)
    
    def update_shot_result(self, position: Position, result: str) -> None:
        """Update AI with the result of its last shot."""
        if result == "hit":
            self.hit_positions.add(position)
            self.last_hit = position
            self._generate_hunt_targets(position)
        elif result == "miss" and position in self.hunt_targets:
            self.hunt_targets.remove(position)
    
    def reset(self) -> None:
        """Reset AI state for a new game."""
        self.hit_positions.clear()
        self.hunt_targets.clear()
        self.last_hit = None
        self.hunt_direction = None
    
    def _update_from_history(self, firing_history: List[Tuple[Position, str]]) -> None:
        """Update internal state from firing history."""
        self.hit_positions.clear()
        
        for position, result in firing_history:
            if result == "hit":
                self.hit_positions.add(position)
                self.last_hit = position
    
    def _get_hunt_target(self) -> Position:
        """Get next target from hunt list."""
        if self.hunt_targets:
            return self.hunt_targets.pop(0)
        
        # Fallback to search pattern
        return self._get_search_target(None)
    
    def _get_search_target(self, board: Board) -> Position:
        """Get search target using checkerboard pattern."""
        # Get all valid positions
        valid_positions = []
        
        for row in range(self.board_rows):
            for col in range(self.board_cols):
                position = Position(row, col)
                
                # Skip if already fired at
                if board and not board.is_valid_position(position):
                    continue
                
                if board:
                    cell_state = board.get_cell_state(position)
                    if cell_state in [CellState.HIT, CellState.MISS]:
                        continue
                
                # Use checkerboard pattern for efficiency
                if (row + col) % 2 == 0:
                    valid_positions.append(position)
        
        # Add remaining positions if checkerboard is exhausted
        if not valid_positions:
            for row in range(self.board_rows):
                for col in range(self.board_cols):
                    position = Position(row, col)
                    
                    if board and not board.is_valid_position(position):
                        continue
                    
                    if board:
                        cell_state = board.get_cell_state(position)
                        if cell_state in [CellState.HIT, CellState.MISS]:
                            continue
                    
                    valid_positions.append(position)
        
        if valid_positions:
            return random.choice(valid_positions)
        
        # Fallback
        return Position(0, 0)
    
    def _generate_hunt_targets(self, hit_position: Position) -> None:
        """Generate hunt targets around a hit."""
        row, col = hit_position.row, hit_position.col
        
        # Add adjacent positions as hunt targets
        adjacent_positions = [
            Position(row - 1, col),  # Up
            Position(row + 1, col),  # Down
            Position(row, col - 1),  # Left
            Position(row, col + 1),  # Right
        ]
        
        for pos in adjacent_positions:
            if (0 <= pos.row < self.board_rows and 
                0 <= pos.col < self.board_cols and 
                pos not in self.hit_positions):
                
                # Don't add if already in hunt targets
                if pos not in self.hunt_targets:
                    self.hunt_targets.append(pos)
    
    def _is_valid_position(self, position: Position) -> bool:
        """Check if position is within board bounds."""
        return (0 <= position.row < self.board_rows and 
                0 <= position.col < self.board_cols)