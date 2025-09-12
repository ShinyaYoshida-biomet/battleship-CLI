# -*- coding: utf-8 -*-
"""Config module to read config file.

Example:
    config = Config([path to your config file])
    print(config.config_text)
"""


class Config:
    """Config class of battleship game.

    Config is an object retaining information written in config file.
    The game of battleship is executed under rules following the config.
    """

    def __init__(self, config_path: str = None, **kwargs) -> None:
        """Initialize Config class variables.

        Args:
            config_path (str, optional): path to config file where rule of
                battleship game is written. If None, uses kwargs or defaults.
            **kwargs: CLI configuration options including:
                - board_size: tuple of (rows, cols)
                - ships: dict of ship_name: ship_size
        """
        if config_path:
            # File-based configuration (legacy mode)
            self.config_text = self.read_file(config_path)
            self.row_num = int(self.config_text[0])
            self.column_num = int(self.config_text[1])
            self.ship_dict = self.get_ship_info()
        else:
            # CLI-based configuration
            board_size = kwargs.get('board_size', (10, 10))
            self.row_num = board_size[0]
            self.column_num = board_size[1]
            
            # Default ships if none provided
            default_ships = {
                'C': 5,  # Carrier
                'B': 4,  # Battleship
                'D': 3,  # Destroyer
                'S': 3,  # Submarine
                'P': 2   # Patrol boat
            }
            self.ship_dict = kwargs.get('ships', default_ships)
            
            # Create config_text for compatibility with existing code
            self.config_text = self._generate_config_text()

    def read_file(self, config_path: str) -> str:
        """Function to read config file.

        Args: 
            config_path (str):  path to config file where rule of
                battleship game is written.

        Returns:
            config_text (str): What is written in config file.
        """
        config_path = config_path.lstrip()
        with open(config_path, 'r') as f:
            config_file = f.read()

        # Eliminate 0 length rows like only '\n'
        config_text = [k for k in config_file.split('\n') if len(k) >= 1]
        return config_text

    def get_num_ships(self):
        """Function to get the number of ships

        Args:

        Returns:
            num_ships (int): The number of ships written in config file.
        """
        stripped = self.config_text[2].lstrip().rstrip()
        num_ships = int(stripped)
        return num_ships

    def get_ship_info(self) -> dict:
        """Function to get the information(name and size) of ships.

        Args: 

        Returns: 
            ship_dict (dict): The information retaining name and size of ships.
        """

        ship_dict = {}
        # Ship information is written from the 3rd lines.
        for row in self.config_text[3:]:
            stripped = row.rstrip().lstrip().split(' ')
            ship_dict[stripped[0]] = int(stripped[1])

        return ship_dict

    def _generate_config_text(self) -> list:
        """Generate config text from CLI parameters for compatibility.
        
        Returns:
            list: Config text lines compatible with file-based format.
        """
        config_lines = [
            str(self.row_num),
            str(self.column_num),
            str(len(self.ship_dict))
        ]
        
        for ship_name, ship_size in self.ship_dict.items():
            config_lines.append(f"{ship_name} {ship_size}")
            
        return config_lines
