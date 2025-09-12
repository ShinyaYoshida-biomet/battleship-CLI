"""Tests for CreateGameUseCase."""
import pytest
from unittest.mock import Mock

from src.application.use_cases.create_game_use_case import CreateGameUseCase, CreateGameRequest
from src.domain.entities.player import PlayerType
from src.domain.entities.game_state import GamePhase
from src.ports.game_repository_port import GameRepositoryPort
from src.ports.notification_port import NotificationPort


class TestCreateGameRequest:
    """Test cases for CreateGameRequest."""

    def test_create_game_request_creation(self):
        """Test that CreateGameRequest can be created with valid parameters."""
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Bob",
            player2_type=PlayerType.COMPUTER,
            board_size=(7, 10)
        )
        
        assert request.player1_name == "Alice"
        assert request.player1_type == PlayerType.HUMAN
        assert request.player2_name == "Bob"
        assert request.player2_type == PlayerType.COMPUTER
        assert request.board_size == (7, 10)

    def test_create_game_request_default_board_size(self):
        """Test that CreateGameRequest uses default board size."""
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Bob",
            player2_type=PlayerType.COMPUTER
        )
        
        assert request.board_size == (7, 7)

    def test_create_game_request_validation(self):
        """Test CreateGameRequest validation."""
        # Empty player names should raise error
        with pytest.raises(ValueError, match="Player names cannot be empty"):
            CreateGameRequest("", PlayerType.HUMAN, "Bob", PlayerType.COMPUTER)
        
        with pytest.raises(ValueError, match="Player names cannot be empty"):
            CreateGameRequest("Alice", PlayerType.HUMAN, "", PlayerType.COMPUTER)
        
        # Invalid board size should raise error
        with pytest.raises(ValueError, match="Board size must be at least 5x5"):
            CreateGameRequest("Alice", PlayerType.HUMAN, "Bob", PlayerType.COMPUTER, (4, 5))
        
        with pytest.raises(ValueError, match="Board size must be at least 5x5"):
            CreateGameRequest("Alice", PlayerType.HUMAN, "Bob", PlayerType.COMPUTER, (5, 3))


class TestCreateGameUseCase:
    """Test cases for CreateGameUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=GameRepositoryPort)
        self.mock_notifier = Mock(spec=NotificationPort)
        self.use_case = CreateGameUseCase(self.mock_repository, self.mock_notifier)

    def test_create_game_success(self):
        """Test successful game creation."""
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Computer",
            player2_type=PlayerType.COMPUTER,
            board_size=(8, 8)
        )
        
        game_state = self.use_case.execute(request)
        
        # Verify game state properties
        assert len(game_state.players) == 2
        assert game_state.players[0].name == "Alice"
        assert game_state.players[0].player_type == PlayerType.HUMAN
        assert game_state.players[1].name == "Computer"
        assert game_state.players[1].player_type == PlayerType.COMPUTER
        assert game_state.phase == GamePhase.SETUP
        assert game_state.current_player == game_state.players[0]
        assert game_state.winner is None
        
        # Verify board sizes
        assert game_state.players[0].placement_board.rows == 8
        assert game_state.players[0].placement_board.cols == 8
        assert game_state.players[1].placement_board.rows == 8
        assert game_state.players[1].placement_board.cols == 8
        
        # Verify repository was called to save the game
        self.mock_repository.save_game.assert_called_once_with(game_state)
        
        # Verify notification was sent
        self.mock_notifier.notify_game_started.assert_called_once_with(
            game_state.players[0], 
            game_state.players[1]
        )

    def test_create_game_pvp(self):
        """Test creating Player vs Player game."""
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Bob",
            player2_type=PlayerType.HUMAN
        )
        
        game_state = self.use_case.execute(request)
        
        assert game_state.players[0].player_type == PlayerType.HUMAN
        assert game_state.players[1].player_type == PlayerType.HUMAN

    def test_create_game_repository_error(self):
        """Test game creation when repository save fails."""
        from src.ports.game_repository_port import RepositoryError
        
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Computer",
            player2_type=PlayerType.COMPUTER
        )
        
        # Mock repository to raise error
        self.mock_repository.save_game.side_effect = RepositoryError("Save failed")
        
        with pytest.raises(RepositoryError):
            self.use_case.execute(request)
        
        # Notification should still be called
        self.mock_notifier.notify_game_started.assert_called_once()

    def test_create_game_default_board_size(self):
        """Test game creation with default board size."""
        request = CreateGameRequest(
            player1_name="Alice",
            player1_type=PlayerType.HUMAN,
            player2_name="Computer",
            player2_type=PlayerType.COMPUTER
        )
        
        game_state = self.use_case.execute(request)
        
        # Should use default 7x7 board
        assert game_state.players[0].placement_board.rows == 7
        assert game_state.players[0].placement_board.cols == 7