from datetime import datetime, timedelta
import LLMInterface.Prompt_Code as Prompt_Code


def calculate_current_date(now_date, pass_time):
    start_date = datetime.strptime(now_date, "%Y-%m-%d %H:%M:%S")
    past_duration = timedelta(seconds=pass_time)
    current_date = start_date + past_duration
    return current_date


SentenceDict = {}
SentenceId = 0


class Sentence:
    def __init__(self, data=None):
        self.str = None  # 句子内容
        self.start_time = None  # 时间
        self.end_time = None  # 时间
        self.location = None  # 地点
        self.subject = None  # 主语
        self.verb = None  # 谓语
        self.object = None  # 宾语
        self.sub_clause = None  # 从句
        self.predicative = None  # 表语
        self.type = None
        if data:
            self.init_sentence(data)

    def init_sentence(self, data):
        self.str = data.get('str')  # 句子内容
        self.start_time = data.get('start_time')  # 开始时间
        self.end_time = data.get('end_time')  # 结束时间
        self.location = data.get('location')  # 地点
        self.subject = data.get('subject')  # 主语
        self.verb = data.get('verb')  # 谓语
        self.object = data.get('object')  # 宾语
        self.sub_clause = data.get('sub_clause')  # 从句
        self.predicate = data.get('predicate')  # 表语
        self.other_person = data.get('other_person')  # 其他人
        self.type = data.get('type')  # 类型

    def get_sentence_data(self):
        return {
            'str': self.str,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'location': self.location,
            'subject': self.subject,
            'verb': self.verb,
            'object': self.object,
            'sub_clause': self.sub_clause,
            'predicate': self.predicate,
            'other_person': self.other_person,
            'type': self.type
        }

    def get_string(self):
        return self.str

    def get_action_data(self):
        return {'location': self.location, 'other_person': self.other_person}

    def get_during_time(self):
        time_format = '%H:%M'
        start_time = datetime.strptime(self.start_time, time_format)
        end_time = datetime.strptime(self.end_time, time_format)

        hour_difference = (end_time - start_time).seconds / 60
        return hour_difference


def Create_Sentence(data, Id=None):
    global SentenceId
    if Id:
        SentenceId = Id
    while (SentenceId in SentenceDict):
        SentenceId = SentenceId + 1
    SentenceDict[SentenceId] = Sentence(data)
    return SentenceId


def Get_Sentence(Id):
    return SentenceDict[Id]


def Update_Sentence_By_String(Id, string):
    SentenceDict[Id].str = string
    data = Prompt_Code.generate_semantic_sentence_dict({'str': string})
    SentenceDict[Id].init_sentence(data)


def Load_Sentences(data):
    for Id, sentence in data.items():
        Id = int(Id)
        SentenceDict[Id] = Sentence(sentence)


def Save_Sentences():
    re_data = {}
    for Id, Sentence in SentenceDict.items():
        re_data[Id] = Sentence.get_sentence_data()
    return re_data
