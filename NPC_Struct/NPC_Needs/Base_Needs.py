class BaseNeeds:
    def __init__(self, needs=None):
        self.needs = needs if needs else []

    def add_mem(self, need):
        if isinstance(need, list):
            self.needs += need
        else:
            self.needs.append(need)

    def change_mem(self, index, needs):
        self.needs[index] = needs

    def delete_mem(self, mem_or_index):
        if isinstance(mem_or_index, int):
            if mem_or_index < len(self.needs):
                del self.needs[mem_or_index]
        else:
            self.needs.remove(mem_or_index)

    def get_needs(self):
        return self.needs

    def get_string(self):
        re_string = "你的需求有:"
        for need in self.needs:
            re_string += (need.get_string()+".")