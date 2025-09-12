# -*- coding: utf-8 -*-
"""Computer AI for battleship game.

This module contains the ComputerAI class that handles
automated ship placement and firing decisions for computer players.

Example:
    ai = ComputerAI(board_size=(10, 10))
    orientation, x, y = ai.get_ship_placement(ship_size=5, placed_ships=[])
    fire_x, fire_y = ai.get_fire_location(firing_board, placement_board)
"""

import random
from typing import Tuple, List, Optional


class ComputerAI:
    """Computer AI for battleship game decisions."""
    
    def __init__(self, board_size: Tuple[int, int]) -> None:
        """Initialize ComputerAI with board dimensions.
        
        Args:
            board_size (Tuple[int, int]): Board dimensions (rows, cols).
        """
        self.board_rows = board_size[0]
        self.board_cols = board_size[1]
        self.last_hit = None
        self.target_queue = []
        self.firing_mode = "hunt"  # "hunt" or "target"
        self.hit_direction = None
        self.original_hit = None
        
    def get_ship_placement(
        self,
        ship_size: int,
        occupied_positions: List[Tuple[int, int]]
    ) -> Tuple[str, int, int]:
        """Get computer's ship placement decision.
        
        Args:
            ship_size (int): Size of the ship to place.
            occupied_positions (List[Tuple[int, int]]): Already occupied board positions.
            
        Returns:
            Tuple[str, int, int]: Orientation ('horizontal' or 'vertical'), x, y coordinates.
        """
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            # Randomly choose orientation
            orientation = random.choice(['horizontal', 'vertical'])
            
            # Calculate valid placement ranges
            if orientation == 'horizontal':
                max_x = self.board_rows - 1
                max_y = self.board_cols - ship_size
            else:  # vertical
                max_x = self.board_rows - ship_size
                max_y = self.board_cols - 1
                
            if max_x < 0 or max_y < 0:
                attempts += 1
                continue
                
            # Random starting position
            x = random.randint(0, max_x)
            y = random.randint(0, max_y)
            
            # Check if placement is valid (no collisions)
            ship_positions = []
            if orientation == 'horizontal':
                ship_positions = [(x, y + i) for i in range(ship_size)]
            else:  # vertical
                ship_positions = [(x + i, y) for i in range(ship_size)]
                
            # Check for collisions
            if not any(pos in occupied_positions for pos in ship_positions):
                return orientation, x, y
                
            attempts += 1
            
        # Fallback: return first valid position found
        return self._find_first_valid_placement(ship_size, occupied_positions)
    
    def _find_first_valid_placement(
        self,
        ship_size: int,
        occupied_positions: List[Tuple[int, int]]
    ) -> Tuple[str, int, int]:
        """Find first valid ship placement systematically.
        
        Args:
            ship_size (int): Size of the ship to place.
            occupied_positions (List[Tuple[int, int]]): Already occupied board positions.
            
        Returns:
            Tuple[str, int, int]: Orientation, x, y coordinates.
        """
        # Try horizontal first
        for x in range(self.board_rows):
            for y in range(self.board_cols - ship_size + 1):
                ship_positions = [(x, y + i) for i in range(ship_size)]
                if not any(pos in occupied_positions for pos in ship_positions):
                    return 'horizontal', x, y
                    
        # Try vertical
        for x in range(self.board_rows - ship_size + 1):
            for y in range(self.board_cols):
                ship_positions = [(x + i, y) for i in range(ship_size)]
                if not any(pos in occupied_positions for pos in ship_positions):
                    return 'vertical', x, y
                    
        # Should never reach here if board has space
        return 'horizontal', 0, 0
    
    def get_fire_location(
        self,
        firing_board_data: List[List[str]],
        previous_shots: List[Tuple[int, int, str]]
    ) -> Tuple[int, int]:
        """Get computer's firing decision using hunt/target strategy.
        
        Args:
            firing_board_data (List[List[str]]): Current firing board state.
            previous_shots (List[Tuple[int, int, str]]): List of (x, y, result) tuples.
            
        Returns:
            Tuple[int, int]: Fire coordinates (x, y).
        """
        # Update AI state based on previous shots
        self._update_firing_state(previous_shots)
        
        if self.firing_mode == "target" and self.target_queue:
            # Target mode: fire around known hits
            return self._get_target_shot(firing_board_data)
        else:
            # Hunt mode: random firing with some intelligence
            return self._get_hunt_shot(firing_board_data)
    
    def _update_firing_state(self, previous_shots: List[Tuple[int, int, str]]) -> None:
        """Update AI firing state based on shot history.
        
        Args:
            previous_shots (List[Tuple[int, int, str]]): List of (x, y, result) tuples.
        """
        if not previous_shots:
            return
            
        last_shot = previous_shots[-1]
        x, y, result = last_shot
        
        if result == 'X':  # Hit
            if self.firing_mode == "hunt":
                # Switch to target mode
                self.firing_mode = "target"
                self.original_hit = (x, y)
                self.last_hit = (x, y)
                # Add adjacent cells to target queue
                self._add_adjacent_targets(x, y)
            elif self.firing_mode == "target":
                # Continue in target mode, update direction if needed
                self.last_hit = (x, y)
                if self.hit_direction is None:
                    # Determine direction from original hit
                    orig_x, orig_y = self.original_hit
                    if x == orig_x:  # Same row, horizontal ship
                        self.hit_direction = "horizontal"
                    elif y == orig_y:  # Same col, vertical ship
                        self.hit_direction = "vertical"
                
                # Add more targets in the determined direction
                if self.hit_direction:
                    self._add_directional_targets(x, y)
                else:
                    self._add_adjacent_targets(x, y)
                    
        elif result == 'O':  # Miss
            # Remove missed location from queue if it was there
            if (x, y) in self.target_queue:
                self.target_queue.remove((x, y))
                
        # Check if we should return to hunt mode
        if self.firing_mode == "target" and not self.target_queue:
            self._reset_to_hunt_mode()
    
    def _add_adjacent_targets(self, x: int, y: int) -> None:
        """Add adjacent cells to target queue.
        
        Args:
            x (int): X coordinate of hit.
            y (int): Y coordinate of hit.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # right, left, down, up
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.board_rows and 
                0 <= new_y < self.board_cols and
                (new_x, new_y) not in self.target_queue):
                self.target_queue.append((new_x, new_y))
    
    def _add_directional_targets(self, x: int, y: int) -> None:
        """Add targets in the determined direction.
        
        Args:
            x (int): X coordinate of hit.
            y (int): Y coordinate of hit.
        """
        if self.hit_direction == "horizontal":
            # Add left and right
            for dy in [-1, 1]:
                new_x, new_y = x, y + dy
                if (0 <= new_y < self.board_cols and
                    (new_x, new_y) not in self.target_queue):
                    self.target_queue.append((new_x, new_y))
        elif self.hit_direction == "vertical":
            # Add up and down
            for dx in [-1, 1]:
                new_x, new_y = x + dx, y
                if (0 <= new_x < self.board_rows and
                    (new_x, new_y) not in self.target_queue):
                    self.target_queue.append((new_x, new_y))
    
    def _reset_to_hunt_mode(self) -> None:
        """Reset AI to hunt mode."""
        self.firing_mode = "hunt"
        self.last_hit = None
        self.hit_direction = None
        self.original_hit = None
        self.target_queue = []
    
    def _get_target_shot(self, firing_board_data: List[List[str]]) -> Tuple[int, int]:
        """Get next target shot from queue.
        
        Args:
            firing_board_data (List[List[str]]): Current firing board state.
            
        Returns:
            Tuple[int, int]: Fire coordinates (x, y).
        """
        while self.target_queue:
            x, y = self.target_queue.pop(0)
            # Check if this position hasn't been fired at yet
            if firing_board_data[x][y] == ' ':
                return x, y
                
        # If no valid targets in queue, return to hunt mode
        self._reset_to_hunt_mode()
        return self._get_hunt_shot(firing_board_data)
    
    def _get_hunt_shot(self, firing_board_data: List[List[str]]) -> Tuple[int, int]:
        """Get hunt mode shot (random unfired position).
        
        Args:
            firing_board_data (List[List[str]]): Current firing board state.
            
        Returns:
            Tuple[int, int]: Fire coordinates (x, y).
        """
        # Get all unfired positions
        unfired_positions = []
        for x in range(self.board_rows):
            for y in range(self.board_cols):
                if firing_board_data[x][y] == ' ':
                    unfired_positions.append((x, y))
        
        if unfired_positions:
            return random.choice(unfired_positions)
        else:
            # Should never happen, but fallback
            return 0, 0