# -*- coding: utf-8 -*-
"""
Hexagonal Architecture entry point for Battleship CLI.
Demonstrates clean separation of concerns and Web-ready structure.
"""

import asyncio
import argparse
from typing import Dict, Tuple

from application.game_service import GameService
from adapters.cli_adapter import CLIAdapter
from adapters.ai_adapter import AIFactory


def parse_arguments():
    """Parse command line arguments for battleship game configuration."""
    parser = argparse.ArgumentParser(
        description='Battleship CLI Game (Hexagonal Architecture)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                              # Default 7x7 board, standard ships, CLI interface
  %(prog)s --board-size 8 8             # Custom 8x8 board
  %(prog)s --ships C:5 B:4 D:3          # Custom ships (Carrier:5, Battleship:4, Destroyer:3)

Ship Types (default):
  B - Battleship (4 cells)
  D - Destroyer (3 cells)
  P - Patrol boat (2 cells)

Architecture:
  This version uses Hexagonal Architecture for clean separation of UI and business logic.
  The same core game logic can be adapted for Web, API, or other interfaces.
        '''
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
    
    return parser.parse_args()


def parse_ships(ships_list) -> Dict[str, int]:
    """Parse ships from command line format."""
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
                exit(1)
            ships_dict[name.upper()] = size
        except ValueError:
            print(f"Error: Invalid ship format '{ship_spec}'. Use NAME:SIZE (e.g., C:5)")
            exit(1)
    
    return ships_dict


def validate_configuration(board_size: Tuple[int, int], ships_dict: Dict[str, int]) -> None:
    """Validate game configuration parameters."""
    rows, cols = board_size
    
    # Validate board size
    if rows < 5 or cols < 5:
        print("Error: Board size must be at least 5x5")
        exit(1)
    if rows > 26 or cols > 26:
        print("Error: Board size cannot exceed 26x26")
        exit(1)
    
    # Validate ships
    if not ships_dict:
        print("Error: At least one ship must be specified")
        exit(1)
    
    total_ship_cells = sum(ships_dict.values())
    total_board_cells = rows * cols
    
    if total_ship_cells > total_board_cells * 0.5:
        print(f"Error: Ships require {total_ship_cells} cells, but board only has {total_board_cells} cells.")
        print("Ships cannot occupy more than 50% of the board.")
        exit(1)
    
    # Check if largest ship can fit
    max_ship_size = max(ships_dict.values())
    if max_ship_size > min(rows, cols):
        print(f"Error: Largest ship size ({max_ship_size}) cannot fit on {rows}x{cols} board")
        exit(1)
    
    # Validate ship names (should be single characters for display)
    for ship_name in ships_dict.keys():
        if len(ship_name) != 1 or not ship_name.isalnum():
            print(f"Error: Ship name '{ship_name}' must be a single alphanumeric character")
            exit(1)


async def main():
    """Main function using Hexagonal Architecture."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Parse and validate configuration
    board_size = tuple(args.board_size)
    ships_dict = parse_ships(args.ships)
    validate_configuration(board_size, ships_dict)
    
    # Create CLI adapter (implements both input and output ports)
    cli_adapter = CLIAdapter()
    
    # Create AI adapter for computer opponents
    ai_adapter = AIFactory.create_ai('standard', board_size)
    
    # Create game service with CLI and AI adapters
    game_service = GameService(
        input_port=cli_adapter,
        output_port=cli_adapter,
        ai_port=ai_adapter
    )
    
    try:
        # Execute game phases
        print("🎮 Starting Battleship Game (Hexagonal Architecture)")
        print("=" * 60)
        
        # Initialize game
        result = await game_service.start_new_game(board_size, ships_dict)
        if not result.success:
            print(f"Error initializing game: {result.message}")
            return
        
        # Ship placement phase
        result = await game_service.execute_ship_placement_phase()
        if not result.success:
            print(f"Error during ship placement: {result.message}")
            return
        
        # Battle phase
        result = await game_service.execute_battle_phase()
        if not result.success:
            print(f"Error during battle: {result.message}")
            return
        
        print("\n🎉 Game completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted by user. Thanks for playing!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())