import random
import arcade
import World.building_mgr as building_mgr
from path_find import astar

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

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

@singleton
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
        blocking_layer_name = "Collisions"
        self.collision_list = self.tile_map.sprite_lists.get(blocking_layer_name)
        # test
        now_list = self.tile_map.sprite_lists.get("Sector Blocks")

        self.width = int(self.tile_map.width + 2)
        self.height = int(self.tile_map.height + 2)
        self.tile = [[Tile() for _ in range(self.height)] for _ in range(self.width)]
        self.buildingMgr = building_mgr.BuildingMgr(self)
        self.world = world
        self.spawning_blocks_list = []
        self.init_tile()



    def add_player(self, player):
        self.scene.add_sprite("Player", player)

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

    def findNoCoillison(self, pos):
        if not self.is_obstacle(pos[0], pos[1]):
            return pos
        for distance in range(1, 4 + 1):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    if abs(dx) + abs(dy) == distance:
                        if not self.is_obstacle(pos[0] + dx, pos[1] + dy):
                            return pos[0] + dx, pos[1] + dy

    def getTileListFromPos(self, pos, view_x=3, view_y=3):
        tilex, tiley = pos[0], pos[1]
        entities = []
        for i in range(-view_x, view_x + 1):
            for j in range(-view_y, view_y + 1):
                if tilex + i < len(self.tile):
                    entities.append(self.tile[tilex + i][tiley + j])
        return entities

    def update(self):
        for xt in range(self.width):
            for yt in range(self.height):
                self.tile[xt][yt].clear()



    def init_tile(self):
        for sprite in self.collision_list:
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            self.tile[tile_x][tile_y].obstacle = True

        Building_list = self.tile_map.sprite_lists.get("Sector Blocks")
        Subregion_list = self.tile_map.sprite_lists.get("Arena Blocks")
        Object_list = self.tile_map.sprite_lists.get("Object Interaction Blocks")
        Spawning_list = self.tile_map.sprite_lists.get("Spawning Blocks")

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

        last_x = 0
        last_y = 0
        for sprite in Spawning_list:
            tile_x = int(sprite.center_x // self.tile_map.tile_width)
            tile_y = int(sprite.center_y // self.tile_map.tile_height)
            if abs(tile_x-last_x)+abs(tile_y-last_y) <= 1:
                continue
            last_x = tile_x
            last_y = tile_y
            self.spawning_blocks_list.append((tile_x, tile_y))



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

    def get_all_npc(self):
        return self.world.NpcDict.values()