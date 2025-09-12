# -*- coding: utf-8 -*-
"""Main module to execute battleship game in CLI.
You can start the game by typing a command below in your command line.

Example:
    python main.py
    
"""
import argparse
import os
import sys
from typing import Dict, Tuple

from config import Config
from game import Game


def parse_arguments():
    """Parse command line arguments for battleship game configuration.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Battleship CLI Game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                              # Default 10x10 board, standard ships, prompt for mode
  %(prog)s --mode pvp                   # Player vs Player mode
  %(prog)s --mode pvc                   # Player vs Computer mode
  %(prog)s --board-size 8 8             # Custom 8x8 board
  %(prog)s --ships C:5 B:4 D:3          # Custom ships (Carrier:5, Battleship:4, Destroyer:3)
  %(prog)s --config config_files/battleship_config.txt  # Use config file

Ship Types (default):
  B - Battleship (4 cells)
  D - Destroyer (3 cells)
  P - Patrol boat (2 cells)
        '''
    )
    
    # Game mode selection
    parser.add_argument(
        '--mode', '-m',
        choices=['pvp', 'pvc', 'prompt'],
        default='prompt',
        help='Game mode: pvp (Player vs Player), pvc (Player vs Computer), or prompt (ask user)'
    )
    
    # Board configuration
    parser.add_argument(
        '--board-size', '-b',
        nargs=2,
        type=int,
        metavar=('ROWS', 'COLS'),
        default=(10, 10),
        help='Board dimensions (default: 10 10)'
    )
    
    # Ship configuration
    parser.add_argument(
        '--ships', '-s',
        nargs='*',
        metavar='NAME:SIZE',
        help='Ships in format NAME:SIZE (e.g., C:5 B:4 D:3). Default: B:4 D:3 P:2'
    )
    
    # Legacy config file support
    parser.add_argument(
        '--config', '-c',
        type=str,
        metavar='PATH',
        help='Path to configuration file (overrides other settings)'
    )
    
    # Player names
    parser.add_argument(
        '--player1', '-p1',
        type=str,
        help='Name for player 1 (will prompt if not provided)'
    )
    
    parser.add_argument(
        '--player2', '-p2',
        type=str,
        help='Name for player 2 (will prompt if not provided and in PvP mode)'
    )
    
    return parser.parse_args()

def parse_ships(ships_list) -> Dict[str, int]:
    """Parse ships from command line format.
    
    Args:
        ships_list: List of strings in format 'NAME:SIZE'
        
    Returns:
        Dict[str, int]: Ship name to size mapping
    """
    if not ships_list:
        # Default ships - simplified for faster gameplay
        return {
            'B': 4,  # Battleship
            'D': 3,  # Destroyer  
            'P': 2   # Patrol boat
        }
    
    ships_dict = {}
    for ship_spec in ships_list:
        try:
            name, size_str = ship_spec.split(':')
            size = int(size_str)
            if size <= 0:
                print(f"Error: Ship size must be positive, got {size} for {name}")
                sys.exit(1)
            ships_dict[name.upper()] = size
        except ValueError:
            print(f"Error: Invalid ship format '{ship_spec}'. Use NAME:SIZE (e.g., C:5)")
            sys.exit(1)
    
    return ships_dict

def validate_configuration(board_size: Tuple[int, int], ships_dict: Dict[str, int]) -> None:
    """Validate game configuration parameters.
    
    Args:
        board_size: Tuple of (rows, cols)
        ships_dict: Dictionary of ship names to sizes
        
    Raises:
        SystemExit: If configuration is invalid
    """
    rows, cols = board_size
    
    # Validate board size
    if rows < 5 or cols < 5:
        print("Error: Board size must be at least 5x5")
        sys.exit(1)
    if rows > 26 or cols > 26:
        print("Error: Board size cannot exceed 26x26")
        sys.exit(1)
    
    # Validate ships
    if not ships_dict:
        print("Error: At least one ship must be specified")
        sys.exit(1)
    
    total_ship_cells = sum(ships_dict.values())
    total_board_cells = rows * cols
    
    if total_ship_cells > total_board_cells * 0.5:
        print(f"Error: Ships require {total_ship_cells} cells, but board only has {total_board_cells} cells.")
        print("Ships cannot occupy more than 50% of the board.")
        sys.exit(1)
    
    # Check if largest ship can fit
    max_ship_size = max(ships_dict.values())
    if max_ship_size > min(rows, cols):
        print(f"Error: Largest ship size ({max_ship_size}) cannot fit on {rows}x{cols} board")
        sys.exit(1)
    
    # Validate ship names (should be single characters for display)
    for ship_name in ships_dict.keys():
        if len(ship_name) != 1 or not ship_name.isalnum():
            print(f"Error: Ship name '{ship_name}' must be a single alphanumeric character")
            sys.exit(1)


def main():
    """Main module to execute battleship game in CLI.

    Uses command line arguments for configuration or prompts user for missing information.
    """
    args = parse_arguments()
    
    print("🚢 Battle Ship Game Has Started! 🚢")
    try:
        with open('images/ship_ascii', 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print("⚓ Welcome to Battleship! ⚓")
        
    # Determine game mode
    if args.mode == 'prompt':
        print("\nGame Modes:")
        print("1. Player vs Player")
        print("2. Player vs Computer")
        
        game_mode = ''
        while game_mode not in ['1', '2']:
            game_mode = input('Please select game mode (1 or 2): ').strip()
        
        game_mode = 'pvp' if game_mode == '1' else 'pvc'
    else:
        game_mode = args.mode
    
    # Initialize configuration
    if args.config:
        # Use legacy config file
        print(f"\nUsing configuration file: {args.config}")
        try:
            config = Config(args.config)
        except FileNotFoundError:
            print(f"Error: Configuration file '{args.config}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            sys.exit(1)
    else:
        # Use CLI configuration
        ships_dict = parse_ships(args.ships)
        board_size = tuple(args.board_size)
        
        # Validate configuration
        validate_configuration(board_size, ships_dict)
        
        print(f"\nGame Configuration:")
        print(f"Board Size: {board_size[0]} x {board_size[1]}")
        print(f"Ships: {', '.join([f'{name}({size})' for name, size in ships_dict.items()])}")
        
        config = Config(config_path=None, board_size=board_size, ships=ships_dict)
    
    # Determine player names and types
    if game_mode == 'pvp':
        # Player vs Player mode
        player1_name = args.player1 or input('Player 1, please enter your name: ')
        player2_name = args.player2 or input('Player 2, please enter your name: ')
        player_names = [player1_name, player2_name]
        player_types = ['human', 'human']
        print(f"\n{player1_name} vs {player2_name} - Let the battle begin!")
    else:
        # Player vs Computer mode
        player1_name = args.player1 or input('Player, please enter your name: ')
        player2_name = 'Computer'
        player_names = [player1_name, player2_name]
        player_types = ['human', 'computer']
        print(f"\n{player1_name} vs {player2_name} - Good luck!")

    # Initialize game instance with config and player information
    game = Game(config, player_names, player_types)
    # Display game rules
    print("\n📋 Game Rules:")
    print(f"Board: {game.config.row_num}x{game.config.column_num}")
    print("Ships to place:")
    for ship_name, ship_size in game.config.ship_dict.items():
        print(f"  {ship_name}: {ship_size} cells")
    print("\nObjective: Sink all enemy ships by guessing their locations!")
    print("Legend: 'O' = Hit, 'X' = Miss, Ship symbols = Your ships\n")
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