class BaseMemory():
    def __init__(self, mem_list=None):
        self.mem = mem_list if mem_list else []

    def add_mem(self, mem, type=None):
        if isinstance(mem, list):
            self.add_mems(mem)
        else:
            self.mem.append(mem)

    def add_mems(self, mem_list):
        self.mem += mem_list

    def change_mem(self, index, mem):
        self.mem[index] = mem

    def delete_mem(self, mem_or_index):
        if isinstance(mem_or_index, int):
            if mem_or_index < len(self.mem):
                del self.mem[mem_or_index]
        else:
            self.mem.remove(mem_or_index)

    def get_mem(self):
        return self.mem
