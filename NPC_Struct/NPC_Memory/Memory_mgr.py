import Long_Memory, Prospective_Memory, Short_Memory, Sensory_Memory
import Base_Struct.Sentence as Sentence
import LLMInterface.Prompt_Code as Prompt_Code
import helper


# 记忆模型管理系统,采用Atkinson和Shiffrin的多存储记忆模型,性格属于记忆
class MemoryMgr:
    def __init__(self, data):
        self.sensoryMem = Sensory_Memory.SensoryMemory()
        self.shortMem = Short_Memory.ShortMemory()
        self.longMem = Long_Memory.LongMemory()
        self.prospectiveMem = Prospective_Memory.ProspectiveMemory()
        if data:
            self.add_mem_from_dict(data)


    def get_dayily_influence(self, now_time):
        return self.get_daily_memory(now_time) + self.get_mem_by_id_list(self.shortMem.get_mem())

    def get_daily_memory(self, time):
        re_mem = []
        for memId in self.prospectiveMem.get_mem():
            mem = Sentence.Get_Sentence(memId)
            if helper.is_same_day(time, mem.time):
                re_mem.append(mem)
        return re_mem

    def get_all_memeory(self):
        return self.get_mem_by_id_list(
            self.sensoryMem.get_mem() + self.shortMem.get_mem() + self.longMem.get_mem() + self.prospectiveMem.get_mem())

    def get_mem_by_id_list(self, list):
        return [Sentence.Get_Sentence(mem_id) for mem_id in list]

    def find_mem_by_type(self, type, name, to_string=False):
        re_mem = []
        if type == "person":
            for mem in self.get_all_memeory():
                if mem.object == name or mem.other_person == name:
                    re_mem.append(mem)
        if type == "location":
            for mem in self.get_all_memeory():
                if self.mem_is_same_place(mem.subject, name):
                    re_mem.append(mem)
        if to_string:
            re_str = ""
            for mem in re_mem:
                re_str += mem.get_string()
                re_str += "."
            return re_str
        else:
            return re_mem

    def add_mem_from_dict(self, mem_dict):
        for key, mem in mem_dict.items():
            if key == "ProspectiveMemory":
                self.prospectiveMem.add_mem(mem)
            if key == "SensoryMemory":
                self.sensoryMem.add_mem(mem)
            if key == "ShortMemory":
                self.shortMem.add_mem(mem)
            else:
                self.longMem.add_mem(mem, key)

    def construct_memory(self, data):
        return # test
        mem_dict_str = Prompt_Code.generate_reflect_memory(data)
        mem_dict_sentence = {}
        for key, value in mem_dict_str.items():
            data['type'] = key
            sentenceId = Sentence.Create_Sentence(data)
            Sentence.Update_Sentence_By_String(sentenceId, value)
            mem_dict_sentence[key] = sentenceId

        self.add_mem_from_dict(mem_dict_sentence)

    def mem_is_same_place(self, str1, str2):
        if not str1 or not str2:
            return False
        processed_string1 = ''.join(char for char in str1 if not char.isspace() and not char.isdigit())
        processed_string2 = ''.join(char for char in str2 if not char.isspace() and not char.isdigit())
        return processed_string2 == processed_string1

    def get_mem_data(self):
        re_data = {}
        for key in ["prospectiveMem", "sensoryMem", "shortMem"]:
            temp = getattr(self, key, None)
            data = temp.get_mem()
            if data:
                re_data[key] = data
        for key in ["ProceduralMemory", "SemanticMemory", "EpisodicMemory", "OpinionMemory"]:
            data = getattr(self.longMem, key, None)
            if data:
                re_data[key] = data

        return re_data


