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

from board import Board
from config import Config
from player import Player


class Game:
    """Game class called in main module.
    Once a game class is instanced, it is used as an interface
    to renew the members of Player class.
    """

    def __init__(self, config: Config, player_names: list) -> None:
        """Initialize Game class variables.

        Args: 
            config (Config): Instanced config object.
            player_names (list): List of player names.
        """
        self.config = config
        self.player_names = player_names
        self.players = {}
        self.orient = ''
        self.location = []
        self.x = 0
        self.y = 0
        self.fire_x = 0
        self.fire_y = 0

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
                ship_size
            )

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

        orient = ''
        # H: Horizontal, V: Vertical
        while orient not in ['H', 'V']:
            orient = input(message_).rstrip().lstrip()
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
        obtained = True
        while obtained:
            location = input(message_).rstrip().lstrip()
            # If it is a correct format,
            # 2 characters should be contained in the variable location
            if len(re.findall('[0-9]+', location)) == 2:
                obtained = False
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
        # input messsage when CLI input interface is displayed.
        message_ = f"{player_name}, enter the location you want to fire at in the form row col:"
        obtained = True
        while obtained:
            # location to fire.
            fire_location = input(message_).rstrip().lstrip()
            if len(re.findall('[0-9]+', fire_location)) == 2:
                obtained = False
        fire_location = fire_location.split(' ')
        self.fire_x = int(fire_location[0])
        self.fire_y = int(fire_location[1])

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
            print(f"{player_name} hit {opponent_player_name}'s {target_symbol}")
        # Else if the target symbol is not a symbol of ships
        else:
            fired_symbol = 'X'
            print(f"{player_name} missed!")

        # fire action of turn player
        self.players[player_name].do_fire(
            self.fire_x, self.fire_y, fired_symbol)
        # being fired action of opponent player.
        self.players[opponent_player_name].be_fired(
            self.fire_x, self.fire_y, fired_symbol)
