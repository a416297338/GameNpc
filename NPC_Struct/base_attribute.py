import NPC_Memory.Memory_mgr as memory_mgr
import NPC_Needs.NeedsMgr as needs_mgr
import NPC_Personality
import Npc_Think
import living_building
import LLMInterface.Prompt_Code as Prompt_Code
import GameInterface.ActionInterface as ActionInterface
import NPC_AiAction.AiAction_Mgr as AiAction_Mgr
import NPC_AiAction.perception as perception
import queue
import random
import weakref


class BaseCharacter:
    def __init__(self, personMsg):
        self.id = id
        self.name = personMsg.get('name')  # 字符串
        self.age = personMsg.get('age')  # 数字
        self.sex = personMsg.get('sex')  # 字符串
        self.occupation = personMsg.get('occupation')  # 字符串
        self.religious = personMsg.get('religious')  # 字符串
        self.background = personMsg.get('background')  # 字符串
        self.belief = personMsg.get('belief')  # 字符串
        self.personality = NPC_Personality.Personality(self, personMsg.get('personality'))  # 字符串列表


class AiCharacter(BaseCharacter):
    def __init__(self, data, game_npc, world):
        super().__init__(data)
        self.world = world
        self.pos = data['pos'] if 'pos' in data else self.world.mapMgr.randomPos()
        self.location = self.world.mapMgr.getLocationByTilePos(self.pos)
        self.memoryMgr = memory_mgr.MemoryMgr(data.get("mem_dict", {}))
        self.needMgr = needs_mgr.NeedsMgr(data.get("mem_dict", {}))
        self.think = Npc_Think.DalilyThink(self)
        self.now_sight_tile = []
        self.now_sight_person = []
        self.now_sight_event = []
        self.dir = 0
        self.living_building = living_building.Npc_building()
        self.game_npc = game_npc
        self.now_thing = None
        self.now_thing_str = None
        self.ai_npc_queue = queue.Queue()

    def get_data(self):
        data_dict = {"name": self.name, "age": self.age, "sex": self.sex, "occupation": self.occupation,
                'religious': self.religious, 'background': self.background, 'belief': self.belief, 'pos': self.pos,
                'personality': self.personality.data_list,'mem_dict': self.memoryMgr.get_mem_data(), 'need_dict': self.needMgr.get_need_data()}
        filtered_dict = {key: value for key, value in data_dict.items() if value}
        return filtered_dict

    def perception(self):  # 观察周围
        self.now_sight_tile = perception.perception(self, self.world.mapMgr)

    def plan(self):  # 计划
        # 先大致计划出接下来的

        dailytime = self.world.getDailyTime()

        daily_thing = self.think.daily_plan()
        print(self.name, "plan")
        if dailytime < daily_thing.start_time and not (daily_thing.start_time > daily_thing.end_time):
            if not self.think.now_day_done:
                self.do_action("sleep", {"time": dailytime})
            self.now_thing_str = "没有什么事情做"
        elif daily_thing.location != self.location:
            print("###debug###", daily_thing.get_string(), "time:", dailytime, "location:", daily_thing.location)
            self.do_action("move", {"location": daily_thing.location, "string": daily_thing.get_string()})
            self.now_thing_str = "从"+ daily_thing.location+"去"+daily_thing.get_string()
        else:
            catch_data = self.think.get_now_thing_data()
            if catch_data:
                thing, data = catch_data
                self.do_action(thing, data)
            else:
                specific_thing = self.think.one_thing_plan()
                self.now_thing = specific_thing
                print("###debug### daily_thing", daily_thing.get_string(), "time:", dailytime)
                print("###debug### specific_thing", specific_thing.get_string())

                # data = {"str": specific_thing.get_string(), "action_list": ActionInterface.PERSON_ACTION_LIST}
                # find_suc, action = Prompt_Code.generate_find_action(data)
                build = self.world.buildingMgr.find_build_by_location(self.location)
                furniture_list = self.world.buildingMgr.find_furniture_in_build(build)
                furniture_list_name = [furniture.name for furniture in furniture_list]
                data = {"doing": specific_thing.get_string(), "building": build.name, "furniture_list": furniture_list_name}
                index = Prompt_Code.generate_find_object(data)
                furniture = furniture_list[index]
                data = {"doing": specific_thing.get_string(), "building": build.name, "furniture": furniture.name}
                generate_text = Prompt_Code.generate_text_about_object(data)
                send_data = {"target_pos": random.choice(furniture.tilePosList), "text": generate_text}
                self.do_action("choose_object", send_data)
                self.think.set_now_thing_data(("choose_object", send_data))
            if not self.now_thing.end_time or (dailytime >= self.now_thing.end_time and (
                    self.now_thing.end_time > self.now_thing.start_time or dailytime < daily_thing.start_time)):
                if self.think.one_thing_done():
                    self.think.daily_thing_done()

    def do_action(self, action, data):  # 执行动作
        result_str, total_time = AiAction_Mgr.do_action(self, action, data)
        if result_str:
            data = {"str": result_str, "start_time": self.world.get_now_time(), "location": data['location'],
                    "person_name": self.name}
            self.memoryMgr.construct_memory(data)

    def react_to_perception(self, npc_list, event_list):
        # 根据观察结果,做出反应, 优先于原先计划的动作
        if self.now_thing:
            now_doing_str = self.now_thing.get_string()
        else:
            now_doing_str = self.now_thing_str
        npc_name = None
        npc_mem = ""
        npc_dict = {}
        event_mem = ""
        event_dict = {}
        event_name = None
        re_data = {}
        for npc in npc_list:
            mem = self.find_mem_by_type("person", npc.name, True)
            npc_mem += mem
            npc_dict[npc.name] = [npc, mem]
        for event in event_list:
            mem = self.find_mem_by_type("event", event.name, True)
            event_mem += mem
            event_dict[event.name] = [event, mem]
        if len(npc_dict) >= 2:
            data = {'doing': now_doing_str, 'personality': self.personality.get_string(), 'mem_list': npc_mem, 'person_list': npc_dict.keys()}
            npc_name = Prompt_Code.generate_choose_npc(data)
        elif len(npc_dict) == 1:
            npc_name = list(npc_dict.keys())[0]
        if len(event_dict) >= 2:
            data = {now_doing_str, self.personality.get_string(), event_mem, event_dict.keys()}
            event_name = Prompt_Code.generate_choose_event(data)
        elif len(event_dict) == 1:
            event_name = list(event_dict.keys())[0]
        if npc_name:
            data = {'doing': now_doing_str, 'personality': self.personality.get_string(), 'name': npc_name, 'mem': npc_dict[npc_name][1]}
            chat_content = Prompt_Code.generate_react_to_npc(data)
            if chat_content:
                re_data['doing'], re_data['person_name'], re_data["other_name"], re_data["person_mem"], re_data[
                    "other_mem"], re_data[
                    "personaliy"], re_data["other_personality"], re_data[
                    'content'] = now_doing_str, self.name, npc_name, self.find_mem_by_type("person",
                                                                                                         npc_name), \
                    npc_dict[npc_name][0].find_mem_by_type("person", self.name), self.personality, npc_dict[npc_name][
                    0].personality, chat_content
                AiAction_Mgr.do_action(self, "chat_two", re_data)
                return True
        if event_name:
            pass
            # todo
        return False

    def get_dayilyinfluence(self):
        now_time = self.world.get_now_time()
        return self.memoryMgr.get_dayily_influence(now_time), self.needMgr.get_dayily_influence(now_time)

    def find_mem_by_type(self, type, name, to_string=False):
        return self.memoryMgr.find_mem_by_type(type, name, to_string)

    def get_base_information(self):
        msg_dict = {"年龄:": self.age, "性别:": self.sex, "职业": self.occupation, "宗教": self.religious,
                    "家庭背景": self.background, "信念": self.belief,
                    #"需求": self.needMgr.get_string()
                    }
        re_string = ""
        for key, vars in msg_dict.items():
            re_string += key + str(vars) + "."
        return re_string

    def update_data(self):
        self.pos = self.game_npc.tile_pos
        self.location = self.world.mapMgr.getLocationByTilePos(self.pos)

    def wait_do_response(self):
        # 等待处理Game响应请求
        # re: 是否执行了独立动作
        if self.ai_npc_queue.empty():
            return False
        while not self.ai_npc_queue.empty():
            thing, data = (self.ai_npc_queue.get())
            if thing == "plan":
                print("###debug### Ai plan")
                self.plan()
            if thing == "update_time":
                self.world.daily_time = data['daily_time']
                self.world.world_pass_time = data['world_pass_time']
            if thing == "view_all":
                self.react_to_perception(data['npc_list'], data['event_list'])
            self.ai_npc_queue.task_done()
        return False

    def wait_do_action(self):
        return self.game_npc.game_npc_queue.empty()

    def getPosTile(self):
        return self.world.mapMgr.tile[self.pos[0]][self.pos[1]]

    def new_day(self):
        self.think.clear_day_done()