import helper
import GameNpc
import threading
import arcade
import map_mgr
import read_data
from datetime import datetime, timedelta

from pyglet.math import Vec2
import time
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tiled Map with Scrolling Example"

class MyGame(arcade.Window):
    _instance = None
    _initialized = False

    def __new__(cls):
        print(cls._initialized)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.collision_list = None
        arcade.set_background_color(arcade.color.AMAZON)

        self.game_map = None
        self.scene = None
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_sprite_list = []
        self.map_width = 0
        self.map_height = 0
        self.tile_dict = {}
        if self._initialized:
            return
        self._initialized = True
        self.NpcDict = {}
        self.frame = 0
        self.start_time = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.last_think_time = self.start_time
        self.think_time_interval = 10
        self.world_pass_time = 8 * 3600
        self.now_time = None
        self.delta_time = 0
        self.is_control_by_ai = True
        self.world_speed = 20
        self.spawning_by_map = False
        self.save_file_name = None

    def update(self, delta_time):
        pass

    def setup(self, map_file, control_by_ai=True):
        # Load the Tiled map
        self.game_map = map_mgr.GameMap(map_file, self)
        self.scene = self.game_map.scene
        self.map_width = self.game_map.map_width
        self.map_height = self.game_map.map_height
        self.is_control_by_ai = control_by_ai
        self.now_time = self.start_time

        if not self.is_control_by_ai:
            self.ai_offline_event_data = read_data.read_data('data/record_data/ai_send_data_102.json')
        #self.on_resize(SCREEN_WIDTH * 4, SCREEN_HEIGHT * 4)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.resize(width, height)
        # self.update_camera_zoom()

    def update_camera_zoom(self):
        # 计算缩放比例
        scale_x = self.width / SCREEN_WIDTH
        scale_y = self.height / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)
        self.camera.scale = scale


    def on_draw(self):
        arcade.start_render()

        self.camera.use()
        self.scene.draw()

        player_sprite_list_old = []
        sort_list = sorted(self.player_sprite_list, key=lambda x: x.center_y)
        for player_sprite in sort_list:
            draw_x = player_sprite.center_x
            draw_y = player_sprite.center_y
            for pos in player_sprite_list_old:
                if abs(draw_y-pos[1]) < 48 and abs(draw_x-pos[0])<200:
                    draw_y += 96
            player_sprite_list_old.append((draw_x, draw_y))
            player_sprite.dialogue_box.draw(draw_x, draw_y)

        # 在屏幕上绘制时间
        arcade.draw_text(f"Time: {self.now_time}", self.camera.position[0] + 10,
                         self.camera.position[1] + self.camera.viewport_height - 30, arcade.color.WHITE, 14)

        # 绘制对话框
        # 绘制人物对话框

    def find_npc(self, data, create=True):
        lock = threading.Lock()
        name = data['name']
        with lock:
            if name in self.NpcDict:
                return self.NpcDict[name]
            else:
                if create:
                    self.NpcDict[name] = self.create_npc(data)
                    return self.NpcDict[name]
                else:
                    return None

    def create_npc(self, data):
        new_npc = GameNpc.PlayerNpc(self.game_map, data)
        if not self.save_file_name:
            new_pos = self.game_map.spawning_blocks_list[len(self.player_sprite_list)]
            new_npc.set_tile_pos(new_pos)

        self.player_sprite_list.append(new_npc)
        self.scene.add_sprite("Player", new_npc)
        if not self.is_control_by_ai:
            if new_npc.name in self.ai_offline_event_data:
                new_npc.offline_event_list = self.ai_offline_event_data[new_npc.name]
                new_npc.speed *= self.world_speed/20

        return new_npc

    def on_update(self, tick_time):
        tick_time = 0.3 if tick_time > 0.3 else tick_time
        pause = False # 是否暂停Game线程
        think_flag = False
        for Npc in self.NpcDict.values():
            if Npc.ai_npc_queue and Npc.ai_npc_queue.unfinished_tasks > 0:  # 等待 Ai 线程完成任务
                pause = True
                break
        if not pause:
            if self.is_control_by_ai and ((self.now_time - self.last_think_time).total_seconds() > self.think_time_interval):
                think_flag = True
                self.last_think_time = self.now_time
            self.world_pass_time += (tick_time*self.world_speed)
            self.now_time = self.start_time + timedelta(seconds=(int(self.world_pass_time)))
            self.frame += 1
            for Npc in self.NpcDict.values():
                if self.is_control_by_ai:
                    if self.frame % 6000 == 0:
                        Npc.clear_ai_data()
                    # if self.daily_time % helper.ONT_TIME == 0:
                    #     Npc.send_msg("plan", {})
                    Npc.tick(time, think_flag=think_flag)
                else:
                    Npc.tick(self.now_time, False)
            # Update player position
            for player_sprite in self.player_sprite_list:
                player_sprite.on_update(tick_time)
        # Scroll the camera to follow the player
        self.scroll_to_player()

    def get_sprite_tiled(self, sprite):
        grid_x = int(sprite.center_x // self.tile_map.tile_width)
        grid_y = int(sprite.center_y // self.tile_map.tile_height)
        return (grid_x, grid_y)

    def get_layer_tiled_list(self, layer_name):
        sprite_list = self.tile_map.sprite_lists.get(layer_name)
        re_list = []
        for sprite in sprite_list:
            grid_x = int(sprite.center_x // self.tile_map.tile_width)
            grid_y = int(sprite.center_y // self.tile_map.tile_height)
            grid_position = (grid_x, grid_y)
            re_list.append(grid_position)

        return re_list

    def scroll_to_player(self):
        # Calculate the desired position of the camera
        target_x = self.player_sprite_list[0].center_x - self.camera.viewport_width / 2
        target_y = self.player_sprite_list[0].center_y - self.camera.viewport_height / 2

        # Ensure the camera doesn't scroll beyond the map boundaries
        if target_x < 0:
            target_x = 0
        elif target_x > self.game_map.width * self.game_map.tile_width - self.camera.viewport_width:
            target_x = self.game_map.width * self.game_map.tile_width - self.camera.viewport_width

        if target_y < 0:
            target_y = 0
        elif target_y > self.game_map.height * self.game_map.tile_height - self.camera.viewport_height:
            target_y = self.game_map.height * self.game_map.tile_height - self.camera.viewport_height
        # Move the camera to the target position
        self.camera.move_to(Vec2(target_x, target_y), speed=0.1)

    def on_key_press(self, key, modifiers):
        self.player_sprite_list[0].key_down(key)
        if key == arcade.key.SPACE:

            sprite_list = self.tile_dict[self.get_sprite_tiled(self.player_sprite)]
            for sprite in sprite_list:
                sprite.visible = False

    def on_key_release(self, key, modifiers):
        self.player_sprite_list[0].key_release(key)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        当鼠标按下时调用此函数。
        :param x: 鼠标的x坐标
        :param y: 鼠标的y坐标
        :param button: 鼠标按钮（1为左键,4为右键）
        :param modifiers: 键盘修饰键（shift, ctrl, alt等）
        """
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_x = x + self.camera.position[0]
            world_y = y + self.camera.position[1]

            # 获取 tilemap 的图块大小
            tile_width = self.game_map.tile_map.tile_width
            tile_height = self.game_map.tile_map.tile_height

            # 计算点击位置的图块坐标
            tile_x = int(world_x // tile_width)
            tile_y = int(world_y // tile_height)
            print(tile_x, tile_y)
            for player_sprite in self.player_sprite_list:
                player_sprite.is_clicked(world_x, world_y)
            # self.game_map.player_sprite.target_to((tile_x, tile_y))

    def on_close(self):
        if self.save_file_name:
            next(iter(self.NpcDict.values())).AiComponent.world.SaveData(self.save_file_name)
            read_data.save_gameplay_record(self.save_file_name['record'])
            name_dict = self.save_file_name
        else:
            name_dict = next(iter(self.NpcDict.values())).AiComponent.world.SaveData()
            name_dict['record'] = read_data.save_gameplay_record(self.save_file_name)
        world_time = self.world_pass_time
        save_playgame_data = {'file_name':name_dict, "world_pass_time": world_time}
        if self.save_file_name:
            read_data.save_data(save_playgame_data, self.save_file_name['load_path'], True)
        else:
            read_data.save_data(save_playgame_data, 'data/load_game/game_data.json')

        super().on_close()
        # 这里可以添加处理窗口关闭事件的代码

    def load_data(self, data):
        self.save_file_name = data['file_name']
        self.ai_offline_event_data = data['record']
        read_data.log_receive_data = self.ai_offline_event_data
        self.world_pass_time = data['world_pass_time']


def start_game(control_by_ai=True):
    # 初始化游戏
    import os
    new_game = MyGame()
    current_path = os.path.dirname(__file__)
    map_file = current_path + "/desert.tmx"
    new_game.setup(map_file, control_by_ai)
    return new_game
