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

    def __init__(self, config_path: str) -> None:
        """Initialize Config class variables.

        Args:
            config_path (str): path to config file where rule of
                battleship game is written.
        """
        self.config_text = self.read_file(config_path)
        self.row_num = int(self.config_text[0])
        self.column_num = int(self.config_text[1])
        self.ship_dict = self.get_ship_info()

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
