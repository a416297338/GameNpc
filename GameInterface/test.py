import arcade
from pyglet.math import Vec2
import time
import World.building_mgr as building_mgr
import datetime
from arcade.experimental import Shadertoy
from pytiled_parser import parse_map

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tiled Map with Scrolling Example"

import random
# find path
import heapq

game = None

class DialogueBox:
    def __init__(self, image_path, font_size=14):
        self.texture = arcade.load_texture(image_path)
        self.text = None
        self.end_time = 0
        self.font_size = font_size

    def set_text(self, text, duration_time = 5):
        self.text = text
        self.end_time = time.time() + duration_time

    def draw(self, center_x, center_y):
        # 绘制对话框
        center_x+=48
        center_y+=48
        now_time = time.time()
        if self.texture and now_time < self.end_time:
            width = 200
            height = 200
            arcade.draw_texture_rectangle(center_x, center_y, width, height, self.texture)

            # 创建文本对象
            text = arcade.Text(self.text, 0, 0, arcade.color.BLACK, self.font_size)

            # 计算文本的起始位置,使其居中
            text_x = center_x - text.content_width // 2
            text_y = center_y - text.content_height // 2 + 20

            # 绘制文本
            text.position = (text_x, text_y)
            text.draw()

class TimeDisplay:
    def __init__(self, x, y, color, font_size=20, font_name="Arial"):
        self.time_text = arcade.Text("00:00:00", x, y, color, font_size, font_name=font_name)
        self.last_time_update = time.time()

    def update(self):
        """ 更新时间显示 """
        current_time = time.time()
        if current_time - self.last_time_update >= 1.0:
            self.last_time_update = current_time
            current_time_str = time.strftime("%H:%M:%S", time.localtime())
            self.time_text.text = current_time_str

    def draw(self):
        """ 绘制时间显示 """
        self.time_text.draw()


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f


def astar(maze, start, end):
    # 创建开始和结束节点
    start_node = Node(None, tuple(start))
    end_node = Node(None, tuple(end))

    # 初始化开放列表和关闭列表
    open_list = []
    closed_dict = {}
    closed_list = []

    # 将开始节点添加到开放列表
    heapq.heappush(open_list, start_node)
    closed_dict[start_node.position] = 0
    find_node = 0
    # 循环直到找到终点
    while open_list:
        # 获取当前节点
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # 如果找到目标,回溯路径
        white_square = arcade.SpriteSolidColor(50, 50, arcade.color.WHITE)
        # 设置方块的位置
        # draw debug
        # pos = game.game_map.getPosFromTile(current_node.position)
        # white_square.center_x = pos[0]  # X 轴位置
        # white_square.center_y = pos[1]  # Y 轴位置
        # 将方块添加到 SpriteList 中
        # game.game_map.scene.add_sprite("TopLayer", white_square)
        # end debug
        print(current_node.f)
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # 返回反转的路径
        find_node += 1
        print(current_node.position)
        if find_node > 500:  # 最大查找节点个数
            break
        # 生成子节点
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # 相邻四个方向
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # 确保在网格范围内
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[0]) - 1) or \
                    node_position[1] < 0:
                continue

            # 确保可走并且不在关闭列表中
            if maze[node_position[0]][node_position[1]]:
                continue

            # 创建新的节点
            child = Node(current_node, node_position)
            # 创建子节点的f, g, 和 h值
            child.g = current_node.g + 1
            # 已有更优解
            if child.position in closed_dict and child.g >= closed_dict[child.position]:
                continue
            closed_dict[child.position] = child.g

            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h * 2
            # 添加子节点到开放列表
            heapq.heappush(open_list, child)

    # 如果没有找到路径,返回离目标最近的节点
    closest_node = min(closed_list, key=lambda node: abs(node.position[0] - end_node.position[0]) + abs(
        node.position[1] - end_node.position[1]))

    path = []
    while closest_node is not None:
        path.append(closest_node.position)
        closest_node = closest_node.parent
    return path[::-1]


# find path

