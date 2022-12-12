# -*- coding: utf-8 -*-
"""Board module called in player instance.

Example:
    board = Board(5, 5)
    board.board()
"""

import pandas as pd


class Board:
    def __init__(self, row_num, column_num):
        r = int(row_num)
        c = int(column_num)
        self.board = pd.DataFrame(
            [['*']*r]*c,
            index=list(range(0, r)),
            columns=list(range(0, c)),
        )

    def set_ship(self, orient, x, y, ship_symbol, ship_size):
        if orient == 'H':
            self.board.iloc[
                x,
                y:(y + ship_size)
            ] = ship_symbol

        elif orient == 'V':
            self.board.iloc[
                x:(x + ship_size),
                y
            ] = ship_symbol
