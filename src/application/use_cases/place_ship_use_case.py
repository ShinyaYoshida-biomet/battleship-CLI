"""Place ship use case."""
from dataclasses import dataclass

from ...domain.entities.game_state import GameState
from ...domain.entities.player import Player
from ...domain.entities.ship import Ship
from ...domain.value_objects.ship_placement import ShipPlacement
from ...ports.game_repository_port import GameRepositoryPort
from ...ports.notification_port import NotificationPort


@dataclass
class PlaceShipRequest:
    """Request object for placing a ship."""
    player: Player
    ship_symbol: str
    ship_name: str
    ship_size: int
    placement: ShipPlacement
    
    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.ship_symbol.strip():
            raise ValueError("Ship symbol cannot be empty")
        
        if not self.ship_name.strip():
            raise ValueError("Ship name cannot be empty")
        
        if self.ship_size <= 0:
            raise ValueError("Ship size must be positive")


class PlaceShipUseCase:
    """Use case for placing a ship on a player's board.
    
    This use case handles:
    - Creating a ship entity
    - Validating ship placement
    - Placing the ship on the player's board
    - Saving the updated game state
    - Sending notifications
    """
    
    def __init__(self, repository: GameRepositoryPort, notifier: NotificationPort):
        """Initialize the use case with required dependencies.
        
        Args:
            repository: Repository for saving game state
            notifier: Service for sending notifications
        """
        self.repository = repository
        self.notifier = notifier
    
    def execute(self, game_state: GameState, request: PlaceShipRequest) -> Ship:
        """Execute the place ship use case.
        
        Args:
            game_state: Current game state
            request: Request containing ship placement parameters
            
        Returns:
            The created and placed Ship
            
        Raises:
            ValueError: If ship cannot be placed
            RepositoryError: If saving the game fails
        """
        # Create the ship
        ship = Ship(
            symbol=request.ship_symbol,
            name=request.ship_name,
            size=request.ship_size,
            placement=request.placement
        )
        
        # Place the ship on the player's board
        # This will raise ValueError if placement is invalid
        request.player.place_ship(ship)
        
        # Send notification
        self.notifier.notify_ship_placed(request.player, ship)
        
        # Save the updated game state
        self.repository.save_game(game_state)
        
        return ship