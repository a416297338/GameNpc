import NPC_AiAction
import GameInterface.ActionInterface as GameInterface
import NPC_Struct.Npc_Mgr as Npc_Mgr
import LLMInterface.Prompt_Code as Prompt_Code


def do_action(person, action, data, callback=None):
    print("do_action debug", action, data)
    if action == "chat_two":
        return chat_two(person, data, callback)
    elif action == "move":
        return move(person, data, callback)
    elif action == "sleep":
        return sleep(person, data, callback)
    elif action == "choose_object":
        return choose_object(person, data, callback)
    else :
        print("上面动作暂时没有实现")
        return None, 10

def sleep(person, data, callback):
    GameInterface.game_do_action("sleep", person, data, callback)

def choose_object(person, data, callback):
    GameInterface.game_do_action("choose_object", person, data, callback)
    return None, 10

def chat_two(person, data, callback):
    content_list = Prompt_Code.generate_chat_people(data)
    re_string = "与人进行了对话,聊天如下:"
    one_person = None
    two_person = None
    if not content_list:
        return None, 10
    for content in content_list:
        name = content.split(":")[0]
        npc = Npc_Mgr.find_npc(name)
        if one_person is None:
            one_person = npc
        elif npc != one_person:
            two_person = npc
            break
    one_person_chat_list = []
    two_person_chat_list = []
    for content in content_list:
        name = content.split(":")[0]
        content = content.split(":")[1]
        npc = Npc_Mgr.find_npc(name)
        if npc == one_person:
            one_person_chat_list.append(content)
        else:
            two_person_chat_list.append(content)
    data_one = {"person": two_person.game_npc.name, "text_list": one_person_chat_list, "time_list": [i * 60 for i in range(len(one_person_chat_list))]}
    data_two = {"person": one_person.game_npc.name, "text_list": two_person_chat_list, "time_list": [i * 60 for i in range(len(two_person_chat_list))]}
    GameInterface.game_do_action("chat_to", one_person, data_one, callback)
    GameInterface.game_do_action("chat_to", two_person, data_two, callback)
    data = {'person_name': person.name, 'content': content_list}
    re_string += Prompt_Code.generate_thing_summary(data)
    return re_string, 5


def move(person, data, callback):
    target_tile = person.world.buildingMgr.find_build_by_location(data['location']).centerTile
    game_data = {"target_pos": target_tile, "string": data['string']}
    GameInterface.game_do_action("move", person, game_data, callback)
    re_string = "从" + (person.location if person.location else "空地") + "移动到了" + data['location']
    return re_string, 10
