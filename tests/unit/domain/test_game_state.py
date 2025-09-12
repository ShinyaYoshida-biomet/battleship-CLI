"""Tests for GameState entity."""
import pytest
from src.domain.entities.game_state import GameState, GamePhase
from src.domain.entities.player import Player, PlayerType
from src.domain.entities.ship import Ship
from src.domain.value_objects.position import Position
from src.domain.value_objects.ship_placement import ShipPlacement, Orientation


class TestGamePhase:
    """Test cases for GamePhase enum."""

    def test_game_phase_values(self):
        """Test that GamePhase has correct values."""
        assert GamePhase.SETUP.value == "setup"
        assert GamePhase.SHIP_PLACEMENT.value == "ship_placement"
        assert GamePhase.BATTLE.value == "battle"
        assert GamePhase.GAME_OVER.value == "game_over"


class TestGameState:
    """Test cases for GameState entity."""

    def test_game_state_creation(self):
        """Test that GameState can be created with players."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        
        game_state = GameState([player1, player2])
        
        assert len(game_state.players) == 2
        assert player1 in game_state.players
        assert player2 in game_state.players
        assert game_state.current_player == player1
        assert game_state.phase == GamePhase.SETUP
        assert game_state.turn_number == 1
        assert game_state.winner is None

    def test_game_state_invalid_players(self):
        """Test that GameState raises error with invalid player count."""
        player1 = Player("Alice", PlayerType.HUMAN)
        
        # Too few players
        with pytest.raises(ValueError, match="Game requires exactly 2 players"):
            GameState([player1])
        
        # Too many players
        player2 = Player("Bob", PlayerType.COMPUTER)
        player3 = Player("Charlie", PlayerType.HUMAN)
        with pytest.raises(ValueError, match="Game requires exactly 2 players"):
            GameState([player1, player2, player3])

    def test_game_state_get_opponent(self):
        """Test getting the opponent of a player."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        assert game_state.get_opponent(player1) == player2
        assert game_state.get_opponent(player2) == player1

    def test_game_state_get_opponent_invalid_player(self):
        """Test getting opponent with invalid player."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        player3 = Player("Charlie", PlayerType.HUMAN)
        game_state = GameState([player1, player2])
        
        with pytest.raises(ValueError, match="Player .* is not in this game"):
            game_state.get_opponent(player3)

    def test_game_state_switch_turn(self):
        """Test switching turns between players."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        assert game_state.current_player == player1
        assert game_state.turn_number == 1
        
        game_state.switch_turn()
        
        assert game_state.current_player == player2
        assert game_state.turn_number == 2
        
        game_state.switch_turn()
        
        assert game_state.current_player == player1
        assert game_state.turn_number == 3

    def test_game_state_advance_phase(self):
        """Test advancing game phases."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        # Start in SETUP
        assert game_state.phase == GamePhase.SETUP
        
        # Advance to SHIP_PLACEMENT
        game_state.advance_phase()
        assert game_state.phase == GamePhase.SHIP_PLACEMENT
        
        # Advance to BATTLE
        game_state.advance_phase()
        assert game_state.phase == GamePhase.BATTLE
        
        # Advance to GAME_OVER
        game_state.advance_phase()
        assert game_state.phase == GamePhase.GAME_OVER
        
        # Cannot advance beyond GAME_OVER
        with pytest.raises(ValueError, match="Cannot advance from GAME_OVER phase"):
            game_state.advance_phase()

    def test_game_state_set_winner(self):
        """Test setting the game winner."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        assert game_state.winner is None
        assert not game_state.is_game_over()
        
        game_state.set_winner(player1)
        
        assert game_state.winner == player1
        assert game_state.phase == GamePhase.GAME_OVER
        assert game_state.is_game_over()

    def test_game_state_set_invalid_winner(self):
        """Test setting invalid winner."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        player3 = Player("Charlie", PlayerType.HUMAN)
        game_state = GameState([player1, player2])
        
        with pytest.raises(ValueError, match="Winner must be one of the players in the game"):
            game_state.set_winner(player3)

    def test_game_state_check_win_condition(self):
        """Test checking win conditions."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        # Place ships on both players so they're not considered to have "lost" initially
        placement1 = ShipPlacement(Position(0, 0), Orientation.HORIZONTAL)
        ship1 = Ship("P", "Patrol", 2, placement1)
        player1.place_ship(ship1)
        
        placement2 = ShipPlacement(Position(1, 1), Orientation.HORIZONTAL)
        ship2 = Ship("P", "Patrol", 2, placement2)
        player2.place_ship(ship2)
        
        # Both players have ships, no winner
        winner = game_state.check_win_condition()
        assert winner is None
        
        # Sink all of player2's ships
        player2.record_incoming_shot(Position(1, 1))
        player2.record_incoming_shot(Position(1, 2))
        
        # Now player1 should win
        winner = game_state.check_win_condition()
        assert winner == player1

    def test_game_state_is_setup_complete(self):
        """Test checking if setup is complete."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Bob", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        # Setup incomplete without ships
        assert not game_state.is_setup_complete()
        
        # Add ships to both players
        placement1 = ShipPlacement(Position(1, 1), Orientation.HORIZONTAL)
        ship1 = Ship("P", "Patrol", 2, placement1)
        player1.place_ship(ship1)
        
        # Still incomplete with only one player having ships
        assert not game_state.is_setup_complete()
        
        placement2 = ShipPlacement(Position(3, 3), Orientation.VERTICAL)
        ship2 = Ship("D", "Destroyer", 3, placement2)
        player2.place_ship(ship2)
        
        # Now setup is complete
        assert game_state.is_setup_complete()

    def test_game_state_get_game_summary(self):
        """Test getting game summary."""
        player1 = Player("Alice", PlayerType.HUMAN)
        player2 = Player("Computer", PlayerType.COMPUTER)
        game_state = GameState([player1, player2])
        
        summary = game_state.get_game_summary()
        
        assert summary["phase"] == "setup"
        assert summary["current_player"] == "Alice"
        assert summary["turn_number"] == 1
        assert summary["winner"] is None
        assert len(summary["players"]) == 2
        assert summary["players"][0]["name"] == "Alice"
        assert summary["players"][1]["name"] == "Computer"