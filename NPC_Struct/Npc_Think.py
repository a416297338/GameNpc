import LLMInterface.Prompt_Code as Prompt_Code
import Base_Struct.Sentence as Sentence
import helper


class DalilyThink:
    def __init__(self, person):
        self.npc = person
        self.now_doing = None  # 当前正在执行的动作
        self.now_doing_end_time = None  # 当前正在执行的动作预估结束时间
        self.now_doing_start_time = None  # 当前正在执行的动作开始时间
        self.now_time = None  # 当前时间
        self.now_day_done = []  # 当天已经执行的动作
        self.now_day_plan_list = []  # 接下来计划列表

        self.now_doing_segment = []  # 当前事件的具体划分
        self.now_doing_idx = 0  # 做到了第几件事
        self.now_thing_data = None  #
        self.segment_thing_have_done = 0

    def daily_plan(self):
        def plan_next(dailytime, now_day_done, npc):
            mem_list, need_list = npc.get_dayilyinfluence()
            data = {'mem_list': mem_list, 'need_list': need_list, 'dailytime': dailytime, 'now_day_done': now_day_done,
                    'npc': npc, 'background': npc.get_base_information()}
            return Prompt_Code.generate_daily_plan(data)

        dailytime = self.npc.world.getDailyTime()
        if self.now_doing is None:
            if not self.now_day_plan_list:
                self.now_day_plan_list = plan_next(dailytime, self.now_day_done, self.npc)
            self.now_doing = Sentence.Sentence(self.now_day_plan_list[0])
            self.adjust_or_create_location()
            self.now_doing_start_time = self.now_doing.start_time
            self.now_doing_end_time = self.now_doing.end_time
            del self.now_day_plan_list[0]
        return self.now_doing

    def one_thing_plan(self):
        if not self.now_doing:
            return
        if not self.now_doing_segment or not self.now_doing_idx:
            data = {"thing": self.now_doing.get_string(), "start_time": self.now_doing.start_time,
                    "end_time": self.now_doing.end_time}
            self.now_doing_segment = Prompt_Code.generate_one_thing_plan(data)
            self.now_doing_idx = 0
        return Sentence.Sentence(self.now_doing_segment[self.now_doing_idx])

    def get_now_thing_data(self):
        return self.now_thing_data

    def set_now_thing_data(self, data):
        self.now_thing_data = data

    def one_thing_done(self):
        self.now_doing_idx += 1
        self.now_thing_data = None
        if self.now_doing_idx >= len(self.now_doing_segment):
            return True
        else:
            return False

    def daily_thing_done(self):
        self.now_day_done.append(self.now_doing)
        # clear now_doing
        self.now_doing = None
        self.now_doing_segment = None

    def adjust_or_create_location(self):
        re_mem = self.npc.find_mem_by_type("location", self.now_doing.location)
        if re_mem:
            mem_list = []
            location_list = []
            for mem in re_mem:
                mem_list.append(mem.get_string())
                location_list.append(mem.location)
            data = {'mem_list': mem_list, 'location_list': location_list, "location": self.now_doing.location}
            location = Prompt_Code.choose_area_from_mem(data)
            if location:
                print("在记忆中查找" + self.now_doing.location + "的结果是" + str(location))
                self.now_doing.location = location
                return location
        now_build_name = self.npc.getPosTile().building.name if self.npc.getPosTile().building else "空地"
        build_list = self.npc.world.buildingMgr.findNearBuidingByPos(None, self.npc.pos, 20)
        build_name_list = [build.name for build in build_list]
        data = {'build_name': now_build_name, 'build_name_list': build_name_list, 'location': self.now_doing.location}
        choose_build_name = Prompt_Code.chooose_build_from_map(data)
        if choose_build_name == "空地":  ## debug 特殊处理禁止选择空地
            choose_build_name = build_name_list[0]
        build = self.npc.world.buildingMgr.findNearBuidingByName(choose_build_name)
        # build = self.npc.world.buildingMgr.create_building(self.now_doing.location)
        location = build.getLocation()
        self.now_doing.location = location
        print("adjust_or_create_location", "我的" + str(self.now_doing.location) + "是" + build.name)
        data = {'str': "我的" + str(self.now_doing.location) + "是" + location, 'subject': str(self.now_doing.location),
                'verb': "是", 'object': location, 'location': location}
        mem_dict = {"SemanticMemory": Sentence.Create_Sentence(data)}
        self.npc.memoryMgr.add_mem_from_dict(mem_dict)

    def clear_daily_plan(self):
        self.now_doing = None
        self.now_day_plan_list = []

    def clear_day_done(self):
        self.now_day_done = []