class Npc_building:
    def __init__(self):
        self.Dict = {}

    def __getitem__(self, item):
        return self.Dict[item]

    def __setitem__(self, key, value):
        self.Dict[key] = value