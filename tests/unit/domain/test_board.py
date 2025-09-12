"""Tests for Board entity."""
import pytest
from src.domain.entities.board import Board, CellState, BoardType
from src.domain.entities.ship import Ship
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation


class TestCellState:
    """Test cases for CellState enum."""

    def test_cell_state_values(self):
        """Test that CellState has correct values."""
        assert CellState.WATER.value == "water"
        assert CellState.SHIP.value == "ship"
        assert CellState.HIT.value == "hit"
        assert CellState.MISS.value == "miss"


class TestBoardType:
    """Test cases for BoardType enum."""

    def test_board_type_values(self):
        """Test that BoardType has correct values."""
        assert BoardType.PLACEMENT.value == "placement"
        assert BoardType.FIRING.value == "firing"


class TestBoard:
    """Test cases for Board entity."""

    def test_board_creation(self):
        """Test that Board can be created with valid parameters."""
        board = Board(7, 10, BoardType.PLACEMENT)
        
        assert board.rows == 7
        assert board.cols == 10
        assert board.board_type == BoardType.PLACEMENT
        
        # Check that all cells are initially water
        for row in range(7):
            for col in range(10):
                assert board.get_cell_state(Position(row, col)) == CellState.WATER

    def test_board_invalid_size(self):
        """Test that invalid board sizes raise errors."""
        with pytest.raises(ValueError, match="Board dimensions must be positive"):
            Board(0, 5, BoardType.PLACEMENT)
        with pytest.raises(ValueError, match="Board dimensions must be positive"):
            Board(5, -1, BoardType.FIRING)

    def test_board_position_validation(self):
        """Test position validation for board operations."""
        board = Board(5, 5, BoardType.PLACEMENT)
        
        # Valid positions
        assert board.is_valid_position(Position(0, 0))
        assert board.is_valid_position(Position(4, 4))
        
        # Invalid positions (out of bounds)
        assert not board.is_valid_position(Position(5, 0))
        assert not board.is_valid_position(Position(0, 5))
        assert not board.is_valid_position(Position(10, 10))

    def test_board_place_ship(self):
        """Test placing ships on the board."""
        board = Board(7, 7, BoardType.PLACEMENT)
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("D", "Destroyer", 3, placement)
        
        # Place the ship
        board.place_ship(ship)
        
        # Check that ship positions are marked correctly
        expected_positions = [Position(1, 2), Position(1, 3), Position(1, 4)]
        for pos in expected_positions:
            assert board.get_cell_state(pos) == CellState.SHIP
            assert board.get_ship_at_position(pos) == ship
            
        # Check that other positions are still water
        assert board.get_cell_state(Position(1, 1)) == CellState.WATER
        assert board.get_cell_state(Position(1, 5)) == CellState.WATER

    def test_board_place_overlapping_ship(self):
        """Test that placing overlapping ships raises error."""
        board = Board(7, 7, BoardType.PLACEMENT)
        
        placement1 = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship1 = Ship("D", "Destroyer", 3, placement1)
        board.place_ship(ship1)
        
        # Try to place overlapping ship
        placement2 = ShipPlacement(Position(1, 3), Orientation.HORIZONTAL)
        ship2 = Ship("P", "Patrol", 2, placement2)
        
        with pytest.raises(ValueError, match="Cannot place ship - position .* is already occupied"):
            board.place_ship(ship2)

    def test_board_place_ship_out_of_bounds(self):
        """Test that placing ship out of bounds raises error."""
        board = Board(5, 5, BoardType.PLACEMENT)
        
        # Ship goes beyond right edge
        placement = ShipPlacement(Position(1, 3), Orientation.HORIZONTAL)
        ship = Ship("D", "Destroyer", 3, placement)  # Would go to columns 3, 4, 5 (5 is out of bounds)
        
        with pytest.raises(ValueError, match="Cannot place ship - position .* is out of bounds"):
            board.place_ship(ship)

    def test_board_record_shot_hit(self):
        """Test recording a hit shot."""
        board = Board(7, 7, BoardType.PLACEMENT)
        placement = ShipPlacement(Position(2, 3), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        board.place_ship(ship)
        
        # Record a hit
        hit_pos = Position(2, 3)
        result = board.record_shot(hit_pos)
        
        assert result == CellState.HIT
        assert board.get_cell_state(hit_pos) == CellState.HIT
        assert ship.is_hit_at_position(hit_pos)

    def test_board_record_shot_miss(self):
        """Test recording a miss shot."""
        board = Board(7, 7, BoardType.PLACEMENT)
        
        # Record a miss
        miss_pos = Position(2, 3)
        result = board.record_shot(miss_pos)
        
        assert result == CellState.MISS
        assert board.get_cell_state(miss_pos) == CellState.MISS

    def test_board_record_shot_invalid_position(self):
        """Test that shooting invalid position raises error."""
        board = Board(5, 5, BoardType.PLACEMENT)
        
        invalid_pos = Position(10, 10)
        with pytest.raises(ValueError, match="Position .* is out of bounds"):
            board.record_shot(invalid_pos)

    def test_board_record_shot_already_fired(self):
        """Test that shooting same position twice raises error."""
        board = Board(7, 7, BoardType.PLACEMENT)
        
        pos = Position(2, 3)
        board.record_shot(pos)  # First shot
        
        with pytest.raises(ValueError, match="Position .* has already been fired upon"):
            board.record_shot(pos)  # Second shot

    def test_board_all_ships_sunk(self):
        """Test checking if all ships are sunk."""
        board = Board(7, 7, BoardType.PLACEMENT)
        
        # Initially no ships
        assert board.all_ships_sunk()
        
        # Add a ship
        placement = ShipPlacement(Position(2, 3), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        board.place_ship(ship)
        
        # Ship not sunk yet
        assert not board.all_ships_sunk()
        
        # Hit the ship partially
        board.record_shot(Position(2, 3))
        assert not board.all_ships_sunk()
        
        # Sink the ship completely
        board.record_shot(Position(2, 4))
        assert board.all_ships_sunk()

    def test_board_get_ships(self):
        """Test getting all ships on the board."""
        board = Board(7, 7, BoardType.PLACEMENT)
        
        assert len(board.get_ships()) == 0
        
        placement1 = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship1 = Ship("D", "Destroyer", 3, placement1)
        board.place_ship(ship1)
        
        placement2 = ShipPlacement(Position(3, 1), Orientation.VERTICAL)
        ship2 = Ship("P", "Patrol", 2, placement2)
        board.place_ship(ship2)
        
        ships = board.get_ships()
        assert len(ships) == 2
        assert ship1 in ships
        assert ship2 in ships