import copy

import NPC_Struct.Npc_Mgr as Npc_Mgr
import NPC_AiAction.perception as perception
import queue
import arcade
import UIcomponent
import helper
import time
import read_data


# 模拟游戏里的NPC
def distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def direction(vector1, vector2):
    diff_vector = [vector2[0] - vector1[0], vector2[1] - vector1[1]]
    magnitude = (diff_vector[0] ** 2 + diff_vector[1] ** 2) ** 0.5
    if magnitude != 0:
        direction = (diff_vector[0] / magnitude, diff_vector[1] / magnitude)
    else:
        direction = (0, 0)
    return direction


def add(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])


def mul(vector1, scale):
    return (vector1[0] * scale, vector1[1] * scale)


class NPC:
    def __init__(self):
        self.name = None  # 暂时用来做唯一标记
        self.speed = 5
        self.game_npc_queue = queue.Queue()
        self.thing_timer = 0
        self.game_map = None
        self.target_pos = None
        self.quick_tick = True  # 用来标记当前是否,可以快速tick
        self.thing_dict = {}
        self.time_dict = {}
        self.AiComponent = None
        self.need_think = True

        self.offline_event_list = []
        self.offline_event_index = 0

        #Game Data
        self.target_path_list = []

    def init_Ai(self, AiData, need_think=True):

        self.AiComponent = Npc_Mgr.create_npc(AiData, self)
        self.ai_npc_queue = self.AiComponent.ai_npc_queue
        self.done_set = set()  # 标记已经处理过的消息
        self.need_think = need_think

    def tick(self, time, online=True, think_flag=False):
        self.do_time_func()
        self.receive_msg(online)
        if think_flag and self.need_think:
            self.prospective(time)

    def receive_msg(self, online=True):
        if online:
            while not self.game_npc_queue.empty():
                thing, data = self.game_npc_queue.get()
                record_data = copy.copy(data)
                if self.game_map and self.game_map.world:
                    record_data['frame'] = self.game_map.world.frame
                    read_data.save_receive_data(self.name, (thing, record_data))
                if self.do_thing(thing, record_data):  # 立即完成事件
                    self.game_npc_queue.task_done()
                else:  # 后续完成事件
                    break
        else:
            if self.offline_event_index >= len(self.offline_event_list):
                return
            thing, data = self.offline_event_list[self.offline_event_index]
            if data['now_time'] <= str(self.game_map.world.now_time):
                self.game_npc_queue.put((None))
                self.do_thing(thing, data)
                self.offline_event_index += 1

    def doing_thing(self):
        return self.thing_dict

    def do_time_func(self):
        keys_to_delete = []
        for end_time, func in self.time_dict.items():
            if end_time < self.game_map.world.world_pass_time:
                print("thing done")
                func()
                keys_to_delete.append(end_time)

        for end_time in keys_to_delete:
            del self.time_dict[end_time]

    def send_msg(self, msg, data):
        self.ai_npc_queue.put((msg, data))

    def clear_ai_data(self):
        self.done_set = set()  # 标记已经处理过的消息

    def call_delay(self, func, delay_time=0.5):
        self.time_dict[self.game_map.world.world_pass_time + delay_time] = func

    def prospective(self, time):
        if not self.AiComponent:
            return
        # self.now_sight_tile = perception.perception(self, self.AiComponent.world.mapMgr)
        # send_data = {'npc_list':[], 'event_list':[]}
        # for tile in self.now_sight_tile:
        #     if tile.npc and tile.npc not in self.done_set:
        #         self.done_set.add(tile.npc)
        #         send_data['npc_list'].append(tile.npc)
        #     if tile.event and tile.event not in self.done_set:
        #         self.done_set.add(tile.event)
        #         send_data['event_list'].append(tile.event)
        npc_list = self.game_map.get_all_npc()
        send_data = {'npc_list': [], 'event_list': []}
        for npc in npc_list:
            if npc == self:
                continue
            if distance(self.tile_pos, npc.tile_pos) < 5:
                if npc not in self.done_set:
                    self.done_set.add(npc)
                    npc.done_set.add(self)
                    send_data['npc_list'].append(npc.AiComponent)
        if send_data['npc_list'] or send_data['event_list']:
            self.send_msg("view_all", send_data)
        if not self.target_path_list and not self.thing_dict and self.game_npc_queue.unfinished_tasks == 0:
            print("###debug send plan")
            self.send_msg("plan", {})

    def do_thing(self, thing, data):
        pass


