"""Tests for PlaceShipUseCase."""
import pytest
from unittest.mock import Mock

from src.application.use_cases.place_ship_use_case import PlaceShipUseCase, PlaceShipRequest
from src.domain.entities.game_state import GameState, GamePhase
from src.domain.entities.player import Player, PlayerType
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation
from src.ports.game_repository_port import GameRepositoryPort
from src.ports.notification_port import NotificationPort


class TestPlaceShipRequest:
    """Test cases for PlaceShipRequest."""

    def test_place_ship_request_creation(self):
        """Test that PlaceShipRequest can be created with valid parameters."""
        player = Player("Alice", PlayerType.HUMAN)
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        
        request = PlaceShipRequest(
            player=player,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement
        )
        
        assert request.player == player
        assert request.ship_symbol == "D"
        assert request.ship_name == "Destroyer"
        assert request.ship_size == 3
        assert request.placement == placement

    def test_place_ship_request_validation(self):
        """Test PlaceShipRequest validation."""
        player = Player("Alice", PlayerType.HUMAN)
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        
        # Empty ship symbol should raise error
        with pytest.raises(ValueError, match="Ship symbol cannot be empty"):
            PlaceShipRequest(player, "", "Destroyer", 3, placement)
        
        # Empty ship name should raise error
        with pytest.raises(ValueError, match="Ship name cannot be empty"):
            PlaceShipRequest(player, "D", "", 3, placement)
        
        # Invalid ship size should raise error
        with pytest.raises(ValueError, match="Ship size must be positive"):
            PlaceShipRequest(player, "D", "Destroyer", 0, placement)
        
        with pytest.raises(ValueError, match="Ship size must be positive"):
            PlaceShipRequest(player, "D", "Destroyer", -1, placement)


class TestPlaceShipUseCase:
    """Test cases for PlaceShipUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=GameRepositoryPort)
        self.mock_notifier = Mock(spec=NotificationPort)
        self.use_case = PlaceShipUseCase(self.mock_repository, self.mock_notifier)
        
        # Create test game state
        self.player1 = Player("Alice", PlayerType.HUMAN)
        self.player2 = Player("Bob", PlayerType.COMPUTER)
        self.game_state = GameState([self.player1, self.player2])

    def test_place_ship_success(self):
        """Test successful ship placement."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        request = PlaceShipRequest(
            player=self.player1,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement
        )
        
        ship = self.use_case.execute(self.game_state, request)
        
        # Verify ship properties
        assert ship.symbol == "D"
        assert ship.name == "Destroyer"
        assert ship.size == 3
        assert ship.placement == placement
        
        # Verify ship is on player's board
        expected_positions = [Position(1, 2), Position(1, 3), Position(1, 4)]
        for pos in expected_positions:
            assert self.player1.placement_board.get_ship_at_position(pos) == ship
        
        # Verify repository was called to save
        self.mock_repository.save_game.assert_called_once_with(self.game_state)
        
        # Verify notification was sent
        self.mock_notifier.notify_ship_placed.assert_called_once_with(self.player1, ship)

    def test_place_ship_out_of_bounds(self):
        """Test placing ship that goes out of bounds."""
        # Ship would go beyond right edge
        placement = ShipPlacement(Position(1, 6), Orientation.HORIZONTAL)  # 7x7 board, ship size 3 goes to col 8
        request = PlaceShipRequest(
            player=self.player1,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement
        )
        
        with pytest.raises(ValueError, match="Cannot place ship"):
            self.use_case.execute(self.game_state, request)
        
        # Should not save or notify on failure
        self.mock_repository.save_game.assert_not_called()
        self.mock_notifier.notify_ship_placed.assert_not_called()

    def test_place_ship_overlapping(self):
        """Test placing overlapping ships."""
        # Place first ship
        placement1 = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        request1 = PlaceShipRequest(
            player=self.player1,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement1
        )
        self.use_case.execute(self.game_state, request1)
        
        # Reset mocks
        self.mock_repository.reset_mock()
        self.mock_notifier.reset_mock()
        
        # Try to place overlapping ship
        placement2 = ShipPlacement(Position(1, 3), Orientation.HORIZONTAL)
        request2 = PlaceShipRequest(
            player=self.player1,
            ship_symbol="P",
            ship_name="Patrol",
            ship_size=2,
            placement=placement2
        )
        
        with pytest.raises(ValueError, match="Cannot place ship"):
            self.use_case.execute(self.game_state, request2)
        
        # Should not save or notify on failure
        self.mock_repository.save_game.assert_not_called()
        self.mock_notifier.notify_ship_placed.assert_not_called()

    def test_place_ship_vertical_orientation(self):
        """Test placing ship with vertical orientation."""
        placement = ShipPlacement(Position(2, 1), Orientation.VERTICAL)
        request = PlaceShipRequest(
            player=self.player1,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement
        )
        
        ship = self.use_case.execute(self.game_state, request)
        
        # Verify ship positions
        expected_positions = [Position(2, 1), Position(3, 1), Position(4, 1)]
        for pos in expected_positions:
            assert self.player1.placement_board.get_ship_at_position(pos) == ship

    def test_place_ship_repository_error(self):
        """Test ship placement when repository save fails."""
        from src.ports.game_repository_port import RepositoryError
        
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        request = PlaceShipRequest(
            player=self.player1,
            ship_symbol="D",
            ship_name="Destroyer",
            ship_size=3,
            placement=placement
        )
        
        # Mock repository to raise error
        self.mock_repository.save_game.side_effect = RepositoryError("Save failed")
        
        # Ship should still be placed, but save error should propagate
        with pytest.raises(RepositoryError):
            self.use_case.execute(self.game_state, request)
        
        # Verify ship was placed despite save error
        expected_positions = [Position(1, 2), Position(1, 3), Position(1, 4)]
        for pos in expected_positions:
            assert self.player1.placement_board.get_ship_at_position(pos) is not None
        
        # Notification should still be called
        self.mock_notifier.notify_ship_placed.assert_called_once()

    def test_place_ship_single_cell(self):
        """Test placing a single-cell ship."""
        placement = ShipPlacement(Position(3, 3), Orientation.HORIZONTAL)
        request = PlaceShipRequest(
            player=self.player1,
            ship_symbol="S",
            ship_name="Submarine",
            ship_size=1,
            placement=placement
        )
        
        ship = self.use_case.execute(self.game_state, request)
        
        # Verify ship is placed correctly
        assert self.player1.placement_board.get_ship_at_position(Position(3, 3)) == ship
        # Ensure no other positions are occupied by this ship
        assert self.player1.placement_board.get_ship_at_position(Position(3, 4)) is None