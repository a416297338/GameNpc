from Base_Needs import BaseNeeds

# 尊重需求, 被尊重的需求,通常也是在前三个需求被满足后才会诞生
class EsteemNeeds(BaseNeeds):
    def get_string(self):
        re_string = "你当前的人生目标是: "
        for need in self.needs:
            re_string += (need.get_string() + ".")

