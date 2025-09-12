"""Console-based notification service."""
from typing import Dict, Any
from rich.console import Console

from ...domain.entities.player import Player
from ...domain.entities.ship import Ship
from ...domain.entities.board import CellState
from ...domain.value_objects.position import Position
from ...ports.notification_port import NotificationPort


class ConsoleNotificationService(NotificationPort):
    """Console implementation of the notification port."""
    
    def __init__(self):
        self.console = Console()
    
    def notify_game_started(self, player1: Player, player2: Player) -> None:
        """Notify that a game has started."""
        self.console.print(f"[bold green]🎮 Game started: {player1.name} vs {player2.name}[/bold green]")
    
    def notify_turn_started(self, player: Player, turn_number: int) -> None:
        """Notify that a player's turn has started."""
        self.console.print(f"[blue]🎯 Turn {turn_number}: {player.name}'s turn[/blue]")
    
    def notify_ship_placed(self, player: Player, ship: Ship) -> None:
        """Notify that a ship has been placed."""
        direction = "horizontally" if ship.placement.orientation.value == "horizontal" else "vertically"
        pos = ship.placement.start_position
        self.console.print(f"[green]✅ {player.name} placed {ship.name} {direction} at ({pos.row}, {pos.col})[/green]")
    
    def notify_shot_fired(
        self, 
        shooter: Player, 
        target: Player, 
        position: Position, 
        result: CellState
    ) -> None:
        """Notify that a shot was fired."""
        result_text = "HIT" if result == CellState.HIT else "MISS"
        color = "green" if result == CellState.HIT else "red"
        self.console.print(f"[{color}]🎯 {shooter.name} fired at ({position.row}, {position.col}) -> {result_text}[/{color}]")
    
    def notify_ship_hit(self, player: Player, ship: Ship, position: Position) -> None:
        """Notify that a ship was hit."""
        self.console.print(f"[yellow]💥 {player.name}'s {ship.name} was hit at ({position.row}, {position.col})[/yellow]")
    
    def notify_ship_sunk(self, player: Player, ship: Ship) -> None:
        """Notify that a ship was sunk."""
        self.console.print(f"[bold red]🚢 {player.name}'s {ship.name} has been sunk![/bold red]")
    
    def notify_game_over(self, winner: Player, loser: Player) -> None:
        """Notify that the game is over."""
        self.console.print(f"[bold bright_green]🏆 Game Over! {winner.name} defeats {loser.name}![/bold bright_green]")
    
    def notify_error(self, error_type: str, message: str, context: Dict[str, Any] = None) -> None:
        """Notify of an error condition."""
        self.console.print(f"[bold red]❌ {error_type}: {message}[/bold red]")
        if context:
            self.console.print(f"[dim]Context: {context}[/dim]")
    
    def notify_info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Notify of an informational event."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
        if context:
            self.console.print(f"[dim]Context: {context}[/dim]")