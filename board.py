# -*- coding: utf-8 -*-
"""Board module called in player instance.

Example:
    board = Board(5, 5)
    board.board()
"""

import pandas as pd


class Board:
    """Board class of battleship game.
    Board is an object with dataframe expressing a player's board
    Example of 10 × 10 board

               0  1  2  3  4  5  6  7  8  9
            0  S  S  S  *  *  *  *  *  *  *
            1  *  P  *  *  *  *  *  *  *  *
            2  *  P  *  *  *  *  *  *  *  *
            3  *  *  *  *  *  *  *  *  *  *
            4  *  *  *  *  *  *  *  *  *  *
            5  *  *  *  *  *  *  *  *  *  *
            6  *  *  *  *  *  *  *  *  *  *
            7  *  *  *  *  *  *  *  *  *  *
            8  *  *  *  *  *  *  *  *  *  *
            9  *  *  *  *  *  *  *  *  *  *
    """

    def __init__(self, row_num: int, column_num: int) -> None:
        """Initialize Board class variables

        Args: 
            row_num (int): The number of rows of the board.
            column_num (int): The number of columns of the board.
        """
        r = row_num
        c = column_num
        # Make dataframe of board
        self.board = pd.DataFrame(
            [['*']*r]*c,
            index=list(range(0, r)),
            columns=list(range(0, c)),
        )

    def set_ship(
            self,
            orient: str,
            x: int,
            y: int,
            ship_symbol: str,
            ship_size: int,
            h_symbols: list,
            v_symbols: list
    ) -> bool:
        """Set ships on the board.

        This method is called only when placement boards are renewed.

        Args:
            orient (str): The orient indicating horizontal(H) or vertical(V)
            x (int): X conrdinate on the board.
            y (int): Y conrdinate on the board.
            ship_symbol (str): The symbol of ships specified in a config file.
            shop_size (str): The length of a ship to place.
            h_symbols (list): List of horizontal symbols like 'hori', 'horizont', etc...
            v_symbols (list): List of vertical symbols like 'vert', 'vertica', etc...
        """
        # When horizontal
        if orient in h_symbols:
            if y + ship_size > self.board.shape[1]:
                return False
            else:
                self.board.iloc[
                    x,
                    y:(y + ship_size)
                ] = ship_symbol

                return True

        # When vertical
        elif orient in v_symbols:
            if x + ship_size > self.board.shape[0]:
                return False
            else:
                self.board.iloc[
                    x:(x + ship_size),
                    y
                ] = ship_symbol
                return True

        else:
            raise ValueError(f'Non defined orient: {orient}')
