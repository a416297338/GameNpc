from __future__ import absolute_import
import NPC_Struct.Npc_Mgr as Npc_Mgr
import map_mgr
import building_mgr
import time
import helper
import GameInterface.ActionInterface as ActionInterface
import GameData.read_data as read_data
import queue
import Base_Struct.Sentence as Sentence
Debug = False


class GameAI:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.target_game = None
        self.npcMgr = Npc_Mgr.NpcMgr(self)
        self.npcMgr.manual_init(self)
        self.frame = 0
        self.mapMgr = map_mgr.GameMap(None)
        self.buildingMgr = self.mapMgr.buildingMgr
        self.worldtime = 0
        self.start_time = "2024-01-01 00:00:00"
        self.world_pass_time = 0
        self.daily_time = helper.ONT_TIME * 6 * 8
        self.delta_time = 0
        self.ActionInterface = ActionInterface

    def run(self):
        # 游戏主循环
        self.world_pass_time = self.target_game.world_pass_time
        temp_time = self.daily_time
        self.daily_time = self.world_pass_time % helper.ONY_DAY
        self.npcMgr.update()
        if temp_time > self.daily_time:
            self.npcMgr.new_day()
        self.frame += 1
        # self.delta_time = time.perf_counter() - self.start_time
        #
        # # 计算当前帧率
        # frame_rate = 1 / self.delta_time
        #
        # # 打印每次执行的时间和当前帧率
        # if Debug:
        #     print(f"now frame {frame_rate:.2f} fps")

    def LoadData(self, load_path=None):
        data_dict = read_data.ReadAllData(load_path)
        if load_path:
            data_dict['file_name']['load_path'] = load_path
            self.target_game.load_data(data_dict)
        self.npcMgr.init_data(data_dict['person'])
        Sentence.Load_Sentences(data_dict['memory'])

    def SaveData(self, save_path=None):
        data_dict = {}
        data_dict['person'] = self.npcMgr.get_data()
        data_dict['memory'] = Sentence.Save_Sentences()
        return read_data.SaveGameData(data_dict, save_path)

    def get_npc_list(self):
        return self.npcMgr.npc_list

    def get_map(self):
        return self.mapMgr

    def update(self):
        # 更新游戏状态
        pass

    def render(self):
        # 渲染游戏画面
        pass

    def get_now_time(self):
        return helper.calculate_current_date(self.start_time,
                                             self.world_pass_time)

    def getDailyTime(self):
        return '{:02d}'.format(
            int(self.daily_time) // 3600) + ":" + '{:02d}'.format(
                int(self.daily_time) // 60 % 60)


def GetAiWorld():
    return GameAI()


def GetWorldMap():
    return GameAI().mapMgr


def GetDailyTime():
    return GetAiWorld().daily_time


def start_game(target_game, load_path=None):
    Game = GameAI()
    Game.target_game = target_game  # 指向游戏对象
    Game.LoadData(load_path)
    return Game


def run():
    GameAI().run()


def is_start_game():
    return GameAI._instance != None
