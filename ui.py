# -*- coding: utf-8 -*-
"""Rich-based UI module for battleship game.

This module provides modern CLI interface using Rich library
for beautiful terminal output with colors, tables, and layouts.
"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich import box
import pandas as pd

console = Console()


class BattleshipUI:
    """Modern UI for Battleship game using Rich."""
    
    def __init__(self):
        self.console = console
        
    def show_welcome_screen(self):
        """Display welcome screen with ASCII art."""
        welcome_text = """
[bold blue]🚢 BATTLESHIP CLI 🚢[/bold blue]

[dim]                     _
                    | \\
                     '.|
     _-   _-    _-  _-||    _-    _-  _-   _-    _-    _-
       _-    _-   - __||___    _-       _-    _-    _-
    _-   _-    _-  |   _   |       _-   _-    _-
      _-    _-    /_) (_) (_\\        _-    _-       _-
              _.-'           `-._      ________       _-
        _..--`                   `-..'       .'
    _.-'  o/o                     o/o`-..__.'        ~  ~
 .-'      o|o                     o|o      `.._.  // ~  ~
 `-._     o|o                     o|o        |||<|||~  ~
     `-.__o\\o                     o|o       .'-'  \\\\ ~  ~
           `-.______________________\\_...-``'.       ~  ~
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
        
    def show_game_config(self, board_size: tuple, ships: Dict[str, int]):
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
        
    def show_game_rules(self, ships: Dict[str, int]):
        """Display game rules and ship information."""
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship',
            'D': 'Destroyer', 
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        rules_text = "[bold]Objective:[/bold] Sink all enemy ships by guessing their locations!\n\n"
        rules_text += "[bold]Ships to place:[/bold]\n"
        
        for ship_symbol, ship_size in ships.items():
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            rules_text += f"  🚢 {ship_name}: {ship_size} cells\n"
            
        rules_text += "\n[bold]Legend:[/bold]\n"
        rules_text += "  [green]🎯 O[/green] = Hit\n"
        rules_text += "  [red]❌ X[/red] = Miss\n"
        rules_text += "  [blue]🚢 Ship symbols[/blue] = Your ships\n"
        rules_text += "  [dim]~ [/dim] = Unknown water"
        
        panel = Panel(
            rules_text,
            title="📋 Game Rules",
            border_style="yellow",
            padding=(0, 2)
        )
        self.console.print(panel)
        
    def create_board_table(self, board_data: pd.DataFrame, title: str, show_ships: bool = False) -> Table:
        """Create a Rich table for board display."""
        table = Table(title=title, box=box.SQUARE, show_header=True, header_style="bold magenta")
        
        # Add column headers
        table.add_column("", style="dim", width=2)
        for col in range(board_data.shape[1]):
            table.add_column(str(col), justify="center", width=3)
        
        # Add rows
        for row in range(board_data.shape[0]):
            row_data = [str(row)]
            for col in range(board_data.shape[1]):
                cell_value = board_data.iloc[row, col]
                
                # Apply styling based on cell content
                if cell_value == 'O':  # Hit
                    styled_cell = "[bold green]🎯[/bold green]"
                elif cell_value == 'X':  # Miss
                    styled_cell = "[bold red]❌[/bold red]"
                elif cell_value == ' ':  # Unknown
                    styled_cell = "[dim]~[/dim]"
                elif cell_value == '*':  # Water (placement board)
                    styled_cell = "[blue]~[/blue]"
                elif show_ships and cell_value in ['B', 'D', 'P', 'C', 'S']:  # Ship
                    styled_cell = f"[bold blue]{cell_value}[/bold blue]"
                else:
                    styled_cell = str(cell_value)
                    
                row_data.append(styled_cell)
            
            table.add_row(*row_data)
            
        return table
        
    def display_boards_side_by_side(self, player_name: str, firing_board: pd.DataFrame, 
                                  placement_board: pd.DataFrame, opponent_name: str = "Enemy"):
        """Display firing and placement boards side by side."""
        
        firing_table = self.create_board_table(
            firing_board, 
            f"🎯 {player_name}'s Attack Board", 
            show_ships=False
        )
        
        placement_table = self.create_board_table(
            placement_board, 
            f"🚢 {player_name}'s Fleet", 
            show_ships=True
        )
        
        # Create side-by-side layout
        columns = Columns([firing_table, placement_table], equal=True, expand=True)
        
        self.console.print()
        self.console.print(Panel(
            columns,
            title=f"⚔️  {player_name}'s Battle View",
            border_style="bright_cyan",
            padding=(1, 2)
        ))
        
    def prompt_game_mode(self) -> str:
        """Prompt user for game mode selection."""
        self.console.print("\n[bold yellow]🎮 Select Game Mode[/bold yellow]")
        
        choices = {
            "1": ("pvp", "👥 Player vs Player"),
            "2": ("pvc", "🤖 Player vs Computer")
        }
        
        for key, (_, description) in choices.items():
            self.console.print(f"  {key}. {description}")
            
        while True:
            choice = Prompt.ask("Choose mode", choices=list(choices.keys()), default="2")
            return choices[choice][0]
            
    def prompt_player_names(self, game_mode: str) -> tuple:
        """Prompt for player names."""
        if game_mode == "pvp":
            player1 = Prompt.ask("[bold blue]Player 1[/bold blue], enter your name", default="Player1")
            player2 = Prompt.ask("[bold green]Player 2[/bold green], enter your name", default="Player2") 
            return player1, player2
        else:
            player1 = Prompt.ask("[bold blue]Player[/bold blue], enter your name", default="Player")
            return player1, "Computer"
            
    def announce_vs(self, player1: str, player2: str):
        """Announce the matchup."""
        vs_text = f"[bold blue]{player1}[/bold blue] [red]VS[/red] [bold green]{player2}[/bold green]"
        
        panel = Panel(
            Align.center(vs_text),
            title="⚔️ Battle Commences!",
            border_style="bright_red",
            padding=(1, 4)
        )
        self.console.print(panel)
        
    def prompt_ship_orientation(self, player_name: str, ship_symbol: str, ship_size: int) -> str:
        """Prompt for ship orientation."""
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship',
            'D': 'Destroyer',
            'S': 'Submarine', 
            'P': 'Patrol boat'
        }
        
        ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        
        self.console.print(f"\n[bold]🚢 {player_name}, placing your {ship_name}[/bold]")
        self.console.print(f"   Size: [yellow]{ship_size}[/yellow] cells")
        self.console.print("   Orientation:")
        self.console.print("   [green]H[/green] = Horizontal (→→→)")
        self.console.print("   [blue]V[/blue] = Vertical   (↓)")
        self.console.print("                  (↓)")
        self.console.print("                  (↓)")
        
        return Prompt.ask("Enter orientation", choices=["h", "v", "H", "V"], default="h").lower()
        
    def prompt_ship_location(self, ship_name: str, ship_size: int, board_size: tuple) -> tuple:
        """Prompt for ship starting location."""
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\n[bold]📍 Where to place your {ship_name}?[/bold]")
        self.console.print(f"   Ship length: [yellow]{ship_size}[/yellow] cells")
        self.console.print(f"   Valid coordinates: [dim]0-{max_row} for rows, 0-{max_col} for columns[/dim]")
        
        while True:
            location_str = Prompt.ask("Starting position (row column)", default="0 0")
            try:
                parts = location_str.strip().split()
                if len(parts) != 2:
                    self.console.print("[red]❌ Please enter two numbers separated by space[/red]")
                    continue
                    
                row, col = int(parts[0]), int(parts[1])
                
                if not (0 <= row <= max_row and 0 <= col <= max_col):
                    self.console.print(f"[red]❌ Coordinates out of bounds! Valid range: 0-{max_row}, 0-{max_col}[/red]")
                    continue
                    
                return row, col
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers[/red]")
                
    def prompt_fire_location(self, player_name: str, board_size: tuple) -> tuple:
        """Prompt for firing location."""
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\n[bold red]🎯 {player_name}, time to fire![/bold red]")
        self.console.print(f"   Valid coordinates: [dim]0-{max_row} for rows, 0-{max_col} for columns[/dim]")
        
        while True:
            location_str = Prompt.ask("Target coordinates (row column)")
            try:
                parts = location_str.strip().split()
                if len(parts) != 2:
                    self.console.print("[red]❌ Please enter two numbers separated by space[/red]")
                    continue
                    
                row, col = int(parts[0]), int(parts[1])
                
                if not (0 <= row <= max_row and 0 <= col <= max_col):
                    self.console.print(f"[red]❌ Coordinates out of bounds! Valid range: 0-{max_row}, 0-{max_col}[/red]")
                    continue
                    
                return row, col
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers[/red]")
                
    def show_fire_result(self, player_name: str, target_player: str, row: int, col: int, 
                        hit: bool, ship_symbol: str = None):
        """Show the result of a fire action."""
        if hit:
            ship_names = {
                'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
                'S': 'Submarine', 'P': 'Patrol boat'
            }
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            message = f"[bold green]🎯 HIT![/bold green] {player_name} hit {target_player}'s {ship_name} at ({row}, {col})"
        else:
            message = f"[bold red]❌ MISS![/bold red] {player_name} missed at ({row}, {col})"
            
        panel = Panel(
            Align.center(message),
            border_style="bright_yellow" if hit else "red",
            padding=(0, 2)
        )
        self.console.print(panel)
        
    def show_ship_placed(self, ship_name: str, orientation: str, row: int, col: int):
        """Show confirmation of ship placement."""
        direction = "horizontally" if orientation == 'h' else "vertically"
        message = f"[bold green]✅ {ship_name} placed {direction} at ({row}, {col})![/bold green]"
        self.console.print(message)
        
    def show_placement_error(self, ship_name: str):
        """Show ship placement error."""
        error_text = f"""[bold red]❌ Cannot place {ship_name} there![/bold red]

[yellow]Reasons this might happen:[/yellow]
• Ship would go off the board
• Ship would overlap with another ship

Let's try a different position..."""
        
        self.console.print(Panel(error_text, border_style="red"))
        
    def show_computer_thinking(self, computer_name: str):
        """Show computer thinking animation."""
        self.console.print(f"\n[bold blue]{computer_name} is thinking...[/bold blue] 🤔")
        
    def show_computer_action(self, computer_name: str, action: str, details: str = ""):
        """Show computer action."""
        message = f"[bold blue]{computer_name}[/bold blue] {action}"
        if details:
            message += f": {details}"
        self.console.print(message)
        
    def show_game_winner(self, winner: str, is_human: bool):
        """Show game winner announcement."""
        if is_human:
            winner_text = f"[bold green]🎉 {winner} WINS! 🎉[/bold green]\n\n[yellow]Congratulations! You've sunk all enemy ships![/yellow]"
            border_color = "bright_green"
        else:
            winner_text = f"[bold red]🤖 {winner} WINS! 🤖[/bold red]\n\n[yellow]The computer beat you this time.\nBetter luck next time![/yellow]"
            border_color = "bright_red"
            
        panel = Panel(
            Align.center(winner_text),
            title="🏆 GAME OVER",
            border_style=border_color,
            padding=(2, 4)
        )
        self.console.print(panel)
        
    def pause_for_input(self, message: str = "Press Enter to continue..."):
        """Pause and wait for user input."""
        Prompt.ask(f"[dim]{message}[/dim]", default="", show_default=False)
        
    def clear_screen(self):
        """Clear the console screen."""
        self.console.clear()
        
    def show_turn_header(self, player_name: str, turn_number: int = None):
        """Show turn header."""
        title = f"⚔️ {player_name}'s Turn"
        if turn_number:
            title += f" (Turn {turn_number})"
            
        self.console.print(f"\n[bold bright_cyan]{title}[/bold bright_cyan]")
        self.console.rule(style="bright_cyan")


# Global UI instance
ui = BattleshipUI()