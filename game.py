# -*- coding: utf-8 -*-
"""Game class called in main module.

Players belong to game objects and 
gamd objects renew players' board.

Example:
    game = Game(Config(config_path), player_names)
    print('\n'.join(game.config.config_text))
    game.set_players()
"""

import re
import time
from typing import List, Tuple

from board import Board
from config import Config
from player import Player
from computer_ai import ComputerAI
from ui import ui


class Game:
    """Game class called in main module.
    Once a game class is instanced, it is used as an interface
    to renew the members of Player class.
    """

    def __init__(self, config: Config, player_names: list, player_types: list = None) -> None:
        """Initialize Game class variables.

        Args: 
            config (Config): Instanced config object.
            player_names (list): List of player names.
            player_types (list): List of player types ('human' or 'computer').
        """
        self.config = config
        self.player_names = player_names
        self.player_types = player_types if player_types else ['human', 'human']
        self.players = {}
        self.orient = ''
        self.location = []
        self.x = 0
        self.y = 0
        self.fire_x = 0
        self.fire_y = 0
        self.h_symbol = 'horizontal'
        self.h_symbols = [self.h_symbol[:i+1]
                          for i in range(len(self.h_symbol))]
        self.v_symbol = 'vertical'
        self.v_symbols = [self.v_symbol[:i+1]
                          for i in range(len(self.v_symbol))]
        
        # Track ship placement modes for human players
        self.placement_modes = {}  # player_name -> 'manual' or 'random'
        
        # Initialize computer AI if needed
        board_size = (config.row_num, config.column_num)
        self.computer_ai = {}
        self.computer_shots = {}  # Track computer shots for AI
        for i, player_type in enumerate(self.player_types):
            if player_type == 'computer':
                player_name = self.player_names[i]
                self.computer_ai[player_name] = ComputerAI(board_size)
                self.computer_shots[player_name] = []

    def set_players(self) -> None:
        """Function to initialize Player class.
        """
        players = {}
        r = self.config.row_num
        c = self.config.column_num

        # Initialize Player class for all players in `player_names``
        for player_name in self.player_names:
            placement_board = Board(r, c, 'placement')  # Board for ship placement
            firing_board = Board(r, c, 'firing')       # Board for attack tracking
            players[player_name] = Player(
                player_name, placement_board, firing_board, self.config)

        self.players = players

    def set_ship_placement_modes(self) -> None:
        """Set ship placement mode for each human player."""
        for i, player_name in enumerate(self.player_names):
            player_type = self.player_types[i]
            if player_type == 'human':
                # Ask human player for placement mode
                placement_mode = ui.prompt_ship_placement_mode(player_name)
                self.placement_modes[player_name] = placement_mode
                
                if placement_mode == 'random':
                    ui.console.print(f"[green]🎲 {player_name} chose random placement![/green]")
                else:
                    ui.console.print(f"[blue]🎯 {player_name} chose manual placement![/blue]")

    def set_ships(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Function to set ships on players' board.

        Args: 
            player_name (str): Name of a player to set board.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        player_index = self.player_names.index(player_name)
        player_type = self.player_types[player_index]
        
        if player_type == 'computer':
            # Computer ship placement
            self._set_computer_ship(player_name, ship_symbol, ship_size)
        else:
            # Human ship placement - check placement mode
            placement_mode = self.placement_modes.get(player_name, 'manual')
            if placement_mode == 'random':
                self._set_random_ship(player_name, ship_symbol, ship_size)
            else:
                self._set_human_ship(player_name, ship_symbol, ship_size)

    def _set_human_ship(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Set ship for human player using CLI input.
        
        Args: 
            player_name (str): Name of a player to set board.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship', 
            'D': 'Destroyer',
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        ship_display = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        
        status = False
        attempts = 0
        
        while not status:
            attempts += 1
            if attempts > 1:
                ui.console.print(f"\n[red]❌ Cannot place {ship_display} there![/red]")
                ui.console.print("[yellow]   Reasons this might happen:[/yellow]")
                ui.console.print("[yellow]   • Ship would go off the board[/yellow]")
                ui.console.print("[yellow]   • Ship would overlap with another ship[/yellow]")
                ui.console.print("[yellow]   Let's try a different position...[/yellow]\n")
            
            # get ship placement using single command
            self.get_ship_placement(player_name, ship_symbol, ship_size)
            status = self.players[player_name].placement_board.set_ship(
                self.orient,
                self.x,
                self.y,
                ship_symbol,
                ship_size,
                self.h_symbols,
                self.v_symbols
            )
            
        ui.console.print(f"[green]🎉 {ship_display} successfully placed![/green]")
        
        # Show the updated board after successful placement
        placement_board = self.players[player_name].placement_board.board
        board_table = ui.create_board_table(placement_board, f"🚢 Your Ships (Updated)", show_ships=True)
        ui.console.print(board_table)

    def _set_computer_ship(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Set ship for computer player using AI.
        
        Args: 
            player_name (str): Name of a player to set board.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        print(f"\n{player_name} is placing their {ship_symbol} (size {ship_size})...")
        
        # Get occupied positions from current board
        occupied_positions = self._get_occupied_positions(player_name)
        
        # Get AI decision for ship placement
        ai_orientation, ai_x, ai_y = self.computer_ai[player_name].get_ship_placement(
            ship_size, occupied_positions
        )
        
        # Convert AI orientation to game format
        self.orient = ai_orientation
        self.x = ai_x
        self.y = ai_y
        
        # Place the ship
        status = self.players[player_name].placement_board.set_ship(
            self.orient,
            self.x,
            self.y,
            ship_symbol,
            ship_size,
            self.h_symbols,
            self.v_symbols
        )
        
        if status:
            print(f"{player_name} placed {ship_symbol} at ({ai_x}, {ai_y}) {ai_orientation}")
        else:
            print(f"Warning: {player_name} ship placement failed, trying again...")
            # Fallback: try again (should be rare with AI logic)
            self._set_computer_ship(player_name, ship_symbol, ship_size)

    
    def _set_random_ship(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Set ship for human player using random placement.
        
        Args: 
            player_name (str): Name of a player to set board.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship', 
            'D': 'Destroyer',
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        ship_display = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        
        ui.console.print(f"\n[cyan]🎲 Randomly placing {ship_display}...[/cyan]")
        
        # Get occupied positions from current board
        occupied_positions = self._get_occupied_positions(player_name)
        
        # Use the same AI logic as computer for random placement
        board_size = (self.config.row_num, self.config.column_num)
        temp_ai = ComputerAI(board_size)
        ai_orientation, ai_x, ai_y = temp_ai.get_ship_placement(ship_size, occupied_positions)
        
        # Convert AI orientation to game format
        self.orient = ai_orientation
        self.x = ai_x
        self.y = ai_y
        
        # Place the ship
        status = self.players[player_name].placement_board.set_ship(
            self.orient,
            self.x,
            self.y,
            ship_symbol,
            ship_size,
            self.h_symbols,
            self.v_symbols
        )
        
        if status:
            ui.console.print(f"[green]✨ {ship_display} randomly placed at ({ai_x}, {ai_y}) {ai_orientation}![/green]")
        else:
            ui.console.print(f"[red]Warning: Random placement failed, trying again...[/red]")
            # Fallback: try again
            self._set_random_ship(player_name, ship_symbol, ship_size)
    
    def _get_occupied_positions(self, player_name: str) -> List[Tuple[int, int]]:
        """Get list of occupied positions on player's placement board.
        
        Args:
            player_name (str): Name of the player.
            
        Returns:
            List[Tuple[int, int]]: List of (x, y) tuples of occupied positions.
        """
        occupied = []
        board = self.players[player_name].placement_board.board
        
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                # Check if the cell is not water ('*' for placement board)
                if board.iloc[x, y] != '*':
                    occupied.append((x, y))
        
        return occupied

    def get_ship_placement(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Function to get ship placement using single command format.

        Args: 
            player_name (str): Name of turn player.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        board_size = (self.config.row_num, self.config.column_num)
        
        # Use Rich UI for single command ship placement
        orient, row, col = ui.prompt_ship_placement(player_name, ship_symbol, ship_size, board_size)
        
        # Set game instance variables
        self.orient = orient
        self.x = row
        self.y = col


    def display_placement_board(self, player_name: str) -> None:
        """Function to display placement board

        Args: 
            player_name (str): Name of turn player.
        """
        # This method is deprecated - use display_boards_side_by_side instead
        placement_board = self.players[player_name].placement_board.board
        ui.create_board_table(placement_board, f"🚢 Your Ships", show_ships=True)

    def display_firing_board(self, player_name: str) -> None:
        """Function to display firing board

        Args: 
            player_name (str): Name of turn player.
        """
        # This method is deprecated - use display_boards_side_by_side instead
        firing_board = self.players[player_name].firing_board.board
        ui.create_board_table(firing_board, f"🎯 Your Attacks", show_ships=False)

    def display_boards_side_by_side(self, player_name: str) -> None:
        """Display firing and placement boards side by side using Rich UI.
        
        Args:
            player_name (str): Name of the player whose boards to display.
        """
        firing_board = self.players[player_name].firing_board.board
        placement_board = self.players[player_name].placement_board.board
        
        # Get opponent player information
        opponent_player = [k for k in self.player_names if k != player_name][0]
        
        # Make sure opponent's ship status is up to date
        self.players[opponent_player].get_left_ships()
        opponent_left_ships = self.players[opponent_player].left_ships if hasattr(self.players[opponent_player], 'left_ships') else None
        
        # Use the Rich UI to display side-by-side boards with ship status
        ui.display_boards_side_by_side(
            player_name=player_name,
            firing_board=firing_board,
            placement_board=placement_board,
            ships_config=self.config.ship_dict,
            opponent_name=opponent_player,
            opponent_left_ships=opponent_left_ships
        )

    def get_fire_location(self, player_name: str) -> None:
        """Function to get location to fire

        Args:
            player_name (str): Name of turn player.
        """
        player_index = self.player_names.index(player_name)
        player_type = self.player_types[player_index]
        
        if player_type == 'computer':
            self._get_computer_fire_location(player_name)
        else:
            self._get_human_fire_location(player_name)

    def _get_human_fire_location(self, player_name: str) -> None:
        """Get fire location from human player via Rich UI input.
        
        Args:
            player_name (str): Name of turn player.
        """
        board_size = (self.config.row_num, self.config.column_num)
        
        while True:
            # Use Rich UI for firing location prompt
            row, col = ui.prompt_fire_location(player_name, board_size)
            
            # Check if already fired at this location
            current_cell = self.players[player_name].firing_board.board.iloc[row, col]
            if current_cell != ' ':
                ui.console.print(f"[red]❌ You already fired at ({row}, {col})! Choose a different target.[/red]")
                continue
                
            self.fire_x = row
            self.fire_y = col
            break

    def _get_computer_fire_location(self, player_name: str) -> None:
        """Get fire location from computer AI using Rich UI.
        
        Args:
            player_name (str): Name of turn player.
        """
        # Show computer thinking with Rich UI
        ui.show_computer_thinking(player_name)
        time.sleep(0.3)  # Brief suspense
        
        # Get current firing board state
        firing_board_data = self._get_board_data(player_name, 'firing')
        
        # Get AI firing decision
        ai_x, ai_y = self.computer_ai[player_name].get_fire_location(
            firing_board_data, 
            self.computer_shots[player_name]
        )
        
        self.fire_x = ai_x
        self.fire_y = ai_y
        
        # Show computer action with Rich UI
        ui.show_computer_action(player_name, "fires", f"at ({ai_x}, {ai_y})")

    def _get_board_data(self, player_name: str, board_type: str) -> List[List[str]]:
        """Get board data as 2D list for AI processing.
        
        Args:
            player_name (str): Name of the player.
            board_type (str): 'firing' or 'placement'.
            
        Returns:
            List[List[str]]: 2D list representation of the board.
        """
        if board_type == 'firing':
            board = self.players[player_name].firing_board.board
        else:
            board = self.players[player_name].placement_board.board
            
        board_data = []
        for x in range(board.shape[0]):
            row = []
            for y in range(board.shape[1]):
                row.append(board.iloc[x, y])
            board_data.append(row)
            
        return board_data

    def is_human_player(self, player_name: str) -> bool:
        """Check if a player is human.
        
        Args:
            player_name (str): Name of the player.
            
        Returns:
            bool: True if player is human, False if computer.
        """
        player_index = self.player_names.index(player_name)
        return self.player_types[player_index] == 'human'

    def fire(self, player_name: str, opponent_player_name: str) -> None:
        """Function to execute fire action using Rich UI.

        Args: 
            player_name (str): Name of turn player.
            opponent_player_name (str): Name of opponent player of turn player.
        """
        # Current symbol located at fire position.
        target_symbol = self.players[opponent_player_name].placement_board.board.iloc[
            self.fire_x,
            self.fire_y
        ]

        # if the target symbol is a symbol of ships
        if target_symbol in self.config.ship_dict.keys():
            fired_symbol = 'O'
            result = 'X'  # Hit for AI tracking
            hit = True
        # Else if the target symbol is not a symbol of ships
        else:
            fired_symbol = 'X'
            result = 'O'  # Miss for AI tracking
            hit = False

        # Show fire result with Rich UI
        ui.show_fire_result(
            player_name, 
            opponent_player_name, 
            self.fire_x, 
            self.fire_y, 
            hit, 
            target_symbol if hit else None
        )

        # Track computer shots for AI learning
        player_index = self.player_names.index(player_name)
        if self.player_types[player_index] == 'computer':
            shot_record = (self.fire_x, self.fire_y, result)
            self.computer_shots[player_name].append(shot_record)

        # fire action of turn player
        self.players[player_name].do_fire(
            self.fire_x, self.fire_y, fired_symbol)
        # being fired action of opponent player.
        self.players[opponent_player_name].be_fired(
            self.fire_x, self.fire_y, fired_symbol)
