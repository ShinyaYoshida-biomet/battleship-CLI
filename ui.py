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
                    styled_cell = "[dim]~[/dim][red]X[/red][dim]~[/dim]"
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
                                  placement_board: pd.DataFrame, ships_config: dict = None, opponent_name: str = "Enemy"):
        """Display firing and placement boards side by side with ship status."""
        
        firing_table = self.create_board_table(
            firing_board, 
            f"🎯 Your Attacks on Enemy", 
            show_ships=False
        )
        
        placement_table = self.create_board_table(
            placement_board, 
            f"🚢 Your Ships", 
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
        
        # Show ship status if ships_config is provided
        if ships_config:
            ship_status_panel = self.create_ship_status_panel(placement_board, ships_config)
            self.console.print(ship_status_panel)

    def create_ship_status_panel(self, placement_board: pd.DataFrame, ships_config: dict) -> Panel:
        """Create a panel showing current ship status."""
        ship_names = {
            'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
            'S': 'Submarine', 'P': 'Patrol boat'
        }
        
        status_text = "[bold]🚢 Ship Status:[/bold]\n"
        
        # Get all cells from placement board
        all_cells = placement_board.values.flatten().tolist()
        
        for ship_symbol, ship_size in ships_config.items():
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            # Count remaining cells for this ship
            remaining_cells = sum(1 for cell in all_cells if cell == ship_symbol)
            
            if remaining_cells == 0:
                # Ship is destroyed
                status_text += f"  [red]💥 {ship_name}: DESTROYED[/red]\n"
            elif remaining_cells < ship_size:
                # Ship is damaged
                status_text += f"  [yellow]⚠️  {ship_name}: DAMAGED ({remaining_cells}/{ship_size})[/yellow]\n"
            else:
                # Ship is intact
                status_text += f"  [green]✅ {ship_name}: INTACT ({remaining_cells}/{ship_size})[/green]\n"
        
        return Panel(
            status_text.rstrip(),
            title="📊 Fleet Status",
            border_style="bright_yellow",
            padding=(0, 1)
        )
        
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

    def prompt_ship_placement_mode(self, player_name: str) -> str:
        """Prompt user for ship placement mode."""
        self.console.print(f"\n[bold yellow]🚢 {player_name}, how would you like to place your ships?[/bold yellow]")
        
        choices = {
            "1": ("manual", "🎯 Manual - Place each ship yourself"),
            "2": ("random", "🎲 Random - Automatically place all ships")
        }
        
        for key, (_, description) in choices.items():
            self.console.print(f"  {key}. {description}")
            
        while True:
            choice = Prompt.ask("Choose placement mode", choices=list(choices.keys()), default="1")
            return choices[choice][0]
            
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
        
    def prompt_ship_placement(self, player_name: str, ship_symbol: str, ship_size: int, board_size: tuple) -> tuple:
        """Prompt for ship placement using single command format."""
        ship_names = {
            'C': 'Carrier',
            'B': 'Battleship', 
            'D': 'Destroyer',
            'S': 'Submarine',
            'P': 'Patrol boat'
        }
        
        ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\n[bold]🚢 {player_name}, placing your {ship_name}[/bold]")
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
                
                orientation, row_str, col_str = parts[0], parts[1], parts[2]
                
                if orientation.lower() not in ['h', 'v']:
                    self.console.print("[red]❌ Orientation must be 'h' or 'v' (e.g., 'h 3 2')[/red]")
                    continue
                    
                row, col = int(row_str), int(col_str)
                
                if not (0 <= row <= max_row and 0 <= col <= max_col):
                    self.console.print(f"[red]❌ Coordinates out of bounds! Valid range: 0-{max_row}, 0-{max_col}[/red]")
                    continue
                    
                return orientation.lower(), row, col
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers (e.g., 'v 3 2')[/red]")
                
    def prompt_fire_location(self, player_name: str, board_size: tuple) -> tuple:
        """Prompt for firing location."""
        max_row, max_col = board_size[0] - 1, board_size[1] - 1
        
        self.console.print(f"\n[bold red]🎯 {player_name}, time to fire![/bold red]")
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
                    
                return row, col
                
            except ValueError:
                self.console.print("[red]❌ Please enter valid numbers (e.g., '3 7')[/red]")
                
    def show_fire_result(self, player_name: str, target_player: str, row: int, col: int, 
                        hit: bool, ship_symbol: str = None, ship_destroyed: bool = False):
        """Show the result of a fire action."""
        if hit:
            ship_names = {
                'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
                'S': 'Submarine', 'P': 'Patrol boat'
            }
            ship_name = ship_names.get(ship_symbol, f'Ship {ship_symbol}')
            
            if ship_destroyed:
                message = f"[bold red]💥 SHIP DESTROYED![/bold red] {player_name} sunk {target_player}'s {ship_name}!"
                border_style = "bright_red"
            else:
                message = f"[bold green]🎯 HIT![/bold green] {player_name} hit {target_player}'s {ship_name} at ({row}, {col})"
                border_style = "bright_yellow"
        else:
            message = f"[bold red]❌ MISS![/bold red] {player_name} missed at ({row}, {col})"
            border_style = "red"
            
        panel = Panel(
            Align.center(message),
            border_style=border_style,
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