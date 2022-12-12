class Config:
    def __init__(self, config_path):
        self.config_text = self.read_file(config_path)
        self.row_num = self.config_text[0]
        self.column_num = self.config_text[1]
        self.ship_dict = self.get_ship_info()

    def read_file(self, config_path):
        config_path = config_path.lstrip()
        with open(config_path, 'r') as f:
            config_file = f.read()

        config_text = [k for k in config_file.split('\n') if len(k) >= 1]
        return config_text

    def get_num_ships(self):
        stripped = self.config_text[2].lstrip().rstrip()
        num_ships = int(stripped)
        return num_ships

    def get_ship_info(self):
        ship_dict = {}
        for row in self.config_text[3:]:
            stripped = row.rstrip().lstrip().split(' ')
            ship_dict[stripped[0]] = int(stripped[1])

        return ship_dict