class Player(arcade.Sprite):
    def __init__(self, game, pos=(0, 0), sprite_path='map_assets/cute_rpg_word_VXAce/characters/!Character_RM_001.png'):

        super().__init__()

        # 加载 sprite sheet
        self.game = game
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
        pos = self.game.getPosFromTile(pos)
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.target_pos = None
        self.target_path_list = None
        self.current_frame = 0
        self.speed = 5
        self.move_key_set = set()
        self.anim_speed = 10
        self.update_animation()

        self.dialogue_box = DialogueBox("map_assets/network/chat.png")

    def is_clicked(self, x, y):
        # 检查点击位置是否在角色的圆形范围内
        if(x - self.center_x) ** 2 + (y - self.center_y) ** 2 <= self.radius ** 2:
            self.chat("don't touch me")
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

    def update(self):
        if self.controll_by_person():
            self.target_pos = None
            self.target_path_list = None
        if self.target_path_list:
            if self.move_to(self.target_path_list[0]):
                del self.target_path_list[0]

        else:
            last_center_x = self.center_x
            last_center_y = self.center_y
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.center_x = min(max(self.center_x, self.width / 2), self.game.map_width - self.width / 2)
            self.center_y = min(max(self.center_y, self.height / 2), self.game.map_height - self.height / 2)
            if self.check_collision():
                self.center_x = last_center_x
                self.center_y = last_center_y
        self.update_animation()
        self.clear_move()

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
        pos = self.game.getPosFromTile(tile_pos)
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

    def target_to(self, target_pos):
        self.target_pos = target_pos
        pos_list = self.game.find_path(self.tile_pos, target_pos)
        # draw debug
        # for pos in pos_list:
        #
        #     # 创建一个白色方块
        #     white_square = arcade.SpriteSolidColor(50, 50, arcade.color.WHITE)
        #     # 设置方块的位置
        #     pos = self.game.getPosFromTile(pos)
        #     white_square.center_x = pos[0]  # X 轴位置
        #     white_square.center_y = pos[1]  # Y 轴位置
        #     # 将方块添加到 SpriteList 中
        #     self.game.scene.add_sprite("TopLayer", white_square)
        # end debug
        self.target_path_list = pos_list[1:]

    def stop(self):
        self.change_x = 0
        self.change_y = 0

    def check_collision(self):
        return arcade.check_for_collision_with_list(self, self.game.collision_list)

    def chat(self, text, duration_time=5, down_flag = False):
        self.dialogue_box.set_text(text, duration_time, down_flag)

    @property
    def tile_pos(self):
        return self.game.getTileFromPos(self.center_x, self.center_y)



class Tile:
    def __init__(self):
        ## static object
        self.obstacle = None
        self.building = None
        self.subregion = None
        self.furniture = None
        ## dynamic object
        self.npc = None
        self.event = None

    def clear(self):
        self.npc = None
        self.event = None

    def __bool__(self):  # 判断是否为实体
        return bool(self.obstacle)

    def observable_set(self):
        return {self.npc, self.building, self.event}


