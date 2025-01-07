class Personality:
    def __init__(self, npc, data_list):
        self.npc = npc
        self.data_list = data_list

    def get_string(self):
        re_str = ""
        for idx, data in enumerate(self.data_list):
            re_str += "({0}): {1} ".format(idx, data)
        return re_str




