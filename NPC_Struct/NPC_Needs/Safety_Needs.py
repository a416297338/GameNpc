from Base_Needs import BaseNeeds

# 安全需求 这包括身体健康,稳定的工作,稳定的生活环境 生理需求基本满足后才会诞生
class SafetyNeeds(BaseNeeds):
    def get_string(self):
        re_string = "你的基本安全需求有:"
        for need in self.needs:
            re_string += (need.get_string() + ".")

