from Base_Needs import BaseNeeds

# 满足了安全需求之后,人们会追求友谊、亲情和爱情。这是对社交互动、群体归属和友谊的需求
class SocialNeeds(BaseNeeds):
    def get_string(self):
        re_string = "你的基本社会需求有:"
        for need in self.needs:
            re_string += (need.get_string() + ".")

