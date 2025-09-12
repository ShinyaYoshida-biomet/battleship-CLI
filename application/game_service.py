# -*- coding: utf-8 -*-
"""
Application Service for Battleship game.
Contains pure business logic without UI dependencies.
"""

from typing import Dict, List, Optional, Tuple
from domain.models import (
    GameState, GamePhase, PlayerType, PlayerInfo, Ship, 
    ShipPlacement, FireAction, FireResult, GameResult,
    PlacementContext, FireContext, Position
)
from ports.game_ports import GameInputPort, GameOutputPort, AIPort

# Import existing infrastructure
from config import Config
from game import Game


class GameService:
    """
    Application service that orchestrates the game flow.
    Uses existing Game class internally but abstracts UI through ports.
    """
    
    def __init__(self, 
                 input_port: GameInputPort,
                 output_port: GameOutputPort, 
                 ai_port: AIPort):
        self.input_port = input_port
        self.output_port = output_port
        self.ai_port = ai_port
        
        # Game state
        self.game_state: Optional[GameState] = None
        self.game_engine: Optional[Game] = None
        
    async def start_new_game(self, 
                           board_size: Tuple[int, int] = (7, 7),
                           ships_config: Dict[str, int] = None) -> GameResult:
        """Initialize and start a new game."""
        
        if ships_config is None:
            ships_config = {'B': 4, 'D': 3, 'P': 2}
        
        await self.output_port.show_welcome()
        
        # Get game mode and player names through ports
        game_mode = await self.input_port.get_game_mode_selection()
        player1_name, player2_name = await self.input_port.get_player_names(game_mode)
        
        # Determine player types
        player_types = ['human', 'computer'] if game_mode == 'pvc' else ['human', 'human']
        
        # Show configuration
        await self.output_port.show_game_config(board_size, ships_config)
        
        # Initialize game state
        players = [
            PlayerInfo(player1_name, PlayerType.HUMAN),
            PlayerInfo(player2_name, PlayerType.COMPUTER if game_mode == 'pvc' else PlayerType.HUMAN)
        ]
        
        self.game_state = GameState(
            phase=GamePhase.SHIP_PLACEMENT,
            current_player=player1_name,
            players=players,
            board_size=board_size,
            ships_config=ships_config
        )
        
        # Initialize underlying game engine (reuse existing logic)
        config = Config(config_path=None, board_size=board_size, ships=ships_config)
        self.game_engine = Game(config, [player1_name, player2_name], player_types)
        self.game_engine.set_players()
        
        return GameResult(True, "Game initialized successfully", self.game_state)
    
    async def execute_ship_placement_phase(self) -> GameResult:
        """Handle ship placement for all players."""
        
        for player_info in self.game_state.players:
            player_name = player_info.name
            
            for ship_symbol, ship_size in self.game_state.ships_config.items():
                ship = Ship(ship_symbol, ship_size, self._get_ship_name(ship_symbol))
                
                # Show current board state
                placement_board = self.game_engine.players[player_name].placement_board.board
                await self.output_port.show_game_state(
                    self.game_state,
                    placement_board=placement_board
                )
                
                if player_info.player_type == PlayerType.HUMAN:
                    # Get placement from user
                    context = PlacementContext(
                        player_name=player_name,
                        ship=ship,
                        board_size=self.game_state.board_size,
                        current_board_state=placement_board
                    )
                    placement = await self.input_port.get_ship_placement(context)
                else:
                    # Get placement from AI
                    context = PlacementContext(
                        player_name=player_name,
                        ship=ship,
                        board_size=self.game_state.board_size,
                        current_board_state=placement_board
                    )
                    placement = await self.ai_port.get_ship_placement_decision(context)
                
                # Execute placement using existing game engine
                result = await self._execute_ship_placement(placement)
                await self.output_port.show_placement_result(result)
                
                if not result.success:
                    await self.output_port.show_error(result.message)
        
        # Move to battle phase
        self.game_state.phase = GamePhase.BATTLE
        self.game_state.current_player = self.game_state.players[0].name
        
        return GameResult(True, "Ship placement phase completed", self.game_state)
    
    async def execute_battle_phase(self) -> GameResult:
        """Handle battle phase with turn-based combat."""
        
        while self.game_state.phase == GamePhase.BATTLE:
            current_player_info = self._get_current_player_info()
            
            # Show game state
            firing_board = self.game_engine.players[current_player_info.name].firing_board.board
            placement_board = self.game_engine.players[current_player_info.name].placement_board.board
            
            await self.output_port.show_game_state(
                self.game_state, 
                firing_board=firing_board,
                placement_board=placement_board
            )
            
            # Get fire action
            if current_player_info.player_type == PlayerType.HUMAN:
                context = FireContext(
                    player_name=current_player_info.name,
                    board_size=self.game_state.board_size,
                    firing_board_state=firing_board
                )
                fire_action = await self.input_port.get_fire_action(context)
            else:
                # AI fire action
                context = FireContext(
                    player_name=current_player_info.name,
                    board_size=self.game_state.board_size,
                    firing_board_state=firing_board
                )
                fire_action = await self.ai_port.get_fire_decision(context)
            
            # Execute fire action
            fire_result = await self._execute_fire_action(fire_action)
            await self.output_port.show_fire_result(fire_result)
            
            # Check for winner
            if fire_result.winner:
                self.game_state.phase = GamePhase.FINISHED
                self.game_state.winner = fire_result.winner
                await self.output_port.show_winner(
                    fire_result.winner, 
                    self._is_human_player(fire_result.winner)
                )
                break
            
            # Switch turn
            self._switch_turn()
            self.game_state.turn_counter += 1
        
        return GameResult(True, "Battle phase completed", self.game_state)
    
    # Helper methods
    def _get_ship_name(self, symbol: str) -> str:
        ship_names = {
            'C': 'Carrier', 'B': 'Battleship', 'D': 'Destroyer',
            'S': 'Submarine', 'P': 'Patrol boat'
        }
        return ship_names.get(symbol, f'Ship {symbol}')
    
    def _get_current_player_info(self) -> PlayerInfo:
        for player in self.game_state.players:
            if player.name == self.game_state.current_player:
                return player
        raise ValueError(f"Current player {self.game_state.current_player} not found")
    
    def _is_human_player(self, player_name: str) -> bool:
        for player in self.game_state.players:
            if player.name == player_name:
                return player.player_type == PlayerType.HUMAN
        return False
    
    def _switch_turn(self):
        current_index = next(i for i, p in enumerate(self.game_state.players) 
                           if p.name == self.game_state.current_player)
        next_index = (current_index + 1) % len(self.game_state.players)
        self.game_state.current_player = self.game_state.players[next_index].name
    
    async def _execute_ship_placement(self, placement: ShipPlacement) -> GameResult:
        """Execute ship placement using existing game engine."""
        try:
            # Use existing game engine logic
            self.game_engine.orient = placement.orientation
            self.game_engine.x = placement.start_position.row
            self.game_engine.y = placement.start_position.col
            
            success = self.game_engine.players[placement.player_name].placement_board.set_ship(
                placement.orientation,
                placement.start_position.row,
                placement.start_position.col,
                placement.ship.symbol,
                placement.ship.size,
                self.game_engine.h_symbols,
                self.game_engine.v_symbols
            )
            
            if success:
                return GameResult(True, f"{placement.ship.name} placed successfully")
            else:
                return GameResult(False, f"Cannot place {placement.ship.name} at specified location")
                
        except Exception as e:
            return GameResult(False, f"Error placing ship: {str(e)}")
    
    async def _execute_fire_action(self, fire_action: FireAction) -> FireResult:
        """Execute fire action using existing game engine."""
        try:
            # Set fire coordinates
            self.game_engine.fire_x = fire_action.target_position.row
            self.game_engine.fire_y = fire_action.target_position.col
            
            # Get opponent
            opponent_name = next(p.name for p in self.game_state.players 
                               if p.name != fire_action.player_name)
            
            # Execute fire using existing logic
            self.game_engine.fire(fire_action.player_name, opponent_name)
            
            # Check hit/miss
            target_symbol = self.game_engine.players[opponent_name].placement_board.board.iloc[
                fire_action.target_position.row, fire_action.target_position.col
            ]
            
            hit = target_symbol in self.game_state.ships_config.keys()
            
            # Check if ship is destroyed
            ship_destroyed = False
            if hit:
                opponent_board = self.game_engine.players[opponent_name].placement_board.board
                all_cells = opponent_board.values.flatten().tolist()
                remaining_cells_of_hit_ship = sum(1 for cell in all_cells if cell == target_symbol)
                ship_destroyed = remaining_cells_of_hit_ship == 0
            
            # Check for winner - check if all ships are destroyed
            opponent_board = self.game_engine.players[opponent_name].placement_board.board
            all_cells = opponent_board.values.flatten().tolist()
            remaining_ships = [cell for cell in all_cells if cell in self.game_state.ships_config.keys()]
            winner = fire_action.player_name if len(remaining_ships) == 0 else None
            
            return FireResult(
                hit=hit,
                ship_symbol=target_symbol if hit else None,
                ship_destroyed=ship_destroyed,
                winner=winner
            )
            
        except Exception as e:
            return FireResult(False, None, False, None)