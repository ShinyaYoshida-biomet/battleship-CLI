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

        # Initialize Player class for all players in `player_names``.
        for player_name in self.player_names:
            players[player_name] = Player(
                player_name, Board(r, c), Board(r, c), self.config)

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
        self.get_orient(player_name, ship_symbol, ship_size)
        status = False
        while not status:
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
        # input messsage when CLI input interface is displayed.
        message_ = f"{player_name}, enter the orientation of"
        message_ += f"your {ship_symbol}, which is {ship_size} long [H/V]:"

        # orient symbol abreviations like 'horizo', 'verti', etc.
        orient_symbols = []

        orient = ''
        # if orient expression was wrong, let user input it again.
        while orient not in self.h_symbols + self.v_symbols:
            orient = input(message_).rstrip().lstrip().lower()
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
        # input messsage when CLI input interface is displayed.
        message_ = f"Enter the starting location for your {ship_symbol}, "
        message_ += f"which is {ship_size} long, in the form row col(eg. 0 4): "
        obtained = False
        while not obtained:
            location = input(message_).rstrip().lstrip()
            # 2 numbers should be contained in the variable location
            if len(re.findall('[0-9]+', location)) >= 2:
                obtained = True

        location = location.split(' ')
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
        # input messsage when CLI input interface is displayed.
        message_ = f"{player_name}, enter the location you want to fire at in the form row col:"
        obtained = False
        while not obtained:
            # location to fire.
            fire_location = input(message_).rstrip().lstrip()
            # condition for the num of number is 2. EG. '9 9' is OK, '9 9 9' is NG.
            number_condition = len(re.findall('[0-9]+', fire_location)) == 2

            fire_location = fire_location.split(' ')
            row_num_condition = int(fire_location[0]) < self.config.row_num
            col_num_condition = int(fire_location[1]) < self.config.column_num
            if (number_condition) and (row_num_condition) and (col_num_condition):
                obtained = True

        self.fire_x = int(fire_location[0])
        self.fire_y = int(fire_location[1])

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
