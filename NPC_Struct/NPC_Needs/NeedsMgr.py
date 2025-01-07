import Base_Needs, Esteem_Needs, Physiological_Needs, Safety_Needs, Social_Needs, Top_Needs
import Base_Struct.Sentence as Sentence


# 需求管理系统,采用亚伯拉罕·马斯洛(Abraham Maslow)的需求层次理论
class NeedsMgr:
    def __init__(self, need_dict=None):
        self.baseNeeds = Base_Needs.BaseNeeds()
        self.esteemNeeds = Esteem_Needs.EsteemNeeds()
        self.physiologicalNeeds = Physiological_Needs.PhysiologicalNeeds()
        self.safetyNeeds = Safety_Needs.SafetyNeeds()
        self.socialNeeds = Social_Needs.SocialNeeds()
        self.topNeeds = Top_Needs.TopNeeds()
        if need_dict:
            self.add_need_from_dict(need_dict)

    def add_need_from_dict(self, need_dict):
        for key, need in need_dict.items():
            if key not in ["baseNeeds", "esteemNeeds", "physiologicalNeeds", "safetyNeeds", "socialNeeds", "topNeeds"]:
                return
            temp = getattr(self, key, None)
            temp.add_mem(need)

    def get_dayily_influence(self, data):
        return self.baseNeeds.get_needs()

    def get_need_by_id_list(self, list):
        return [Sentence.Get_Sentence(mem_id) for mem_id in list]

    def get_string(self):
        needs_list = self.get_need_by_id_list(self.get_needs())
        return [need.get_string() for need in needs_list]

    def get_needs(self):
        return self.baseNeeds.get_needs() + self.esteemNeeds.get_needs() + self.physiologicalNeeds.get_needs() + self.safetyNeeds.get_needs() + self.socialNeeds.get_needs() + self.topNeeds.get_needs()

    def get_need_data(self):
        re_data = {}
        for key in ["baseNeeds", "esteemNeeds", "physiologicalNeeds", "safetyNeeds", "socialNeeds", "topNeeds"]:
            temp = getattr(self, key, None)
            data = temp.get_needs()
            if data:
                re_data[key] = data

        return re_data