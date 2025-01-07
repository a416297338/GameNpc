from Base_Needs import BaseNeeds

# 自我实现需求,比较模糊,每个人都不相同,通常只有极少数NPC会持有
class TopNeeds(BaseNeeds):
    def get_string(self):
        re_string = "你当前的人生目标是: "
        for need in self.needs:
            re_string += (need.get_string() + ".")
