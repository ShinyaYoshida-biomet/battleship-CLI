"""Main module for Battleship CLI with hexagonal architecture.

This module sets up the dependency injection and orchestrates the game flow
using the new hexagonal architecture.
"""
import argparse
import sys
import random
from typing import Dict, Tuple

from config import Config

# Domain imports
from src.domain.entities.player import PlayerType
from src.domain.entities.game_state import GamePhase
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation

# Application imports
from src.application.services.game_service import GameService
from src.application.use_cases.create_game_use_case import CreateGameUseCase, CreateGameRequest
from src.application.use_cases.place_ship_use_case import PlaceShipUseCase, PlaceShipRequest

# Infrastructure imports
from src.infrastructure.adapters.cli_ui_adapter import CLIUIAdapter
from src.infrastructure.adapters.in_memory_game_repository import InMemoryGameRepository
from src.infrastructure.adapters.console_notification_service import ConsoleNotificationService
from src.infrastructure.adapters.computer_ai_adapter import ComputerAIAdapter


class BattleshipGameOrchestrator:
    """Orchestrates the Battleship game using hexagonal architecture."""
    
    def __init__(self):
        # Infrastructure adapters
        self.ui = CLIUIAdapter()
        self.repository = InMemoryGameRepository()
        self.notifier = ConsoleNotificationService()
        
        # Application services
        self.game_service = GameService(self.repository, self.notifier)
        
        # Use cases
        self.create_game_use_case = CreateGameUseCase(self.repository, self.notifier)
        self.place_ship_use_case = PlaceShipUseCase(self.repository, self.notifier)
        
        # AI adapters (will be created per game)
        self.ai_adapters = {}
    
    def run_game(self, config: Config, mode: str, player1_name: str = None, player2_name: str = None):
        """Run the complete game flow."""
        try:
            # Show welcome screen
            self.ui.display_welcome_screen()
            
            # Determine game mode
            if mode == 'prompt':
                game_mode = self.ui.prompt_game_mode()
            else:
                game_mode = mode
            
            # Get player names
            if player1_name and (game_mode == 'pvc' or player2_name):
                if game_mode == 'pvc':
                    names = (player1_name, "Computer")
                else:
                    names = (player1_name, player2_name)
            else:
                names = self.ui.prompt_player_names(game_mode)
            
            player1_name, player2_name = names
            
            # Determine player types
            if game_mode == 'pvp':
                player_types = (PlayerType.HUMAN, PlayerType.HUMAN)
            else:
                player_types = (PlayerType.HUMAN, PlayerType.COMPUTER)
            
            # Show configuration
            self.ui.display_game_config((config.row_num, config.column_num), config.ship_dict)
            
            # Create game
            create_request = CreateGameRequest(
                player1_name=player1_name,
                player1_type=player_types[0],
                player2_name=player2_name,  
                player2_type=player_types[1],
                board_size=(config.row_num, config.column_num)
            )
            
            game_state = self.create_game_use_case.execute(create_request)
            
            # Initialize AI if needed
            for player in game_state.players:
                if player.is_computer():
                    self.ai_adapters[player.name] = ComputerAIAdapter(config.row_num, config.column_num)
            
            # Advance to ship placement phase
            game_state.advance_phase()
            
            # Ship placement phase
            self._ship_placement_phase(game_state, config.ship_dict)
            
            # Advance to battle phase
            game_state.advance_phase()
            
            # Battle phase
            self._battle_phase(game_state)
            
        except KeyboardInterrupt:
            self.ui.display_info("Game interrupted by user. Thanks for playing!")
            sys.exit(0)
        except Exception as e:
            self.ui.display_error(f"Game error: {e}")
            sys.exit(1)
    
    def _ship_placement_phase(self, game_state, ships_config: Dict[str, int]):
        """Handle ship placement for all players."""
        for player in game_state.players:
            self.ui.display_info(f"\\n=== {player.name}'s Ship Placement ===")
            
            if player.is_computer():
                # Computer placement
                self._place_computer_ships(game_state, player, ships_config)
            else:
                # Human placement
                placement_mode = self.ui.prompt_ship_placement_mode(player.name)
                if placement_mode == 'random':
                    self._place_random_ships(game_state, player, ships_config)
                else:
                    self._place_manual_ships(game_state, player, ships_config)
            
            self.ui.display_info(f"{player.name} has finished placing ships!")
    
    def _place_manual_ships(self, game_state, player, ships_config: Dict[str, int]):
        """Handle manual ship placement for human players."""
        ship_names = {
            'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
            'S': 'Submarine', 'P': 'Patrol boat'
        }
        
        for ship_symbol, ship_size in ships_config.items():
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            while True:
                try:
                    # Show current board
                    self.ui.display_placement_board(player)
                    
                    # Get placement from user
                    placement = self.ui.prompt_ship_placement(
                        player.name, ship_symbol, ship_size,
                        (player.placement_board.rows, player.placement_board.cols)
                    )
                    
                    # Try to place the ship
                    request = PlaceShipRequest(player, ship_symbol, ship_name, ship_size, placement)
                    self.place_ship_use_case.execute(game_state, request)
                    
                    self.ui.display_info(f"✅ {ship_name} placed successfully!")
                    break
                    
                except Exception as e:
                    self.ui.display_error(f"Cannot place {ship_name}: {e}")
                    continue
    
    def _place_random_ships(self, game_state, player, ships_config: Dict[str, int]):
        """Handle random ship placement."""
        ship_names = {
            'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
            'S': 'Submarine', 'P': 'Patrol boat'
        }
        
        for ship_symbol, ship_size in ships_config.items():
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            # Use AI adapter for random placement
            ai = ComputerAIAdapter(player.placement_board.rows, player.placement_board.cols)
            occupied_positions = self._get_occupied_positions(player)
            
            placement = ai.get_ship_placement(ship_size, player.placement_board, occupied_positions)
            
            request = PlaceShipRequest(player, ship_symbol, ship_name, ship_size, placement)
            self.place_ship_use_case.execute(game_state, request)
            
            self.ui.display_info(f"🎲 {ship_name} randomly placed")
    
    def _place_computer_ships(self, game_state, player, ships_config: Dict[str, int]):
        """Handle computer ship placement."""
        ship_names = {
            'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
            'S': 'Submarine', 'P': 'Patrol boat'
        }
        
        ai = self.ai_adapters[player.name]
        
        for ship_symbol, ship_size in ships_config.items():
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            occupied_positions = self._get_occupied_positions(player)
            placement = ai.get_ship_placement(ship_size, player.placement_board, occupied_positions)
            
            request = PlaceShipRequest(player, ship_symbol, ship_name, ship_size, placement)
            self.place_ship_use_case.execute(game_state, request)
    
    def _get_occupied_positions(self, player):
        """Get list of occupied positions on player's board."""
        occupied = []
        for row in range(player.placement_board.rows):
            for col in range(player.placement_board.cols):
                pos = Position(row, col)
                if player.placement_board.get_ship_at_position(pos):
                    occupied.append(pos)
        return occupied
    
    def _battle_phase(self, game_state):
        """Handle the main battle phase."""
        turn_counter = 0
        
        while not game_state.is_game_over():
            current_player = game_state.current_player
            opponent = game_state.get_opponent(current_player)
            turn_counter += 1
            
            # Show turn header
            self.ui.display_turn_header(current_player.name, turn_counter)
            
            # Show boards for human players
            if not current_player.is_computer():
                self.ui.display_boards_side_by_side(current_player, opponent)
            
            # Get fire location
            if current_player.is_computer():
                fire_pos = self._get_computer_fire_location(current_player, opponent)
            else:
                fire_pos = self._get_human_fire_location(current_player)
            
            # Fire the shot
            result = self.game_service.fire_shot(game_state, current_player, fire_pos)
            
            # Show fire result
            hit_ship = None
            if result.value == "hit":
                hit_ship = opponent.placement_board.get_ship_at_position(fire_pos)
            
            self.ui.display_fire_result(
                current_player.name, opponent.name, fire_pos, result,
                hit_ship.symbol if hit_ship else None
            )
            
            # Check for sunk ship
            if hit_ship and hit_ship.is_sunk():
                self.ui.display_ship_sunk(opponent.name, hit_ship)
            
            # Check win condition
            winner = self.game_service.check_game_over(game_state)
            if winner:
                self.ui.display_game_winner(winner, not winner.is_computer())
                break
            
            # Show updated boards after shot
            if not current_player.is_computer():
                import time
                time.sleep(1)
                self.ui.display_boards_side_by_side(current_player, opponent)
                time.sleep(2)
                self.ui.clear_screen()
            
            # Advance turn
            self.game_service.advance_turn(game_state)
    
    def _get_human_fire_location(self, player):
        """Get fire location from human player."""
        board_size = (player.firing_board.rows, player.firing_board.cols)
        
        while True:
            position = self.ui.prompt_fire_location(player.name, board_size)
            
            if player.can_fire_at_position(position):
                return position
            else:
                self.ui.display_error(f"Already fired at ({position.row}, {position.col}). Choose different coordinates.")
    
    def _get_computer_fire_location(self, player, opponent):
        """Get fire location from computer AI."""
        ai = self.ai_adapters[player.name]
        
        # Create firing history for AI
        firing_history = []
        for row in range(player.firing_board.rows):
            for col in range(player.firing_board.cols):
                pos = Position(row, col)
                cell_state = player.firing_board.get_cell_state(pos)
                if cell_state.value in ['hit', 'miss']:
                    firing_history.append((pos, cell_state.value))
        
        return ai.get_fire_location(opponent.placement_board, firing_history)


def get_version():
    """Get version from VERSION file."""
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return '1.0.0'


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Battleship CLI Game with Hexagonal Architecture',
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
    
    # Version information
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'Battleship CLI {get_version()}'
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
                sys.exit(1)
            ships_dict[name.upper()] = size
        except ValueError:
            print(f"Error: Invalid ship format '{ship_spec}'. Use NAME:SIZE (e.g., C:5)")
            sys.exit(1)
    
    return ships_dict


def validate_configuration(board_size: Tuple[int, int], ships_dict: Dict[str, int]) -> None:
    """Validate game configuration parameters."""
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
    """Main entry point for Battleship CLI."""
    try:
        args = parse_arguments()
        
        # Initialize configuration
        if args.config:
            # Use legacy config file
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
            
            config = Config(config_path=None, board_size=board_size, ships=ships_dict)
        
        # Create and run game
        orchestrator = BattleshipGameOrchestrator()
        orchestrator.run_game(config, args.mode, args.player1, args.player2)
        
    except KeyboardInterrupt:
        print("\\n\\nGame interrupted by user. Thanks for playing! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()