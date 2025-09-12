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
            # Human ship placement
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
        
        self.get_orient(player_name, ship_symbol, ship_size)
        status = False
        attempts = 0
        
        while not status:
            attempts += 1
            if attempts > 1:
                print(f"\n❌ Cannot place {ship_display} there!")
                print("   Reasons this might happen:")
                print("   • Ship would go off the board")
                print("   • Ship would overlap with another ship")
                print("   Let's try a different position...\n")
            
            # get information to set a battleship
            self.get_location(ship_symbol, ship_size)
            status = self.players[player_name].placement_board.set_ship(
                self.orient,
                self.x,
                self.y,
                ship_symbol,
                ship_size,
                self.h_symbols,
                self.v_symbols
            )
            
        print(f"🎉 {ship_display} successfully placed!")

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
                if board.iloc[x, y] != ' ':
                    occupied.append((x, y))
        
        return occupied

    def get_orient(
        self,
        player_name: str,
        ship_symbol: str,
        ship_size: str
    ) -> None:
        """Function to set orientation obtained from CLI

        Args: 
            player_name (str): Name of turn player.
            ship_symbol (str): The name(symbol) of a ship to set.
            ship_size (int): The length of a ship to set.
        """
        # Create clear, user-friendly message
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship', 
            'D': 'Destroyer',
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        ship_display = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        
        print(f"\n🚢 {player_name}, placing your {ship_display}")
        print(f"   Size: {ship_size} cells")
        print("   Choose orientation:")
        print("   H = Horizontal (→→→)")
        print("   V = Vertical   (↓)")
        print("                  (↓)")
        print("                  (↓)")
        
        orient = ''
        # if orient expression was wrong, let user input it again.
        while orient not in self.h_symbols + self.v_symbols:
            orient = input(f"Enter orientation [H=Horizontal/V=Vertical]: ").rstrip().lstrip().lower()
            if orient not in self.h_symbols + self.v_symbols:
                print("❌ Please enter 'H' for Horizontal or 'V' for Vertical")
        
        direction_text = "Horizontally" if orient in self.h_symbols else "Vertically"
        print(f"✅ Placing {direction_text}!")
        self.orient = orient

    def get_location(
        self,
        ship_symbol: str,
        ship_size: int
    ) -> None:
        """Function to set location obtained from CLI

        Args: 
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
        
        print(f"\n📍 Where do you want to place your {ship_display}?")
        print(f"   This ship is {ship_size} cells long")
        print("   Enter the starting position as: row column")
        print("   Example: '2 5' means row 2, column 5")
        print("   (Remember: coordinates start from 0)")
        
        obtained = False
        while not obtained:
            location = input("Starting position (row column): ").rstrip().lstrip()
            # 2 numbers should be contained in the variable location
            numbers = re.findall('[0-9]+', location)
            if len(numbers) >= 2:
                row, col = int(numbers[0]), int(numbers[1])
                # Check if coordinates are within bounds
                if (0 <= row < self.config.row_num and 
                    0 <= col < self.config.column_num):
                    obtained = True
                    print(f"✅ Starting at row {row}, column {col}")
                else:
                    print(f"❌ Position out of bounds! Board is {self.config.row_num}x{self.config.column_num} (0-{self.config.row_num-1}, 0-{self.config.column_num-1})")
            else:
                print("❌ Please enter two numbers separated by space (e.g., '2 5')")

        location = location.split()
        self.x = int(location[0])
        self.y = int(location[1])

    def display_placement_board(self, player_name: str) -> None:
        """Function to display placement board

        Args: 
            player_name (str): Name of turn player.
        """
        print(f"{player_name}\'s placement board:")
        print(self.players[player_name].placement_board.board)

    def display_firing_board(self, player_name: str) -> None:
        """Function to display firing board

        Args: 
            player_name (str): Name of turn player.
        """
        print(f"{player_name}\'s firing board:")
        print(self.players[player_name].firing_board.board)

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
        """Get fire location from human player via CLI input.
        
        Args:
            player_name (str): Name of turn player.
        """
        print(f"\n🎯 {player_name}, time to fire!")
        print("   Enter the coordinates you want to attack")
        print("   Format: row column (e.g., '3 7' for row 3, column 7)")
        print("   Coordinates start from 0")
        print(f"   Valid range: 0-{self.config.row_num-1} for rows, 0-{self.config.column_num-1} for columns")
        
        obtained = False
        while not obtained:
            fire_location = input("Target coordinates (row column): ").rstrip().lstrip()
            
            # Check if we have exactly 2 numbers
            numbers = re.findall('[0-9]+', fire_location)
            if len(numbers) != 2:
                print("❌ Please enter exactly two numbers separated by space (e.g., '3 7')")
                continue
            
            row, col = int(numbers[0]), int(numbers[1])
            
            # Check bounds
            if not (0 <= row < self.config.row_num and 0 <= col < self.config.column_num):
                print(f"❌ Coordinates out of bounds! Valid range: 0-{self.config.row_num-1}, 0-{self.config.column_num-1}")
                continue
                
            # Check if already fired at this location
            current_cell = self.players[player_name].firing_board.board.iloc[row, col]
            if current_cell != ' ':
                print(f"❌ You already fired at ({row}, {col})! Choose a different target.")
                continue
                
            obtained = True
            print(f"🎯 Firing at row {row}, column {col}!")

        self.fire_x = row
        self.fire_y = col

    def _get_computer_fire_location(self, player_name: str) -> None:
        """Get fire location from computer AI.
        
        Args:
            player_name (str): Name of turn player.
        """
        print(f"\n{player_name} is thinking...")
        time.sleep(1)  # Add suspense
        
        # Get current firing board state
        firing_board_data = self._get_board_data(player_name, 'firing')
        
        # Get AI firing decision
        ai_x, ai_y = self.computer_ai[player_name].get_fire_location(
            firing_board_data, 
            self.computer_shots[player_name]
        )
        
        self.fire_x = ai_x
        self.fire_y = ai_y
        
        print(f"{player_name} fires at ({ai_x}, {ai_y})!")

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
        """Function to execute fire action.

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
            print(f"{player_name} hit {opponent_player_name}'s {target_symbol}!")
        # Else if the target symbol is not a symbol of ships
        else:
            fired_symbol = 'X'
            result = 'O'  # Miss for AI tracking
            print(f"{player_name} missed!")

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
