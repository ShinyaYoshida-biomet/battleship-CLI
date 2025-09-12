"""Tests for Ship entity."""
import pytest
from src.domain.entities.ship import Ship
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation


class TestShip:
    """Test cases for Ship entity."""

    def test_ship_creation(self):
        """Test that Ship can be created with valid parameters."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("B", "Battleship", 4, placement)
        
        assert ship.symbol == "B"
        assert ship.name == "Battleship"
        assert ship.size == 4
        assert ship.placement == placement
        assert not ship.is_sunk()

    def test_ship_positions(self):
        """Test that Ship correctly calculates its positions."""
        # Horizontal ship
        placement = ShipPlacement(Position(2, 1), Orientation.HORIZONTAL)
        ship = Ship("D", "Destroyer", 3, placement)
        
        expected_positions = [Position(2, 1), Position(2, 2), Position(2, 3)]
        assert ship.get_positions() == expected_positions
        
        # Vertical ship
        placement = ShipPlacement(Position(1, 2), Orientation.VERTICAL)
        ship = Ship("D", "Destroyer", 3, placement)
        
        expected_positions = [Position(1, 2), Position(2, 2), Position(3, 2)]
        assert ship.get_positions() == expected_positions

    def test_ship_hit(self):
        """Test ship hit functionality."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        
        # Initial state
        assert len(ship.hits) == 0
        assert not ship.is_sunk()
        
        # Hit the ship
        hit_pos = Position(1, 2)
        ship.hit(hit_pos)
        
        assert hit_pos in ship.hits
        assert not ship.is_sunk()  # Still alive with 1 hit out of 2
        
        # Hit the ship again to sink it
        hit_pos2 = Position(1, 3)
        ship.hit(hit_pos2)
        
        assert hit_pos2 in ship.hits
        assert ship.is_sunk()  # Now sunk

    def test_ship_hit_invalid_position(self):
        """Test that hitting invalid position raises error."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        
        invalid_pos = Position(0, 0)  # Not part of the ship
        with pytest.raises(ValueError, match="Position .* is not part of this ship"):
            ship.hit(invalid_pos)

    def test_ship_occupies_position(self):
        """Test checking if ship occupies a position."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        
        assert ship.occupies_position(Position(1, 2))
        assert ship.occupies_position(Position(1, 3))
        assert not ship.occupies_position(Position(0, 2))
        assert not ship.occupies_position(Position(1, 4))

    def test_ship_is_hit_at_position(self):
        """Test checking if ship is hit at specific position."""
        placement = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        ship = Ship("P", "Patrol", 2, placement)
        
        pos = Position(1, 2)
        assert not ship.is_hit_at_position(pos)
        
        ship.hit(pos)
        assert ship.is_hit_at_position(pos)
        assert not ship.is_hit_at_position(Position(1, 3))

    def test_ship_equality(self):
        """Test ship equality based on id."""
        placement1 = ShipPlacement(Position(1, 2), Orientation.HORIZONTAL)
        placement2 = ShipPlacement(Position(3, 4), Orientation.VERTICAL)
        
        ship1 = Ship("B", "Battleship", 4, placement1)
        ship2 = Ship("B", "Battleship", 4, placement1)  # Same properties but different instance
        ship3 = ship1  # Same instance
        
        assert ship1 != ship2  # Different instances are not equal
        assert ship1 == ship3  # Same instance is equal
        assert ship1.id != ship2.id  # Different IDs