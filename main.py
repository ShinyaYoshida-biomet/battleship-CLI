# -*- coding: utf-8 -*-
"""Main module to execute battleship game in CLI.
You can start the game by typing a command below in your command line.

Example:
    python main.py
    
"""
import os

from config import Config
from game import Game


def main():
    """Main module to execute battleship game in CLI.

    (There are no arguments and global variables.)
    """

    # obtain config path
    config_message = 'Please enter the path to the configuration file for this game:'
    config_path = input(config_message)

    # obtain player names
    player1_name = input('Player 1, please enter your name:')
    player2_name = input('Player 2, please enter your name:')
    player_names = [player1_name, player2_name]

    # Initialize game instance with config and player information.
    game = Game(Config(config_path), player_names)
    print("\n".join(game.config.config_text))
    game.set_players()

    # Player1 and Player2 initialize their battleship locations
    for player in player_names:
        game.display_placement_board(player)
        # Initialize battleship location
        for ship_symbol, ship_size in game.config.ship_dict.items():
            # get information to set a battleship
            game.get_orient(player, ship_symbol, ship_size)
            game.get_location(ship_symbol, ship_size)
            # set a battleship based on the information
            game.set_ships(player, ship_symbol, ship_size)

            game.display_placement_board(player)

        # clear console for good appearance
        os.system('sleep 2')
        os.system('clear')

    # Fire part
    finish_flag = False
    while not finish_flag:
        for player in player_names:
            # show turn player's firing board and placement board.
            game.display_firing_board(player)
            game.display_placement_board(player)

            # get fire location from CLI.
            game.get_fire_location(player)
            opponent_player = [k for k in player_names if k != player][0]
            # Fire!
            game.fire(player, opponent_player)

            # check left ships of the opponent player.
            game.players[opponent_player].get_left_ships()
            left_ships = game.players[opponent_player].left_ships

            # When there are no left ships game is end.
            if len(left_ships) == 0:
                print(f"{player} Won! Game was finished!")
                finish_flag = True
                break

            os.system('sleep 1.5')
            os.system('clear')


if __name__ == '__main__':
    main()

    # ToDo
    # 不要なモジュールを削除したり結合したり。
    # ボードの広さをはみ出てしまった時にやり直す処理
    # そのほかコメント。
