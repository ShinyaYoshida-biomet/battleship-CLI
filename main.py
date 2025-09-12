# -*- coding: utf-8 -*-
"""Main module to execute battleship game in CLI.
You can start the game by typing a command below in your command line.

Example:
    python main.py
    
"""
import argparse
import os
import sys
import time
from typing import Dict, Tuple

from config import Config
from game import Game
from ui import ui


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
  %(prog)s                              # Default 7x7 board, standard ships, prompt for mode
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
        default=(7, 7),
        help='Board dimensions (default: 7 7)'
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
    try:
        args = parse_arguments()
        
        # Show welcome screen with Rich UI
        ui.show_welcome_screen()
            
        # Determine game mode
        if args.mode == 'prompt':
            game_mode = ui.prompt_game_mode()
        else:
            game_mode = args.mode
        
        # Initialize configuration
        if args.config:
            # Use legacy config file
            ui.console.print(f"\n[blue]Using configuration file: {args.config}[/blue]")
            try:
                config = Config(args.config)
            except FileNotFoundError:
                ui.console.print(f"[red]Error: Configuration file '{args.config}' not found.[/red]")
                sys.exit(1)
            except Exception as e:
                ui.console.print(f"[red]Error reading configuration file: {e}[/red]")
                sys.exit(1)
        else:
            # Use CLI configuration
            ships_dict = parse_ships(args.ships)
            board_size = tuple(args.board_size)
            
            # Validate configuration
            validate_configuration(board_size, ships_dict)
            
            # Show configuration with Rich UI
            ui.show_game_config(board_size, ships_dict)
            
            config = Config(config_path=None, board_size=board_size, ships=ships_dict)
        
        # Determine player names and types
        if game_mode == 'pvp':
            # Player vs Player mode
            if args.player1 and args.player2:
                player1_name, player2_name = args.player1, args.player2
            else:
                player1_name, player2_name = ui.prompt_player_names('pvp')
            player_names = [player1_name, player2_name]
            player_types = ['human', 'human']
        else:
            # Player vs Computer mode
            if args.player1:
                player1_name, player2_name = args.player1, 'Computer'
            else:
                player1_name, player2_name = ui.prompt_player_names('pvc')
            player_names = [player1_name, player2_name]
            player_types = ['human', 'computer']
        
        # Announce the matchup with Rich UI
        ui.announce_vs(player1_name, player2_name)

        # Initialize game instance with config and player information
        game = Game(config, player_names, player_types)
        
        # Display game rules with Rich UI
        ui.show_game_rules(game.config.ship_dict)
        
        game.set_players()
        
        # Ask human players for ship placement mode
        game.set_ship_placement_modes()

        # Player1 and Player2 initialize their battleship locations
        for player in player_names:
            # Only show board to human players
            if game.is_human_player(player):
                ui.console.print(f"\n[bold blue]=== {player}'s Ship Placement ===[/bold blue]")
                game.display_placement_board(player)
            else:
                ui.console.print(f"\n[bold green]=== {player} is placing ships ===[/bold green]")
                
            # Initialize battleship location
            for ship_symbol, ship_size in game.config.ship_dict.items():
                # set a battleship based on the information
                game.set_ships(player, ship_symbol, ship_size)

                # Only show updated board to human players
                if game.is_human_player(player):
                    game.display_placement_board(player)

            # clear console for good appearance
            if game.is_human_player(player):
                ui.console.print("\n[green]Ship placement complete! Get ready for battle...[/green]")
                time.sleep(0.5)  # Brief pause
                ui.clear_screen()
            else:
                ui.console.print(f"[blue]{player} has finished placing ships![/blue]")
                time.sleep(0.3)

        # Fire part - main game loop
        finish_flag = False
        turn_counter = 0
        
        while not finish_flag:
            for player in player_names:
                turn_counter += 1
                
                # Show turn header with Rich UI
                ui.show_turn_header(player, turn_counter)
                
                # Show boards to human players during their turn
                if game.is_human_player(player):
                    game.display_boards_side_by_side(player)
                else:
                    ui.console.print(f"\n[bold blue]{player} is analyzing the battlefield...[/bold blue]")

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
                    ui.show_game_winner(player, game.is_human_player(player))
                    finish_flag = True
                    break

                # Show result to human player if it was computer's turn  
                if not game.is_human_player(player) and game.is_human_player(opponent_player):
                    time.sleep(0.5)  # Brief pause
                
                # Appropriate pause based on player type
                if game.is_human_player(player):
                    time.sleep(0.3)
                    ui.clear_screen()
                else:
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        ui.console.print("\n\n[bold red]🛑 Game interrupted by user[/bold red]")
        ui.console.print("[yellow]Thanks for playing Battleship CLI! 👋[/yellow]")
        sys.exit(0)


if __name__ == '__main__':
    main()