import datetime
import os

def distance(pos1, pos2):
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


ONY_DAY = 24 * 60 * 60
ONT_TIME = 10 * 60
ONE_GAME_TIME = 1

RESPONSE_TIME = 30*600 # 对同一事物的响应时间

Game_TICK_TIME = 60
AI_TICK_TIME = ONT_TIME

class CompontList:
    def __init__(self):
        self.components = []

    def __getattribute__(self, name):
        # Check if the attribute exists in the current object's __dict__
        if name in ['add_element', 'del_element', 'components']:
            return super().__getattribute__(name)
        # If the attribute does not exist, try to find the method in the components
        def method_proxy(*args, **kwargs):
            for component in self.components:
                if hasattr(component, name):
                    method = getattr(component, name)
                    if callable(method):
                        method(*args, **kwargs)

        return method_proxy

    def add_element(self, component):
        self.components.append(component)

    def del_element(self, component):
        self.components.remove(component)

def getDate(all_time, start_date):
    return all_time


from datetime import datetime, timedelta


def calculate_current_date(now_date, pass_time):
    start_date = datetime.strptime(now_date, "%Y-%m-%d %H:%M:%S")
    past_duration = timedelta(seconds=pass_time)
    current_date = start_date + past_duration
    return current_date

def is_same_day(data1, data2):
    data1 = datetime.strptime(data1, "%Y-%m-%d")
    data2 = datetime.strptime(data2, "%Y-%m-%d")
    return data1 == data2

def get_assets_path(path):
    current_path = os.path.dirname(__file__)
    return current_path + "/GameInterface/map_assets/" + path
# 使用示例
now_date = "2024-04-24 12:00:00"
pass_time = 375 * 3600  # 1小时（3600秒）
result = calculate_current_date(now_date, pass_time)
print(result)
