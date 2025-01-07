from NPC_Struct.base_attribute import AiCharacter
import GameInterface.ActionInterface as GameInterface
import concurrent.futures
import time
import traceback

class NpcMgr:
    _instance = None

    def manual_init(self, world):
        self.world = world
        self.npc_list = []
        self.npc_name_dict = {}

    def __new__(cls, world=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.world = world
        return cls._instance

    def add_npc(self, npc):
        self.npc_list.append(npc)
        self.npc_name_dict[npc.name] = npc

    def del_npc(self, npc):
        self.npc_list.remove(npc)
        del self.npc_name_dict[npc.name]

    def process_npc(self, npc):
        # debug
        # end
        start = time.perf_counter()
        npc.update_data()
        npc.wait_do_response()
        end = time.perf_counter()
        if end-start < 0.1:
            time.sleep(0.5)
        # npc.perception()
        # while npc.game_npc.game_npc_queue.unfinished_tasks > 0:# 等待 game 线程完成任务
        #     print("wait game thread", npc.name)
        #     time.sleep(0.5)

    def process_all_npcs(self, npc_list):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_npc, npc) for npc in npc_list]
            # 等待所有任务完成
            concurrent.futures.wait(futures)
            for future in futures:
                try:
                    result = future.result()  # 获取future的结果
                    # 处理结果
                except Exception as e:
                    traceback.print_exc()  # 打印详细的堆栈跟踪
                    print("!!!!!! 这里有一个报错", e)
            # 处理异常

    def update(self):
        self.process_all_npcs(self.npc_list)

    def create_npc(self, data, game_npc):
        new_npc = AiCharacter(data, game_npc, self.world)
        self.add_npc(new_npc)
        return new_npc

    def find_npc(self, name):
        return self.npc_name_dict[name]

    def init_data(self, data_list):
        data_list = data_list  # test
        self.world.target_game.find_npc(data_list[0]).init_Ai(data_list[0], False)
        for data in data_list[1:]:
            self.world.target_game.find_npc(data).init_Ai(data)

    def get_data(self):
        data_list = []
        for npc in self.npc_list:
            data_list.append(npc.get_data())
        return data_list

    def new_day(self):
        for npc in self.npc_list:
            npc.new_day()

def create_npc(data, game_npc):
    return NpcMgr().create_npc(data, game_npc)


def find_npc(name):
    return NpcMgr().find_npc(name)

def get_all_npc():
    return NpcMgr().npc_list