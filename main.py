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

    print("Battle ship game has started!!!")
    with open('images/ship_ascii', 'r') as f:
        print(f.read())
        
    # Select game mode
    print("\nGame Modes:")
    print("1. Player vs Player")
    print("2. Player vs Computer")
    
    game_mode = ''
    while game_mode not in ['1', '2']:
        game_mode = input('Please select game mode (1 or 2): ').strip()
    
    # obtain config path
    config_message = 'Please enter the path to the configuration file for this game:'
    config_path = input(config_message)

    # obtain player names based on game mode
    if game_mode == '1':
        # Player vs Player mode
        player1_name = input('Player 1, please enter your name:')
        player2_name = input('Player 2, please enter your name:')
        player_names = [player1_name, player2_name]
        player_types = ['human', 'human']
    else:
        # Player vs Computer mode
        player1_name = input('Player, please enter your name:')
        player2_name = 'Computer'
        player_names = [player1_name, player2_name]
        player_types = ['human', 'computer']
        print(f"You will be playing against the {player2_name}!")

    # Initialize game instance with config and player information.
    game = Game(Config(config_path), player_names, player_types)
    print("\n".join(game.config.config_text))
    game.set_players()

    # Player1 and Player2 initialize their battleship locations
    for player in player_names:
        # Only show board to human players
        if game.is_human_player(player):
            print(f"\n=== {player}'s Ship Placement ===")
            game.display_placement_board(player)
        else:
            print(f"\n=== {player} is placing ships ===")
            
        # Initialize battleship location
        for ship_symbol, ship_size in game.config.ship_dict.items():
            # set a battleship based on the information
            game.set_ships(player, ship_symbol, ship_size)

            # Only show updated board to human players
            if game.is_human_player(player):
                game.display_placement_board(player)

        # clear console for good appearance
        if game.is_human_player(player):
            print("\nShip placement complete! Get ready for battle...")
            os.system('sleep 2')
            os.system('clear')
        else:
            print(f"{player} has finished placing ships!")
            os.system('sleep 1')

    # Fire part
    finish_flag = False
    while not finish_flag:
        for player in player_names:
            # Only show boards to human players during their turn
            if game.is_human_player(player):
                print(f"\n=== {player}'s Turn ===")
                print("\nYour Firing Board:")
                game.display_firing_board(player)
                print("\nYour Ships:")
                game.display_placement_board(player)
            else:
                print(f"\n=== {player}'s Turn ===")

            # get fire location (human input or AI decision)
            game.get_fire_location(player)
            opponent_player = [k for k in player_names if k != player][0]
            
            # Fire!
            game.fire(player, opponent_player)

            # check left ships of the opponent player.
            game.players[opponent_player].get_left_ships()
            left_ships = game.players[opponent_player].left_ships

            # When there are no left ships game is end.
            if len(left_ships) == 0:
                print(f"\n🎉 {player} Won! Game was finished! 🎉")
                if game.is_human_player(player):
                    print("Congratulations!")
                else:
                    print("The computer beat you this time. Better luck next time!")
                finish_flag = True
                break

            # Show result to human player if it was computer's turn
            if not game.is_human_player(player) and game.is_human_player(opponent_player):
                print("\nPress Enter to continue...")
                input()
            
            # Appropriate sleep and clear based on player type
            if game.is_human_player(player):
                os.system('sleep 1.5')
                os.system('clear')
            else:
                os.system('sleep 2')


if __name__ == '__main__':
    main()
