import Read_Data
import LLMApi
import json
import functools


def data_confirm_json(data):
    try:
        re_data = json.loads(data)
        return re_data
    except Exception as e:
        return False


def retry_if_none(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        while result is None:
            print("Result is None, retrying...")
            result = func(*args, **kwargs)
        return result

    return wrapper


@retry_if_none
def generate_daily_plan(data):
    Input_list = [data['dailytime'], data['now_day_done'], data['mem_list'], data['need_list'], data['background']]
    prompt = Read_Data.generate_prompt(Input_list, "daily_plan_v1.txt")
    data = LLMApi.GPT_request(prompt)
    prompt2 = Read_Data.generate_prompt(data, "semantic_decomposition_v1.txt")
    data2 = LLMApi.GPT_request(prompt2)
    re_data = data_confirm_json(data2)
    if re_data:
        return re_data

@retry_if_none
def generate_one_thing_plan(data):
    Input_list = [data['thing'], data['start_time'], data['end_time']]
    prompt = Read_Data.generate_prompt(Input_list, "event_segmentation_v1.txt")
    data = LLMApi.GPT_request(prompt)
    prompt2 = Read_Data.generate_prompt(data, "semantic_decomposition_v1.txt")
    data = LLMApi.GPT_request(prompt2)
    re_data = data_confirm_json(data)
    if re_data:
        return re_data

@retry_if_none
def generate_find_action(data):
    def confirm_data(re_data):
        return isinstance(re_data, list) and isinstance(re_data[0], bool)

    Input_list = [data['str'], data['action_list']]
    prompt = Read_Data.generate_prompt(Input_list, "find_action_v1.txt")

    data = LLMApi.GPT_request(prompt)
    print("generate_find_action", data)
    data = data_confirm_json(data)
    if confirm_data(data):
        return data[0], data[1]
    else:
        return False, "nothing"

@retry_if_none
def generate_find_object(data):
    # 当前你正在要做的事:! < INPUT
    # 0 >!
    # 当前你所在的地点:! < INPUT
    # 1 >!
    # 当前周围所存在的事物:! < INPUT
    # 2 >!

    def confirm_data(re_data):
        try:
            _ = data["furniture_list"][int(re_data) - 1]
            return True
        except:
            return False

    Input_list = [data['doing'], data['building'], data["furniture_list"]]
    prompt = Read_Data.generate_prompt(Input_list, "choose_object.txt")
    re_data = LLMApi.GPT_request(prompt)
    if confirm_data(re_data):
        return int(re_data) - 1
    else:
        return 0

@retry_if_none
def generate_text_about_object(data):
    def confirm_data(data):
        return True

    Input_list = [data['doing'], data['building'], data["furniture"]]
    prompt = Read_Data.generate_prompt(Input_list, "text_about_object.txt")
    data = LLMApi.GPT_request(prompt)
    if confirm_data(data):
        return data
    else:
        return "这东西感觉没什么作用"

@retry_if_none
def generate_choose_npc(data):
    def confirm_data(re_data):
        return re_data in data["person_list"]

    Input_list = [data['doing'], data['personality'], data["mem_list"], data["person_list"]]
    prompt = Read_Data.generate_prompt(Input_list, "choose_npc_v1.txt")
    re_data = LLMApi.GPT_request(prompt)
    if confirm_data(re_data):
        return re_data
    else:
        return data["person_list"][0]

@retry_if_none
def generate_choose_event(data):
    def confirm_data(data):
        return data in data["person_list"]

    Input_list = [data['doing'], data['personality'], data["mem_list"], data["event_list"]]
    prompt = Read_Data.generate_prompt(Input_list, "choose_event_v1.txt")
    data = LLMApi.GPT_request(prompt)
    if confirm_data(data):
        return prompt

@retry_if_none
def generate_react_to_npc(data):
    def confirm_data(re_data):
        re_data = data_confirm_json(re_data)
        if re_data and isinstance(re_data, list) and len(re_data) == 2 and re_data[0]:
            return re_data
        return False

    Input_list = [data['doing'], data['personality'], data["name"], data["mem"]]
    prompt = Read_Data.generate_prompt(Input_list, "react_to_npc_v1.txt")
    re_data = LLMApi.GPT_request(prompt)
    re_data = confirm_data(re_data)
    if re_data:
        return re_data[1]
    else:
        print("观察到了", data["name"], "但是不愿意讲话", re_data)
        return False

@retry_if_none
def generate_react_to_event(data):
    def confirm_data(data):
        return data in data["person_list"]

    Input_list = [data['doing'], data['personality'], data["mem_list"], data["event_list"]]
    prompt = Read_Data.generate_prompt(Input_list, "choose_event_v1.txt")
    data = LLMApi.GPT_request(prompt)
    if confirm_data(data):
        return prompt

@retry_if_none
def generate_chat_people(data):
    def confirm_data(re_data):
        content_list = data_confirm_json(re_data)
        if isinstance(content_list, list):
            for content in content_list:
                name = content.split(":")[0]
                if (name != data['person_name'] and name != data["other_name"]) or len(content.split(":")) < 2:
                    print(content_list, data['person_name'], data["other_name"])
                    return None
        return content_list

    Input_list = [data['doing'], data['person_name'], data["other_name"], data["person_mem"], data["other_mem"],
                  data["personaliy"], data["other_personality"], data['content']]
    prompt = Read_Data.generate_prompt(Input_list, "chat_people_v1.txt")
    re_data = LLMApi.GPT_request(prompt)
    re_data = confirm_data(re_data)
    if re_data:
        return re_data
    else:
        return None

@retry_if_none
def generate_thing_summary(data):
    def confirm_data(data):
        return True

    Input_list = [data['person_name'], data['content']]
    prompt = Read_Data.generate_prompt(Input_list, "thing_summary_v1.txt")
    if confirm_data(prompt):
        return prompt

@retry_if_none
def generate_semantic_sentence_dict(data):
    def confirm_data(data):
        data = data_confirm_json(data)
        if data and isinstance(data, dict):
            return data
        return False

    Input_list = [data['str']]
    prompt = Read_Data.generate_prompt(Input_list, "semantic_sentence_v1.txt")
    data = LLMApi.GPT_request(prompt)
    data = confirm_data(data)
    if data:
        return data
    else:
        return {}

@retry_if_none
def generate_reflect_memory(data):
    def confirm_data(data):
        data = data_confirm_json(data)
        if data and isinstance(data, dict):
            return data
        return False

    Input_list = [data['str'], data['person_name']]
    prompt = Read_Data.generate_prompt(Input_list, "Reflection/reflect_memory_v1.txt")
    data = LLMApi.GPT_request(prompt)
    data = confirm_data(data)
    if data:
        return data
    else:
        return {}

@retry_if_none
def choose_area_from_mem(data):
    def confirm_data(re_data):
        for loc_name in data['location_list']:
            if re_data.strip() == loc_name.strip():
                return loc_name
        return None

    Input_list = [data['location'], data['mem_list'], data['location_list']]

    prompt = Read_Data.generate_prompt(Input_list, "choose_area_from_mem_v1.txt")
    re_data = LLMApi.GPT_request(prompt)
    re_data = confirm_data(re_data)
    if re_data:
        return re_data
    else:
        return None

@retry_if_none
def chooose_build_from_map(data):
    def confirm_data(re_data):
        try:
            num = int(re_data)
            if num > len(data['build_name_list']):
                return None
            return num
        except:
            return None

    Input_list = [data['build_name'], data['location'], data['build_name_list']]

    prompt = Read_Data.generate_prompt(Input_list, "choose_build_to_move.txt")
    re_data = LLMApi.GPT_request(prompt)
    re_data = confirm_data(re_data)
    if re_data:
        if re_data == 0:
            return data['build_name']
        else:
            return data['build_name_list'][re_data - 1]
    else:
        return data['build_name']
