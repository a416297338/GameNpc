import json
import os

current_path = os.path.dirname(__file__)

log_receive_data = {}


def save_receive_data(name, data):
    if name not in log_receive_data:
        log_receive_data[name] = []
    log_receive_data[name].append(data)


def read_data(file='data/person_data.json'):
    print(current_path + file)
    with open(current_path + "/" + file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def ReadAllData(load_path):
    re_data = {}
    if load_path: # test debug
        game_data = read_data(load_path)
        re_data = game_data
        re_data['person'] = read_data(game_data['file_name']['person'])
        re_data['memory'] = read_data(game_data['file_name']['memory'])
        re_data['record'] = read_data(game_data['file_name']['record'])
    else:
        re_data['person'] = read_data('data/person_data.json')
        re_data['memory'] = read_data('data/memory_data.json')
    return re_data


def SaveGameData(data, save_path):
    check_list = ['person', 'memory']
    file_name_dict = {}
    for name in check_list:
        if save_path:
            file_name_dict[name] = save_data(data[name], save_path[name], True)
        else:
            file_name_dict[name] = save_data(data[name], 'data/archive/' + name + '.json')
    return file_name_dict


def save_data(data, file_name, overwrite=False):
    if not file_name.endswith('.json'):
        file_name += '.json'
    file_name = current_path + "/" + file_name
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    base, extension = os.path.splitext(file_name)
    counter = 1
    if not overwrite:
        while os.path.exists(file_name):
            file_name = f"{base}_{counter}{extension}"
            counter += 1

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return file_name.split(current_path+"/")[1]


def save_gameplay_record(save_path):
    if save_path:
        return save_data(log_receive_data, save_path,True)
    else:
        return save_data(log_receive_data, 'data/record_data/ai_send_data.json')