class PlayerNpc(arcade.Sprite, NPC):
    def __init__(self, game_map, data, sprite_path='cute_rpg_word_VXAce/characters/!Character_RM_001.png'):
        super().__init__()
        NPC.__init__(self)
        # 加载 sprite sheet
        pos = data['pos']
        self.name = data['name']
        self.game_map = game_map
        sprite_path = helper.get_assets_path(sprite_path)
        self.textures = arcade.load_spritesheet(
            sprite_path,  # 替换为你的 sprite sheet 路径
            sprite_width=48,  # 每个帧的宽度
            sprite_height=48,  # 每个帧的高度
            columns=12,  # sprite sheet 中的列数
            count=48  # 总帧数
        )
        self.radius = 48
        self.highLight = [0, 3, 6, 9]
        self.moveForward = {"down": 0, "left": 12, "right": 24, "up": 36}
        self.moveState = "down"
        # 设置初始帧
        pos = self.game_map.findNoCoillison(pos)
        pos = self.game_map.getPosFromTile(pos)
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.target_pos = None
        self.target_person = None
        self.target_path_list = []
        self.current_frame = 0
        self.speed = 5
        self.move_key_set = set()
        self.anim_speed = 10
        self.update_animation()

        self.cross_wall = True
        self.move_able = True
        image_path = helper.get_assets_path("network/chat.png")

        self.dialogue_box = UIcomponent.DialogueBox(image_path)
        self.dialogue_box.set_text("观测npc")

    def is_clicked(self, x, y):
        # 检查点击位置是否在角色的圆形范围内
        if (x - self.center_x) ** 2 + (y - self.center_y) ** 2 <= self.radius ** 2:
            self.chat("my name is" + self.name)
        return (x - self.center_x) ** 2 + (y - self.center_y) ** 2 <= self.radius ** 2

    def update_animation(self, delta_time: float = 1 / 60):
        # 更新帧
        if self.change_x != 0:
            self.moveState = "left" if self.change_x < 0 else "right"
        elif self.change_y != 0:
            self.moveState = "down" if self.change_y < 0 else "up"
        anim_frame = int(self.current_frame * delta_time * self.anim_speed)
        self.current_frame += 1
        isMove = self.change_x != 0 or self.change_y != 0
        self.set_texture(self.get_frame_index(self.moveState) + (anim_frame % 3 if isMove else 1))

    def get_frame_index(self, direction, highlight=0):
        return self.moveForward[direction] + self.highLight[highlight]

    def on_update(self, delta_time: float = 1 / 60):
        if not self.move_able:
            return
        if self.controll_by_person():
            self.target_pos = None
            self.target_path_list = []
        if self.target_person:
            pos_list = self.game_map.find_path(self.tile_pos, self.target_person.tile_pos)
            self.target_path_list = pos_list[1:]
        if self.target_path_list:
            if self.move_to(self.target_path_list[0]):
                del self.target_path_list[0]
        else:
            last_center_x = self.center_x
            last_center_y = self.center_y
            self.center_x += self.change_x * delta_time * 60
            self.center_y += self.change_y * delta_time * 60
            self.center_x = min(max(self.center_x, self.width / 2), self.game_map.map_width - self.width / 2)
            self.center_y = min(max(self.center_y, self.height / 2), self.game_map.map_height - self.height / 2)
            if not self.cross_wall and self.check_collision():
                self.center_x = last_center_x
                self.center_y = last_center_y
        self.update_animation()
        self.clear_move()
        self.update_thing()  # 处理事件

    def update(self):
        print("update")

    def update_thing(self):  # 处理事件
        def delayed_chat(text, delay):
            def task():
                self.chat(text, 100)

            print(text, delay)
            self.call_delay(task, delay)

        thing, data = self.get_most_important_thing()
        thing_done = False
        if thing == "choose_object":
            if self.tile_pos[0] == data['target_pos'][0] and self.tile_pos[1] == data['target_pos'][1]:
                self.dialogue_box.set_text(data["text"])
                self.call_delay(lambda: self.game_npc_queue.task_done(), 60*5)
                thing_done = True
            else:
                if not self.target_path_list:# 意外情况阻断,重新寻路过去
                    self.target_to_pos(data['target_pos'])
        if thing == "chat_to":
            if distance(self.tile_pos, self.target_person.tile_pos) < 4:
                print("chat_to")
                if self.tile_pos[0] < self.target_person.tile_pos[0]:
                    down_flag = True
                self.target_person = None
                self.target_pos = None
                self.target_path_list = []
                chat_time = 0
                for idx in range(len(data["text_list"])):
                    chat_text = data["text_list"][idx]
                    chat_time = data["time_list"][idx]
                    delayed_chat(chat_text, chat_time)
                self.move_able = False
                def chat_end():
                    self.game_npc_queue.task_done()
                    self.move_able = True
                self.call_delay(chat_end, chat_time + 60)
                thing_done = True
        if thing_done:
            del self.thing_dict[thing]

    def get_most_important_thing(self):
        thing = None
        data = None
        for thing, data in self.thing_dict.items():
            if thing == "chat_to":
                return thing, data
        return thing, data

    def controll_by_person(self):
        # move
        if arcade.key.UP in self.move_key_set:
            self.moveState = 'up'
            self.change_y = self.speed
        elif arcade.key.DOWN in self.move_key_set:
            self.moveState = 'down'
            self.change_y = -self.speed
        elif arcade.key.LEFT in self.move_key_set:
            self.moveState = 'left'
            self.change_x = -self.speed
        elif arcade.key.RIGHT in self.move_key_set:
            self.moveState = 'right'
            self.change_x = self.speed
        else:
            return False
        return True

    def clear_move(self):
        self.change_y = 0
        self.change_x = 0

    def move_left(self):
        self.change_x = -self.speed

    def move_right(self):
        self.change_x = self.speed

    def move_up(self):
        self.change_y = self.speed

    def move_down(self):
        self.change_y += -self.speed

    def key_down(self, key):
        self.move_key_set.add(key)

    def key_release(self, key):
        self.move_key_set.discard(key)

    def move_to(self, tile_pos):
        pos = self.game_map.getPosFromTile(tile_pos)
        diff_x = pos[0] - self.center_x
        diff_y = pos[1] - self.center_y
        arrive = True
        if abs(diff_x) < self.speed:
            self.change_x = diff_x
        else:
            arrive = False
            self.change_x = self.speed * (-1 if diff_x < 0 else 1)
        if abs(diff_y) < self.speed:
            self.change_y = diff_y
        else:
            arrive = False
            self.change_y = self.speed * (-1 if diff_y < 0 else 1)
        self.center_x += self.change_x
        self.center_y += self.change_y

        return arrive

    def target_to_person(self, person):
        self.target_person = person
        pos_list = self.game_map.find_path(self.tile_pos, person.tile_pos)
        self.target_path_list = pos_list[1:]

    def target_to_pos(self, target_pos):
        self.target_pos = target_pos
        pos_list = self.game_map.find_path(self.tile_pos, target_pos)
        # draw debug
        # for pos in pos_list:
        #
        #     # 创建一个白色方块
        #     white_square = arcade.SpriteSolidColor(50, 50, arcade.color.WHITE)
        #     # 设置方块的位置
        #     pos = self.game_map.getPosFromTile(pos)
        #     white_square.center_x = pos[0]  # X 轴位置
        #     white_square.center_y = pos[1]  # Y 轴位置
        #     # 将方块添加到 SpriteList 中
        #     self.game_map.scene.add_sprite("TopLayer", white_square)
        # end debug
        self.target_path_list = pos_list[1:]

    def stop(self):
        self.change_x = 0
        self.change_y = 0

    def check_collision(self):
        return arcade.check_for_collision_with_list(self, self.game_map.collision_list)

    def chat(self, text, duration_time=100, down_flag=False):
        self.dialogue_box.set_text(text, duration_time, down_flag)

    def do_thing(self, thing, data):
        if thing == "move":
            self.target_to_pos(data["target_pos"])
            self.chat(data["string"])
            self.game_npc_queue.task_done()
            return False
        if thing == "chat_to":
            if not self.target_person:
                print("chat_to start")
                npc = self.game_map.world.find_npc({'name': data["person"]}, False)
                self.target_to_person(npc)
                self.thing_dict[thing] = data
                return False
        if thing == "choose_object" and thing not in self.thing_dict:
            self.target_to_pos(data["target_pos"])
            self.thing_dict[thing] = data
            return False
        if thing == "sleep":
            self.chat("睡觉中zzzzzz")
            self.game_npc_queue.task_done()
        return True

    def draw(self, *, filter=None, pixelated=None, blend_function=None):
        print("12345")
        """
        Draw the sprite.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.
        :param pixelated: ``True`` for pixelated and ``False`` for smooth interpolation.
                          Shortcut for setting filter=GL_NEAREST.
        :param blend_function: Optional parameter to set the OpenGL blend function used for drawing the sprite list,
                               such as 'arcade.Window.ctx.BLEND_ADDITIVE' or 'arcade.Window.ctx.BLEND_DEFAULT'
        """

        if self._sprite_list is None:
            from arcade import SpriteList

            self._sprite_list = SpriteList()
            self._sprite_list.append(self)

        self._sprite_list.draw(filter=filter, pixelated=pixelated, blend_function=blend_function)

    @property
    def tile_pos(self):
        return self.game_map.getTileFromPos(self.center_x, self.center_y)

    def set_tile_pos(self, pos):
        pos = self.game_map.getPosFromTile(pos)
        self.center_x = pos[0]
        self.center_y = pos[1]
