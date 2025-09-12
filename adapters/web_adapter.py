# -*- coding: utf-8 -*-
"""
Web Adapter for Battleship game (Structure for future implementation).
Implements Hexagonal Architecture ports for Web interface.
"""

from typing import Tuple, Optional
from domain.models import (
    GameState, ShipPlacement, FireAction, Ship, Position,
    PlacementContext, FireContext, GameResult, FireResult
)
from ports.game_ports import GameInputPort, GameOutputPort


class WebSocketConnection:
    """Abstraction for WebSocket connection. To be implemented."""
    
    def __init__(self, websocket):
        self.websocket = websocket
    
    async def send_json(self, data: dict):
        """Send JSON data to client."""
        # Implementation will depend on web framework (FastAPI, etc.)
        pass
    
    async def receive_json(self) -> dict:
        """Receive JSON data from client."""
        # Implementation will depend on web framework
        pass


class WebInputAdapter(GameInputPort):
    """Web implementation of GameInputPort using WebSocket."""
    
    def __init__(self, connection: WebSocketConnection):
        self.connection = connection
    
    async def get_ship_placement(self, context: PlacementContext) -> ShipPlacement:
        """Get ship placement from web client."""
        
        # Send placement request to client
        request = {
            "type": "ship_placement_request",
            "player_name": context.player_name,
            "ship": {
                "symbol": context.ship.symbol,
                "size": context.ship.size,
                "name": context.ship.name
            },
            "board_size": context.board_size,
            "board_state": self._serialize_board(context.current_board_state) if context.current_board_state is not None else None
        }
        
        await self.connection.send_json(request)
        
        # Wait for client response
        response = await self.connection.receive_json()
        
        # Parse response
        return ShipPlacement(
            player_name=context.player_name,
            ship=context.ship,
            orientation=response["orientation"],
            start_position=Position(response["row"], response["col"])
        )
    
    async def get_fire_action(self, context: FireContext) -> FireAction:
        """Get fire coordinates from web client."""
        
        # Send fire request to client
        request = {
            "type": "fire_request",
            "player_name": context.player_name,
            "board_size": context.board_size,
            "firing_board_state": self._serialize_board(context.firing_board_state) if context.firing_board_state is not None else None
        }
        
        await self.connection.send_json(request)
        
        # Wait for client response
        response = await self.connection.receive_json()
        
        return FireAction(
            player_name=context.player_name,
            target_position=Position(response["row"], response["col"])
        )
    
    async def get_game_mode_selection(self) -> str:
        """Get game mode selection from web client."""
        
        request = {"type": "game_mode_request"}
        await self.connection.send_json(request)
        
        response = await self.connection.receive_json()
        return response["mode"]  # "pvp" or "pvc"
    
    async def get_player_names(self, game_mode: str) -> Tuple[str, str]:
        """Get player names from web client."""
        
        request = {
            "type": "player_names_request",
            "game_mode": game_mode
        }
        await self.connection.send_json(request)
        
        response = await self.connection.receive_json()
        return response["player1"], response["player2"]
    
    def _serialize_board(self, board) -> Optional[list]:
        """Serialize pandas DataFrame to list for JSON."""
        if board is None:
            return None
        
        # Convert DataFrame to list of lists
        return board.values.tolist()


class WebOutputAdapter(GameOutputPort):
    """Web implementation of GameOutputPort using WebSocket."""
    
    def __init__(self, connection: WebSocketConnection):
        self.connection = connection
    
    async def show_welcome(self):
        """Display welcome screen to web client."""
        
        await self.connection.send_json({
            "type": "welcome_screen",
            "title": "🚢 BATTLESHIP CLI 🚢",
            "message": "Welcome to the modern Battleship experience!"
        })
    
    async def show_game_config(self, board_size: Tuple[int, int], ships: dict):
        """Display game configuration to web client."""
        
        await self.connection.send_json({
            "type": "game_config",
            "board_size": board_size,
            "ships": ships
        })
    
    async def show_game_state(self, state: GameState, 
                            firing_board: object = None, 
                            placement_board: object = None):
        """Display current game state to web client."""
        
        message = {
            "type": "game_state_update",
            "phase": state.phase.value,
            "current_player": state.current_player,
            "turn_counter": state.turn_counter,
            "board_size": state.board_size
        }
        
        if firing_board is not None:
            message["firing_board"] = self._serialize_board(firing_board)
        
        if placement_board is not None:
            message["placement_board"] = self._serialize_board(placement_board)
        
        await self.connection.send_json(message)
    
    async def show_placement_result(self, result: GameResult):
        """Display ship placement result to web client."""
        
        await self.connection.send_json({
            "type": "placement_result",
            "success": result.success,
            "message": result.message
        })
    
    async def show_fire_result(self, result: FireResult):
        """Display fire action result to web client."""
        
        await self.connection.send_json({
            "type": "fire_result",
            "hit": result.hit,
            "ship_symbol": result.ship_symbol,
            "ship_destroyed": result.ship_destroyed,
            "winner": result.winner
        })
    
    async def show_winner(self, winner: str, is_human: bool):
        """Display game winner to web client."""
        
        await self.connection.send_json({
            "type": "game_over",
            "winner": winner,
            "is_human": is_human
        })
    
    async def show_error(self, message: str):
        """Display error message to web client."""
        
        await self.connection.send_json({
            "type": "error",
            "message": message
        })
    
    def _serialize_board(self, board) -> Optional[list]:
        """Serialize pandas DataFrame to list for JSON."""
        if board is None:
            return None
        return board.values.tolist()


class WebAdapter(WebInputAdapter, WebOutputAdapter):
    """
    Combined Web adapter that implements both input and output ports.
    Ready for WebSocket-based web implementation.
    """
    
    def __init__(self, connection: WebSocketConnection):
        WebInputAdapter.__init__(self, connection)
        WebOutputAdapter.__init__(self, connection)


# Example FastAPI integration structure (for future implementation)
"""
from fastapi import FastAPI, WebSocket
from adapters.web_adapter import WebAdapter, WebSocketConnection
from application.game_service import GameService

app = FastAPI()

@app.websocket("/ws/game")
async def websocket_game(websocket: WebSocket):
    await websocket.accept()
    
    connection = WebSocketConnection(websocket)
    web_adapter = WebAdapter(connection)
    game_service = GameService(web_adapter, web_adapter)
    
    # Start game
    await game_service.start_new_game()
    await game_service.execute_ship_placement_phase()
    await game_service.execute_battle_phase()
"""