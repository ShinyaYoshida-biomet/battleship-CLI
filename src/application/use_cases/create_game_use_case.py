"""Create game use case."""
from dataclasses import dataclass
from typing import Tuple

from ...domain.entities.game_state import GameState
from ...domain.entities.player import Player, PlayerType
from ...ports.game_repository_port import GameRepositoryPort
from ...ports.notification_port import NotificationPort


@dataclass
class CreateGameRequest:
    """Request object for creating a new game."""
    player1_name: str
    player1_type: PlayerType
    player2_name: str
    player2_type: PlayerType
    board_size: Tuple[int, int] = (7, 7)
    
    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.player1_name.strip() or not self.player2_name.strip():
            raise ValueError("Player names cannot be empty")
        
        rows, cols = self.board_size
        if rows < 5 or cols < 5:
            raise ValueError("Board size must be at least 5x5")


class CreateGameUseCase:
    """Use case for creating a new battleship game.
    
    This use case handles the initialization of a new game, including:
    - Creating players with their boards
    - Setting up initial game state
    - Saving the game to the repository
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
    
    def execute(self, request: CreateGameRequest) -> GameState:
        """Execute the create game use case.
        
        Args:
            request: Request containing game creation parameters
            
        Returns:
            Created GameState
            
        Raises:
            RepositoryError: If saving the game fails
        """
        # Create players with specified board size
        rows, cols = request.board_size
        
        player1 = Player(
            name=request.player1_name,
            player_type=request.player1_type,
            board_rows=rows,
            board_cols=cols
        )
        
        player2 = Player(
            name=request.player2_name,
            player_type=request.player2_type,
            board_rows=rows,
            board_cols=cols
        )
        
        # Create game state
        game_state = GameState([player1, player2])
        
        # Send notification first (should always happen)
        self.notifier.notify_game_started(player1, player2)
        
        # Save the game (may fail, but game is still created)
        self.repository.save_game(game_state)
        
        return game_state