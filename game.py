import re
import numpy as np

from board import Board
from config import Config
from player import Player


class Game:
    def __init__(self, config: Config, player_names: list):
        self.config = config
        self.player_names = player_names
        self.players = {}
        self.orient = ''
        self.location = []
        self.x = 0
        self.y = 0
        self.fire_x = 0
        self.fire_y = 0

    def set_players(self):
        players = {}
        r = self.config.row_num
        c = self.config.column_num

        for player_name in self.player_names:
            players[player_name] = Player(
                player_name, Board(r, c), Board(r, c), self.config)

        self.players = players

    def set_ships(self, player_name, ship_symbol, ship_size):
        self.players[player_name].placement_board.set_ship(
            self.orient,
            self.x,
            self.y,
            ship_symbol,
            ship_size
        )

    def get_orient(self, player_name, ship_symbol, ship_size):
        message_ = f"{player_name}, enter the orientation of"
        message_ += f"your {ship_symbol}, which is {ship_size} long [H/V]:"

        orient = ''
        while orient not in ['H', 'V']:
            orient = input(message_).rstrip().lstrip()
        self.orient = orient

    def get_location(self, ship_symbol, ship_size):
        message_ = f"Enter the starting location for your {ship_symbol}, "
        message_ += f"which is {ship_size} long, in the form row col(eg. 0 4): "
        obtained = True
        while obtained:
            location = input(message_).rstrip().lstrip()
            if len(re.findall('[0-9]+', location)) == 2:
                obtained = False
        location = location.split(' ')
        self.x = int(location[0])
        self.y = int(location[1])

    def display_placement_board(self, player_name):
        print(f"{player_name}\'s placement board:")
        print(self.players[player_name].placement_board.board)

    def display_firing_board(self, player_name):
        print(f"{player_name}\'s firing board:")
        print(self.players[player_name].firing_board.board)

    def get_fire_location(self, player_name):
        message_ = f"{player_name}, enter the location you want to fire at in the form row col:"
        obtained = True
        while obtained:
            fire_location = input(message_).rstrip().lstrip()
            if len(re.findall('[0-9]+', fire_location)) == 2:
                obtained = False
        fire_location = fire_location.split(' ')
        self.fire_x = int(fire_location[0])
        self.fire_y = int(fire_location[1])

    def fire(self, player_name, opponent_player_name):

        target_symbol = self.players[opponent_player_name].placement_board.board.iloc[
            self.fire_x,
            self.fire_y
        ]

        if target_symbol in self.config.ship_dict.keys():
            fired_symbol = 'O'
            print(f"{player_name} hit {opponent_player_name}'s {target_symbol}")
        else:
            fired_symbol = 'X'
            print(f"{player_name} missed!")

        self.players[player_name].do_fire(
            self.fire_x, self.fire_y, fired_symbol)
        self.players[opponent_player_name].be_fired(
            self.fire_x, self.fire_y, fired_symbol)
