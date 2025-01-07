from Base_Memory import BaseMemory


def isSkill(mem):
    return False


def isSemantic(mem):
    return False


def isEpisodic(mem):
    return False

# 长期记忆,这里分为了几个模块,分别是
# ProceduralMemory 程序记忆 如 会做饭,会修车等技能,或者后续一些行为习惯,早上八点起床,每天洗澡,一周倒一次垃圾
# SemanticMemory 语义记忆,主要存放知识概念类记忆,银行可以帮你保管财产,图书馆不得大声说话,父母会在你困难时提供帮助,房子123是我家
# EpisodicMemory 情景记忆, 比如1月20日 去了一家餐厅吃了一顿豪华的午餐,2月20日,参加了一场盛大的晚会,2月21日 与朋友在学校发生了激烈的争吵
# OpinionMemory 观点记忆,这一类本身属于语义记忆,但做区分,上一类主要是规则知识,这一类主要更偏向于个人主人主观观点,比如 小明是一个不诚信的人, 咖啡不好喝,某家餐厅不好吃
class LongMemory(BaseMemory):
    def __init__(self, mem_list=None):
        super().__init__(mem_list)
        self.ProceduralMemory = []
        self.SemanticMemory = []
        self.EpisodicMemory = []
        self.OpinionMemory = []

    def add_mems(self, mem_list):
        super().add_mem(mem_list)
        self.seg_mem(mem_list)

    def add_mem(self, mem, type=None):
        if type not in ["ProceduralMemory", "SemanticMemory", "EpisodicMemory", "OpinionMemory"]:
            return
        temp = getattr(self, type, None)
        if isinstance(mem, list):
            temp = temp+mem
        elif isinstance(mem, int):
            temp.append(mem)
        setattr(self, type, temp)


    def seg_mem(self, mem_list):
        for mem in mem_list:
            if isSkill(mem):
                self.ProceduralMemory += mem
            elif isSemantic(mem):
                self.SemanticMemory += mem
            elif isEpisodic(mem):
                self.EpisodicMemory += mem

    def get_mem(self):
        return self.ProceduralMemory + self.SemanticMemory + self.EpisodicMemory + self.OpinionMemory
