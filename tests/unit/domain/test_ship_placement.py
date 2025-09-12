"""Tests for ShipPlacement value object."""
import pytest
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation


class TestOrientation:
    """Test cases for Orientation enum."""

    def test_orientation_values(self):
        """Test that Orientation has correct values."""
        assert Orientation.HORIZONTAL.value == "horizontal"
        assert Orientation.VERTICAL.value == "vertical"


class TestShipPlacement:
    """Test cases for ShipPlacement value object."""

    def test_ship_placement_creation(self):
        """Test that ShipPlacement can be created with valid parameters."""
        position = Position(3, 4)
        placement = ShipPlacement(position, Orientation.HORIZONTAL)
        
        assert placement.start_position == position
        assert placement.orientation == Orientation.HORIZONTAL

    def test_ship_placement_equality(self):
        """Test that two placements with same values are equal."""
        pos = Position(3, 4)
        placement1 = ShipPlacement(pos, Orientation.HORIZONTAL)
        placement2 = ShipPlacement(pos, Orientation.HORIZONTAL)
        placement3 = ShipPlacement(pos, Orientation.VERTICAL)
        
        assert placement1 == placement2
        assert placement1 != placement3

    def test_ship_placement_immutability(self):
        """Test that ShipPlacement is immutable."""
        placement = ShipPlacement(Position(3, 4), Orientation.HORIZONTAL)
        with pytest.raises(AttributeError):
            placement.orientation = Orientation.VERTICAL

    def test_ship_placement_string_representation(self):
        """Test ShipPlacement string representation."""
        placement = ShipPlacement(Position(3, 4), Orientation.HORIZONTAL)
        expected = "ShipPlacement(Position(3, 4), horizontal)"
        assert str(placement) == expected

    def test_ship_placement_calculate_positions(self):
        """Test calculating all positions for a ship placement."""
        # Horizontal placement
        placement = ShipPlacement(Position(2, 1), Orientation.HORIZONTAL)
        positions = placement.calculate_positions(3)
        expected = [Position(2, 1), Position(2, 2), Position(2, 3)]
        assert positions == expected
        
        # Vertical placement
        placement = ShipPlacement(Position(1, 2), Orientation.VERTICAL)
        positions = placement.calculate_positions(3)
        expected = [Position(1, 2), Position(2, 2), Position(3, 2)]
        assert positions == expected

    def test_ship_placement_calculate_positions_size_one(self):
        """Test calculating positions for size 1 ship."""
        placement = ShipPlacement(Position(5, 3), Orientation.HORIZONTAL)
        positions = placement.calculate_positions(1)
        expected = [Position(5, 3)]
        assert positions == expected

    def test_ship_placement_invalid_size(self):
        """Test that invalid size raises error."""
        placement = ShipPlacement(Position(0, 0), Orientation.HORIZONTAL)
        with pytest.raises(ValueError, match="Ship size must be positive"):
            placement.calculate_positions(0)
        with pytest.raises(ValueError, match="Ship size must be positive"):
            placement.calculate_positions(-1)