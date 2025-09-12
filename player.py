# -*- coding: utf-8 -*-
"""Player module called in game instance.

This module consist of a class named 'Player'.
The Player object has a board in it and
methods to change the boardwhen they are fired.

Example:
    player_x = Player('name', Board(3, 3), Board(3, 3))
    player_x.be_fired(1, 1, 'X')
    print(player_x.placement_board.board)
"""

import numpy as np

from config import Config
from board import Board


class Player:
    """Player class of battleship game.
    A player has both placement board and firing board.
    Player class has the method to change their board when firing.
    """

    def __init__(
        self,
        player_name: str,
        placement_board: Board,
        firing_board: Board,
        config: Config
    ) -> None:
        """Initialize Player class variables.

        Args:
            player_name (str): name of a player.
            placement_board (Board): A board object used as placement board, 
                showing which ships are alived.
            firing_board (Board): A board object used as firing board,
                showing which cells are already fired.
        """
        self.name = player_name
        self.placement_board = placement_board
        self.firing_board = firing_board
        self.left_ships = config.ship_dict.keys()

    def do_fire(
            self,
            fire_x: int,
            fire_y: int,
            fired_symbol: str
    ) -> None:
        """Process when a player did fire

        Args:
            fire_x (int): x cordinate to fire.
            fire_y (int): y cordinate to fire.
            fired_symbol (str): 'X' or 'O', 
                respectively expressing missed and hit.
        """
        self.firing_board.board.iloc[
            fire_x,
            fire_y
        ] = fired_symbol

    def be_fired(self, fire_x, fire_y, fired_symbol) -> None:
        """Process when a player is fired

        Args:
            fire_x (int): x cordinate to be fired.
            fire_y (int): y cordinate to be fired.
            fired_symbol (str): 'X' or 'O', 
                respectively expressing missed and hit.
        """
        self.placement_board.board.iloc[
            fire_x,
            fire_y
        ] = fired_symbol

    def get_left_ships(self) -> None:
        """Method to know non-destroyed ships.

        This function computes the left ships in player's board and
        let you know when entire ship is destroyed.
        """
        # Get all cells from the placement board
        all_cells = self.placement_board.board.values.flatten().tolist()
        
        # Count intact cells for each ship type
        ship_counts = {}
        for cell in all_cells:
            # Skip water ('*'), missed shots ('X'), and hit ships ('O')
            if cell not in ['*', 'X', 'O']:  
                ship_counts[cell] = ship_counts.get(cell, 0) + 1
        
        # Get unique ship types that still have intact cells
        current_left_ships = list(ship_counts.keys())
        
        # Find ships that were destroyed since last check
        previous_ships = set(self.left_ships) if hasattr(self, 'left_ships') else set()
        current_ships = set(current_left_ships)
        diff_left_ships = list(previous_ships - current_ships)

        # Announce destroyed ships
        if len(diff_left_ships) > 0:
            for destroyed_ship in diff_left_ships:
                print(f"{self.name}'s {destroyed_ship} is destroyed!")
        
        # Update left ships
        self.left_ships = current_left_ships
