"""Tests for Player entity."""
import pytest
from src.domain.entities.player import Player, PlayerType
from src.domain.entities.board import Board, BoardType, CellState
from src.domain.entities.ship import Ship
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation


class TestPlayerType:
    """Test cases for PlayerType enum."""

    def test_player_type_values(self):
        """Test that PlayerType has correct values."""
        assert PlayerType.HUMAN.value == "human"
        assert PlayerType.COMPUTER.value == "computer"


class TestPlayer:
    """Test cases for Player entity."""

    def test_player_creation(self):
        """Test that Player can be created with valid parameters."""
        player = Player("John", PlayerType.HUMAN)
        
        assert player.name == "John"
        assert player.player_type == PlayerType.HUMAN
        assert player.placement_board is not None
        assert player.firing_board is not None
        assert isinstance(player.placement_board, Board)
        assert isinstance(player.firing_board, Board)
        assert player.placement_board.board_type == BoardType.PLACEMENT
        assert player.firing_board.board_type == BoardType.FIRING

    def test_player_with_custom_board_size(self):
        """Test that Player can be created with custom board size."""
        player = Player("Alice", PlayerType.COMPUTER, board_rows=8, board_cols=10)
        
        assert player.placement_board.rows == 8
        assert player.placement_board.cols == 10
        assert player.firing_board.rows == 8
        assert player.firing_board.cols == 10

    def test_player_place_ship(self):
        """Test placing a ship on player's board."""
        player = Player("Bob", PlayerType.HUMAN)
        
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("D", "Destroyer", 3, placement)
        
        player.place_ship(ship)
        
        # Verify ship is on placement board
        expected_positions = [Position(1, 2), Position(1, 3), Position(1, 4)]
        for pos in expected_positions:
            assert player.placement_board.get_cell_state(pos) == CellState.SHIP
            assert player.placement_board.get_ship_at_position(pos) == ship

    def test_player_record_incoming_shot(self):
        """Test recording incoming shots on player's board."""
        player = Player("Charlie", PlayerType.HUMAN)
        
        # Place a ship
        placement = ShipPlacement(Position(2, 3), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        player.place_ship(ship)
        
        # Record a hit
        hit_result = player.record_incoming_shot(Position(2, 3))
        assert hit_result == CellState.HIT
        assert player.placement_board.get_cell_state(Position(2, 3)) == CellState.HIT
        
        # Record a miss
        miss_result = player.record_incoming_shot(Position(0, 0))
        assert miss_result == CellState.MISS
        assert player.placement_board.get_cell_state(Position(0, 0)) == CellState.MISS

    def test_player_record_outgoing_shot(self):
        """Test recording outgoing shots on player's firing board."""
        player = Player("Diana", PlayerType.HUMAN)
        
        # Record shots
        player.record_outgoing_shot(Position(1, 2), CellState.HIT)
        player.record_outgoing_shot(Position(3, 4), CellState.MISS)
        
        assert player.firing_board.get_cell_state(Position(1, 2)) == CellState.HIT
        assert player.firing_board.get_cell_state(Position(3, 4)) == CellState.MISS

    def test_player_has_lost(self):
        """Test checking if player has lost (all ships sunk)."""
        player = Player("Eve", PlayerType.HUMAN)
        
        # Initially no ships, so technically "lost" (no ships to sink)
        assert player.has_lost()
        
        # Place a ship
        placement = ShipPlacement(Position(2, 3), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        player.place_ship(ship)
        
        # Now has ships, so not lost
        assert not player.has_lost()
        
        # Sink the ship
        player.record_incoming_shot(Position(2, 3))
        player.record_incoming_shot(Position(2, 4))
        
        # Now all ships sunk, so lost
        assert player.has_lost()

    def test_player_get_ships(self):
        """Test getting player's ships."""
        player = Player("Frank", PlayerType.HUMAN)
        
        assert len(player.get_ships()) == 0
        
        # Place ships
        placement1 = ShipPlacement(Position(1, 1), Orientation.HORIZONTAL)
        ship1 = Ship("D", "Destroyer", 3, placement1)
        player.place_ship(ship1)
        
        placement2 = ShipPlacement(Position(3, 2), Orientation.VERTICAL)
        ship2 = Ship("P", "Patrol", 2, placement2)
        player.place_ship(ship2)
        
        ships = player.get_ships()
        assert len(ships) == 2
        assert ship1 in ships
        assert ship2 in ships

    def test_player_get_active_ships(self):
        """Test getting player's active (non-sunk) ships."""
        player = Player("Grace", PlayerType.HUMAN)
        
        # Place two ships
        placement1 = ShipPlacement(Position(1, 1), Orientation.HORIZONTAL)
        ship1 = Ship("D", "Destroyer", 3, placement1)
        player.place_ship(ship1)
        
        placement2 = ShipPlacement(Position(3, 2), Orientation.VERTICAL)
        ship2 = Ship("P", "Patrol", 2, placement2)
        player.place_ship(ship2)
        
        # Initially both active
        active_ships = player.get_active_ships()
        assert len(active_ships) == 2
        assert ship1 in active_ships
        assert ship2 in active_ships
        
        # Sink one ship
        player.record_incoming_shot(Position(3, 2))
        player.record_incoming_shot(Position(4, 2))
        
        # Now only one active
        active_ships = player.get_active_ships()
        assert len(active_ships) == 1
        assert ship1 in active_ships
        assert ship2 not in active_ships

    def test_player_equality(self):
        """Test player equality based on ID."""
        player1 = Player("Henry", PlayerType.HUMAN)
        player2 = Player("Henry", PlayerType.HUMAN)  # Same name but different instance
        player3 = player1  # Same instance
        
        assert player1 != player2  # Different instances are not equal
        assert player1 == player3  # Same instance is equal
        assert player1.id != player2.id  # Different IDs

    def test_player_is_computer(self):
        """Test checking if player is computer."""
        human_player = Player("Isaac", PlayerType.HUMAN)
        computer_player = Player("Computer", PlayerType.COMPUTER)
        
        assert not human_player.is_computer()
        assert computer_player.is_computer()

    def test_player_can_fire_at_position(self):
        """Test checking if player can fire at a position."""
        player = Player("Julia", PlayerType.HUMAN)
        
        pos = Position(2, 3)
        
        # Initially can fire
        assert player.can_fire_at_position(pos)
        
        # After firing, cannot fire again
        player.record_outgoing_shot(pos, CellState.MISS)
        assert not player.can_fire_at_position(pos)