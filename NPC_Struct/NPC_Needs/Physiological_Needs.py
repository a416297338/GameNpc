from Base_Needs import BaseNeeds

# 基本生理需求 每个人都会有,例如 每天要吃饭,每天要喝水,每天要睡觉 每个NPC都必然会有
class PhysiologicalNeeds(BaseNeeds):
    def get_string(self):
        re_string = "你的基本生理需求有:"
        for need in self.needs:
            re_string += (need.get_string() + ".")

