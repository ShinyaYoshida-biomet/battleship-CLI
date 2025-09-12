"""Main game service implementation."""
from typing import Dict, List, Optional, Any

from ...domain.entities.game_state import GameState
from ...domain.entities.player import Player, PlayerType
from ...domain.entities.ship import Ship
from ...domain.entities.board import CellState
from ...domain.value_objects.position import Position
from ...domain.value_objects.ship_placement import ShipPlacement
from ...ports.game_service_port import GameServicePort, GameError
from ...ports.game_repository_port import GameRepositoryPort
from ...ports.notification_port import NotificationPort


class GameService(GameServicePort):
    """Implementation of the game service port."""
    
    def __init__(self, repository: GameRepositoryPort, notifier: NotificationPort):
        self.repository = repository
        self.notifier = notifier
    
    def create_game(
        self, 
        player1_name: str, 
        player1_type: PlayerType,
        player2_name: str, 
        player2_type: PlayerType,
        board_size: tuple = (7, 7)
    ) -> GameState:
        """Create a new game."""
        rows, cols = board_size
        
        player1 = Player(player1_name, player1_type, rows, cols)
        player2 = Player(player2_name, player2_type, rows, cols)
        
        game_state = GameState([player1, player2])
        
        # Notify and save
        self.notifier.notify_game_started(player1, player2)
        self.repository.save_game(game_state)
        
        return game_state
    
    def place_ship(
        self, 
        game_state: GameState, 
        player: Player, 
        ship_symbol: str, 
        ship_name: str, 
        ship_size: int,
        placement: ShipPlacement
    ) -> None:
        """Place a ship on a player's board."""
        try:
            ship = Ship(ship_symbol, ship_name, ship_size, placement)
            player.place_ship(ship)
            
            # Notify and save
            self.notifier.notify_ship_placed(player, ship)
            self.repository.save_game(game_state)
            
        except Exception as e:
            raise GameError(f"Cannot place ship: {e}")
    
    def fire_shot(
        self, 
        game_state: GameState, 
        shooter: Player, 
        position: Position
    ) -> CellState:
        """Fire a shot at the opponent."""
        try:
            opponent = game_state.get_opponent(shooter)
            
            # Check if position is valid to fire at
            if not shooter.can_fire_at_position(position):
                raise GameError(f"Cannot fire at position {position} - already fired there")
            
            # Record the shot on opponent's board
            result = opponent.record_incoming_shot(position)
            
            # Record the shot on shooter's firing board
            shooter.record_outgoing_shot(position, result)
            
            # Notify about the shot
            self.notifier.notify_shot_fired(shooter, opponent, position, result)
            
            # Check if a ship was hit and if it's sunk
            if result == CellState.HIT:
                hit_ship = opponent.placement_board.get_ship_at_position(position)
                if hit_ship:
                    self.notifier.notify_ship_hit(opponent, hit_ship, position)
                    
                    if hit_ship.is_sunk():
                        self.notifier.notify_ship_sunk(opponent, hit_ship)
            
            # Save game state
            self.repository.save_game(game_state)
            
            return result
            
        except Exception as e:
            if isinstance(e, GameError):
                raise
            raise GameError(f"Cannot fire shot: {e}")
    
    def check_game_over(self, game_state: GameState) -> Optional[Player]:
        """Check if the game is over and return winner if any."""
        winner = game_state.check_win_condition()
        if winner:
            loser = game_state.get_opponent(winner)
            game_state.set_winner(winner)
            self.notifier.notify_game_over(winner, loser)
            self.repository.save_game(game_state)
        return winner
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID."""
        return self.repository.load_game(game_id)
    
    def save_game(self, game_state: GameState) -> None:
        """Save current game state."""
        try:
            self.repository.save_game(game_state)
        except Exception as e:
            raise GameError(f"Cannot save game: {e}")
    
    def advance_turn(self, game_state: GameState) -> None:
        """Advance to the next player's turn."""
        game_state.switch_turn()
        self.notifier.notify_turn_started(game_state.current_player, game_state.turn_number)
        self.repository.save_game(game_state)
    
    def get_valid_ship_placements(
        self, 
        player: Player, 
        ship_size: int
    ) -> List[ShipPlacement]:
        """Get all valid ship placements for a player."""
        from ...domain.value_objects.ship_placement import Orientation
        
        valid_placements = []
        
        for row in range(player.placement_board.rows):
            for col in range(player.placement_board.cols):
                for orientation in [Orientation.HORIZONTAL, Orientation.VERTICAL]:
                    placement = ShipPlacement(Position(row, col), orientation)
                    positions = placement.calculate_positions(ship_size)
                    
                    # Check if all positions are valid and not occupied
                    valid = True
                    for pos in positions:
                        if (not player.placement_board.is_valid_position(pos) or
                            player.placement_board.get_cell_state(pos) != CellState.WATER):
                            valid = False
                            break
                    
                    if valid:
                        valid_placements.append(placement)
        
        return valid_placements
    
    def get_valid_fire_positions(self, player: Player) -> List[Position]:
        """Get all valid firing positions for a player."""
        valid_positions = []
        
        for row in range(player.firing_board.rows):
            for col in range(player.firing_board.cols):
                position = Position(row, col)
                if player.can_fire_at_position(position):
                    valid_positions.append(position)
        
        return valid_positions
    
    def get_game_summary(self, game_state: GameState) -> Dict[str, Any]:
        """Get a summary of the current game state."""
        return game_state.get_game_summary()