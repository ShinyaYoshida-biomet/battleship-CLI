"""CLI UI Adapter for Rich-based terminal interface."""
import time
from typing import Tuple, Dict, Any
import pandas as pd

from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Prompt

from ...domain.entities.board import CellState
from ...domain.entities.player import Player
from ...domain.entities.ship import Ship
from ...domain.value_objects.position import Position
from ...domain.value_objects.ship_placement import ShipPlacement, Orientation
from ...ports.ui_port import UIPort


console = Console()


class CLIUIAdapter(UIPort):
    """CLI implementation of the UI port using Rich library."""
    
    def __init__(self):
        self.console = console
    
    def display_welcome_screen(self) -> None:
        """Display welcome screen with ASCII art."""
        welcome_text = """
[bold blue]🚢 BATTLESHIP CLI 🚢[/bold blue]

[dim]                     _
                    | \\\\
                     '.|\n     _-   _-    _-  _-||    _-    _-  _-   _-    _-    _-
       _-    _-   - __||___    _-       _-    _-    _-
    _-   _-    _-  |   _   |       _-   _-    _-
      _-    _-    /_) (_) (_\\\\        _-    _-       _-
              _.-'           `-._      ________       _-
        _..--`                   `-..'       .'
    _.-'  o/o                     o/o`-..__.'        ~  ~
 .-'      o|o                     o|o      `.._.  // ~  ~
 `-._     o|o                     o|o        |||<|||~  ~
     `-.__o\\\\o                     o|o       .'-'  \\\\\\\\ ~  ~
           `-.______________________\\\\_...-``'.       ~  ~
                                    `._______`.
[/dim]

[bold green]Welcome to the modern Battleship experience![/bold green]
"""
        
        panel = Panel(
            welcome_text,
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(Align.center(panel))
    
    def prompt_game_mode(self) -> str:
        """Prompt user for game mode selection."""
        self.console.print("\\n[bold yellow]🎮 Select Game Mode[/bold yellow]")
        
        choices = {
            "1": ("pvp", "👥 Player vs Player"),
            "2": ("pvc", "🤖 Player vs Computer")
        }
        
        for key, (_, description) in choices.items():
            self.console.print(f"  {key}. {description}")
            
        while True:
            choice = Prompt.ask("Choose mode", choices=list(choices.keys()), default="2")
            return choices[choice][0]
    
    def prompt_player_names(self, mode: str) -> Tuple[str, str]:
        """Prompt for player names."""
        if mode == "pvp":
            player1 = Prompt.ask("[bold blue]Player 1[/bold blue], enter your name", default="Player1")
            player2 = Prompt.ask("[bold green]Player 2[/bold green], enter your name", default="Player2") 
            return player1, player2
        else:
            player1 = Prompt.ask("[bold blue]Player[/bold blue], enter your name", default="Player")
            return player1, "Computer"
    
    def display_game_config(self, board_size: Tuple[int, int], ships: Dict[str, int]) -> None:
        """Display game configuration."""
        config_text = f"""
[bold]Board Size:[/bold] {board_size[0]} x {board_size[1]}
[bold]Ships:[/bold] {', '.join([f'{name}({size})' for name, size in ships.items()])}
"""
        
        panel = Panel(
            config_text,
            title="🎮 Game Configuration",
            border_style="green",
            padding=(0, 2)
        )
        self.console.print(panel)
    
    def prompt_ship_placement_mode(self, player_name: str) -> str:
        """Prompt player for ship placement mode."""
        self.console.print(f"\\n[bold yellow]🚢 {player_name}, how would you like to place your ships?[/bold yellow]\\n")
        
        self.console.print("  [bold green]1[/bold green]. 🎲 Random - Automatically place all ships [dim](Recommended)[/dim]")
        self.console.print("  [bold green]2[/bold green]. 🎯 Manual - Place each ship yourself")
        self.console.print()
        
        while True:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Enter your choice[/bold cyan]", 
                    choices=["1", "2"], 
                    default="1",
                    show_choices=False
                )
                
                if choice == "1":
                    self.console.print("[green]✓ Random placement selected![/green]")
                    return "random"
                else:
                    self.console.print("[green]✓ Manual placement selected![/green]")
                    return "manual"
                    
            except KeyboardInterrupt:
                raise
            except Exception:
                self.console.print("[red]Invalid choice. Please enter 1 or 2.[/red]")
                continue
    
    def prompt_ship_placement(
        self, 
        player_name: str, 
        ship_symbol: str, 
        ship_size: int,
        board_size: Tuple[int, int]
    ) -> ShipPlacement:
        """Prompt player for ship placement."""
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship', 
            'D': 'Destroyer',
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\\n[bold]🚢 {player_name}, placing your {ship_name}[/bold]")
        self.console.print(f"   Size: [yellow]{ship_size}[/yellow] cells")
        self.console.print("   Command format: [yellow]orientation row column[/yellow]")
        self.console.print("   • [green]h row column[/green] = Horizontal (→→→)")
        self.console.print("   • [blue]v row column[/blue] = Vertical (↓↓↓)")
        self.console.print(f"   Valid coordinates: [dim]0-{max_row} for rows, 0-{max_col} for columns[/dim]")
        
        while True:
            command_str = Prompt.ask("Placement command", default="h 0 0")
            try:
                parts = command_str.strip().split()
                if len(parts) != 3:
                    self.console.print("[red]❌ Please use format: orientation row column (e.g., 'v 3 2')[/red]")
                    continue
                
                orientation_str, row_str, col_str = parts[0], parts[1], parts[2]
                
                if orientation_str.lower() not in ['h', 'v']:
                    self.console.print("[red]❌ Orientation must be 'h' or 'v' (e.g., 'h 3 2')[/red]")
                    continue
                    
                row, col = int(row_str), int(col_str)
                
                if not (0 <= row <= max_row and 0 <= col <= max_col):
                    self.console.print(f"[red]❌ Coordinates out of bounds! Valid range: 0-{max_row}, 0-{max_col}[/red]")
                    continue
                
                # Convert to domain objects
                position = Position(row, col)
                orientation = Orientation.HORIZONTAL if orientation_str.lower() == 'h' else Orientation.VERTICAL
                
                return ShipPlacement(position, orientation)
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers (e.g., 'v 3 2')[/red]")
    
    def prompt_fire_location(self, player_name: str, board_size: Tuple[int, int]) -> Position:
        """Prompt player for firing location."""
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\\n[bold red]🎯 {player_name}, time to fire![/bold red]")
        self.console.print(f"   Format: [yellow]row column[/yellow] (e.g., '3 7')")
        self.console.print(f"   Valid coordinates: [dim]0-{max_row} for rows, 0-{max_col} for columns[/dim]")
        
        while True:
            command_str = Prompt.ask("Target coordinates")
            try:
                parts = command_str.strip().split()
                if len(parts) != 2:
                    self.console.print("[red]❌ Please use format: row column (e.g., '3 7')[/red]")
                    continue
                    
                row, col = int(parts[0]), int(parts[1])
                
                if not (0 <= row <= max_row and 0 <= col <= max_col):
                    self.console.print(f"[red]❌ Coordinates out of bounds! Valid range: 0-{max_row}, 0-{max_col}[/red]")
                    continue
                    
                return Position(row, col)
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers (e.g., '3 7')[/red]")
    
    def display_placement_board(self, player: Player) -> None:
        """Display player's placement board."""
        board_table = self._create_board_table(player.placement_board, f"🚢 Your Ships", show_ships=True)
        self.console.print(board_table)
    
    def display_firing_board(self, player: Player) -> None:
        """Display player's firing board."""
        board_table = self._create_board_table(player.firing_board, f"🎯 Your Attacks", show_ships=False)
        self.console.print(board_table)
    
    def display_boards_side_by_side(self, player: Player, opponent: Player) -> None:
        """Display both boards side by side."""
        firing_table = self._create_board_table(
            player.firing_board, 
            f"🎯 Your Attacks on {opponent.name}", 
            show_ships=False
        )
        
        placement_table = self._create_board_table(
            player.placement_board, 
            f"🚢 Your Ships", 
            show_ships=True
        )
        
        columns = Columns([firing_table, placement_table], equal=True, expand=True)
        
        self.console.print()
        self.console.print(Panel(
            columns,
            title=f"⚔️  {player.name}'s Battle View",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
    
    def display_turn_header(self, player_name: str, turn_number: int) -> None:
        """Display turn header."""
        title = f"⚔️ {player_name}'s Turn"
        if turn_number:
            title += f" (Turn {turn_number})"
            
        self.console.print(f"\\n[bold bright_cyan]{title}[/bold bright_cyan]")
        self.console.rule(style="bright_cyan")
    
    def display_fire_result(
        self, 
        shooter: str, 
        target: str, 
        position: Position, 
        result: CellState,
        ship_symbol: str = None
    ) -> None:
        """Display the result of a fire action."""
        row, col = position.row, position.col
        
        if result == CellState.HIT:
            ship_names = {
                'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
                'S': 'Submarine', 'P': 'Patrol boat'
            }
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            message = f"[bold green]🎯 HIT![/bold green] {shooter} hit {target}'s {ship_name} at ({row}, {col})"
            border_style = "bright_yellow"
        else:
            message = f"[bold red]❌ MISS![/bold red] {shooter} missed at ({row}, {col})"
            border_style = "red"
            
        panel = Panel(
            Align.center(message),
            border_style=border_style,
            padding=(0, 2)
        )
        self.console.print(panel)
    
    def display_ship_sunk(self, player_name: str, ship: Ship) -> None:
        """Display ship sunk notification."""
        message = f"[bold red]💥 SHIP DESTROYED![/bold red] {player_name}'s {ship.name} has been sunk!"
        panel = Panel(
            Align.center(message),
            border_style="bright_red",
            padding=(0, 2)
        )
        self.console.print(panel)
    
    def display_game_winner(self, winner: Player, is_human: bool) -> None:
        """Display game winner."""
        if is_human:
            winner_text = f"[bold green]🎉 {winner.name} WINS! 🎉[/bold green]\\n\\n[yellow]Congratulations! You've sunk all enemy ships![/yellow]"
            border_color = "bright_green"
        else:
            winner_text = f"[bold red]🤖 {winner.name} WINS! 🤖[/bold red]\\n\\n[yellow]The computer beat you this time.\\nBetter luck next time![/yellow]"
            border_color = "bright_red"
            
        panel = Panel(
            Align.center(winner_text),
            title="🏆 GAME OVER",
            border_style=border_color,
            padding=(2, 4)
        )
        self.console.print(panel)
    
    def display_error(self, message: str) -> None:
        """Display error message."""
        self.console.print(f"[bold red]❌ Error: {message}[/bold red]")
    
    def display_info(self, message: str) -> None:
        """Display informational message."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        self.console.clear()
    
    def _create_board_table(self, board, title: str, show_ships: bool = False) -> Table:
        """Create a Rich table for board display."""
        table = Table(title=title, box=box.SQUARE, show_header=True, header_style="bold magenta")
        
        # Add column headers
        table.add_column("", style="dim", width=2)
        for col in range(board.cols):
            table.add_column(str(col), justify="center", width=3)
        
        # Add rows
        for row in range(board.rows):
            row_data = [str(row)]
            for col in range(board.cols):
                position = Position(row, col)
                cell_state = board.get_cell_state(position)
                
                # Apply styling based on cell content
                if cell_state == CellState.HIT:
                    styled_cell = "[bold green]🎯[/bold green]"
                elif cell_state == CellState.MISS:
                    styled_cell = "[dim]~[/dim][red]X[/red][dim]~[/dim]"
                elif cell_state == CellState.WATER:
                    if show_ships:
                        styled_cell = "[blue]~[/blue]"
                    else:
                        styled_cell = "[dim]~[/dim]"
                elif cell_state == CellState.SHIP and show_ships:
                    # Get ship symbol from board
                    ship = board.get_ship_at_position(position)
                    ship_symbol = ship.symbol if ship else "S"
                    styled_cell = f"[bold blue]{ship_symbol}[/bold blue]"
                else:
                    styled_cell = "[dim]~[/dim]"
                    
                row_data.append(styled_cell)
            
            table.add_row(*row_data)
            
        return table