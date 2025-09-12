"""Tests for Position value object."""
import pytest
from src.domain.value_objects.position import Position


class TestPosition:
    """Test cases for Position value object."""

    def test_position_creation(self):
        """Test that Position can be created with valid coordinates."""
        pos = Position(3, 5)
        assert pos.row == 3
        assert pos.col == 5

    def test_position_equality(self):
        """Test that two positions with same coordinates are equal."""
        pos1 = Position(3, 5)
        pos2 = Position(3, 5)
        pos3 = Position(4, 5)
        
        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_immutability(self):
        """Test that Position is immutable."""
        pos = Position(3, 5)
        with pytest.raises(AttributeError):
            pos.row = 4

    def test_position_validation_negative_values(self):
        """Test that Position raises error for negative coordinates."""
        with pytest.raises(ValueError, match="Coordinates must be non-negative"):
            Position(-1, 5)
        with pytest.raises(ValueError, match="Coordinates must be non-negative"):
            Position(3, -1)

    def test_position_string_representation(self):
        """Test Position string representation."""
        pos = Position(3, 5)
        assert str(pos) == "Position(3, 5)"

    def test_position_hash(self):
        """Test that Position can be used as dictionary key."""
        pos1 = Position(3, 5)
        pos2 = Position(3, 5)
        pos3 = Position(4, 5)
        
        position_dict = {pos1: "test"}
        assert position_dict[pos2] == "test"  # Same position should work as key
        
        # Different positions should be different keys
        assert hash(pos1) == hash(pos2)
        assert hash(pos1) != hash(pos3)