class GameMap:
    def __init__(self, map_path, world=None):
        self.tile_map = arcade.load_tilemap(map_path, scaling=1.0)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.scene.add_sprite_list("TopLayer")
        self.tile_dict = {}
        for layer_name, layer in self.scene.name_mapping.items():
            for sprite in layer:
                tile_x = int(sprite.center_x // self.tile_map.tile_width)
                tile_y = int(sprite.center_y // self.tile_map.tile_height)
                if (tile_x, tile_y) not in self.tile_dict:
                    self.tile_dict[(tile_x, tile_y)] = []
                sprite.layer_name = layer_name
                self.tile_dict[(tile_x, tile_y)].append(sprite)
        self.map_width = self.tile_map.width * self.tile_map.tile_width
        self.map_height = self.tile_map.height * self.tile_map.tile_height
        self.tile_width = self.tile_map.tile_width
        self.tile_height = self.tile_map.tile_height
        # Create a simple player sprite
        self.player_sprite = Player(self, (65, 80))
        blocking_layer_name = "Collisions"
        self.collision_list = self.tile_map.sprite_lists.get(blocking_layer_name)
        # test
        now_list = self.tile_map.sprite_lists.get("Sector Blocks")

        self.scene.add_sprite("Player", self.player_sprite)
        self.world = world
        self.width = int(self.tile_map.width + 2)
        self.height = int(self.tile_map.height + 2)
        self.tile = [[Tile() for _ in range(self.height)] for _ in range(self.width)]
        self.buildingMgr = building_mgr.BuildingMgr(self)
        self.init_tile()


    def set_map(self, tile):
        self.tile = tile

    def set_obstacle(self, x, y):
        self.tile[x][y].obstacle = True

    def is_obstacle(self, x, y):
        return self.tile[x][y]

    def getTileFromPos(self, posx, posy):
        return int(posx // self.tile_width), int(posy // self.tile_height)

    def randomPos(self):
        return self.tile_width * random.randint(0, self.width - 1), self.tile_height * random.randint(0, self.hight - 1)

    def getPosFromTile(self, tile):
        return tile[0] * self.tile_width + self.tile_width * 0.5, tile[1] * self.tile_height + self.tile_height * 0.5

    def getTileListFromPos(self, pos, view_x=3, view_y=3):
        tilex, tiley = self.getTileFromPos(pos[0], pos[1])
        entities = []
        for i in range(-view_x, view_x + 1):
            for j in range(-view_y, view_y + 1):
                if tilex + i in self.tile:
                    entities.extend(self.tile[tilex + i][tiley + j])
        return entities

    def update(self):
        for xt in range(self.width):
            for yt in range(self.height):
                self.tile[xt][yt].clear()

        for npc in self.world.get_npc_list():
            x, y = npc.pos[0], npc.pos[1]
            self.tile[x][y].npc = npc


    def init_tile(self):
        for sprite in self.collision_list:
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            self.tile[tile_x][tile_y].obstacle = True

        Building_list = self.tile_map.sprite_lists.get("Sector Blocks")
        Subregion_list = self.tile_map.sprite_lists.get("Arena Blocks")
        Object_list = self.tile_map.sprite_lists.get("Object Interaction Blocks")
        build_dict = {}

        for sprite in Building_list:
            build_name = sprite.properties['name']
            if build_name not in build_dict:
                build_dict[build_name] = []
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            build_dict[build_name].append((tile_x, tile_y))
        for name, pos_list in build_dict.items():
            self.buildingMgr.addBuild("build", build_dict[name], name=name)

        subregion_dict = {}
        for sprite in Subregion_list:
            subregion_name = sprite.properties['name']
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            tile_build = self.tile[tile_x][tile_y].building
            if not tile_build:
                continue
            if tile_build not in subregion_dict:
                subregion_dict[tile_build] = {}
            if subregion_name not in subregion_dict[tile_build]:
                subregion_dict[tile_build][subregion_name] = []
            subregion_dict[tile_build][subregion_name].append((tile_x, tile_y))

        for build, subregion_dict in subregion_dict.items():
            for subregion_name, subregion_list in subregion_dict.items():
                self.buildingMgr.addSubregion(build, subregion_list, subregion_name)

        object_dict = {}
        for sprite in Object_list:
            object_name = sprite.properties['name']
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            tile_subregion = self.tile[tile_x][tile_y].subregion
            if not tile_subregion:
                continue
            if tile_subregion not in object_dict:
                object_dict[tile_subregion] = {}
            if object_name not in object_dict[tile_subregion]:
                object_dict[tile_subregion][object_name] = []
            object_dict[tile_subregion][object_name].append((tile_x, tile_y))

        for subregion, object_dict in object_dict.items():
            for object_name, object_list in object_dict.items():
                self.buildingMgr.addFurniture(subregion, object_list, object_name)



    def getTile(self, x, y):
        return self.tile[x][y]

    def getLocationByTilePos(self, tilePos):
        if self.tile[tilePos[0]][tilePos[1]].building:
            return self.tile[tilePos[0]][tilePos[1]].building.getLocation()
        else:
            return None

    def init_data(self, data):
        pass

    def check_area_obstacle(self, s_x, s_y, end_x, end_y):
        for x in range(s_x, end_x):
            for y in range(s_y, end_y):
                if self.tile[x][y]:
                    return False
        return True

    def find_path(self, start_pos, end_pos):
        return astar(self.tile, start_pos, end_pos)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.collision_list = None
        arcade.set_background_color(arcade.color.AMAZON)

        self.game_map = None
        self.scene = None
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_sprite = None
        self.map_width = 0
        self.map_height = 0
        self.tile_dict = {}

    def update(self, delta_time):
        pass

    def setup(self):
        # Load the Tiled map
        self.game_map = GameMap("desert.tmx")
        self.scene = self.game_map.scene
        self.map_width = self.game_map.map_width
        self.map_height = self.game_map.map_height
        self.player_sprite = self.game_map.player_sprite
        print(self.map_width)
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
        self.player_sprite.dialogue_box.draw(self.player_sprite.center_x, self.player_sprite.center_y)
        # 获取当前时间
        current_time = time.strftime("%H:%M:%S", time.localtime())

        # 在屏幕上绘制时间
        arcade.draw_text(f"Time: {current_time}", self.camera.position[0] + 10,
                         self.camera.position[1] + self.camera.viewport_height - 30, arcade.color.WHITE, 14)

        # 绘制对话框
        # 绘制人物对话框


    def on_update(self, delta_time):
        # Update player position
        self.player_sprite.update()
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
        target_x = self.player_sprite.center_x - self.camera.viewport_width / 2
        target_y = self.player_sprite.center_y - self.camera.viewport_height / 2

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
        self.player_sprite.key_down(key)
        if key == arcade.key.SPACE:

            sprite_list = self.tile_dict[self.get_sprite_tiled(self.player_sprite)]
            for sprite in sprite_list:
                sprite.visible = False

    def on_key_release(self, key, modifiers):
        self.player_sprite.key_release(key)

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
            self.player_sprite.is_clicked(world_x, world_y)
            self.game_map.player_sprite.target_to((tile_x, tile_y))


import threading

def print_message(message):
    print(message)

def test_func():
    game = MyGame()
    game.setup()
    arcade.run()
    print("111")

def main():
    global game
    thread1 = threading.Thread(target=print_message, args=("Hello from Thread 1",))
    thread2 = threading.Thread(target=test_func)

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待线程结束
    thread1.join()
    thread2.join()

    print("Both threads have finished.")



if __name__ == "__main__":
    main()
