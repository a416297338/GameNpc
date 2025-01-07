# AI与游戏相互处理系统,主要用来对接人物思考的结果在游戏中具体表现
from __future__ import absolute_import
from __future__ import print_function
PERSON_ACTION_LIST = ["move", "chat"]
PERSON_REACT_LIST = []

import GameInterface.Game_Main as Game_Main
import GameNpc
import time


def game_do_action(action, npc, game_data, callback):
    game_npc = npc.game_npc
    game_data["now_time"] = npc.world.get_now_time().strftime(
        "%Y-%m-%d %H:%M:%S")
    game_npc.game_npc_queue.put((action, game_data))


def chat(npc, content, callback):
    data = {}
    npc.game_npc_queue.put(("chat", data))


def move(npc, pos, callback):
    data = {"target_pos": pos}
    npc.game_npc_queue.put(("move", data))


# def init_data(data):
#     global PERSON_ACTION_LIST
#     PERSON_ACTION_LIST = data
#
# def get_data():
#     return {"action_list": PERSON_ACTION_LIST}


def find_npc(name):
    if name in Game_Main.GetNpcDict():
        return Game_Main.GetNpcDict()[name]
    else:
        Game_Main.Game().NpcDict[name] = GameNpc.NPC({})
        return Game_Main.GetNpcDict()[name]


def get_all_npc():
    return six_ex.values(Game_Main.GetNpcDict())


class GameNpcInterface:
    def __init__(self, game_character):
        self.game_character = game_character

    def move(self, pos):
        return self.game_character.move(pos)

    def chat_two(self, pos):
        return self.game_character.chat_two(pos)

    def do_action(self, action, data):
        method = getattr(self, action, None)
        # 如果方法存在,则调用它
        if method:
            method(data)
        else:
            print(f"Method '{action}' not found.")
