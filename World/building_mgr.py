import helper
import random

class Furniture:
    def __init__(self, subregion, tilePosList, name):
        self.tilePosList = tilePosList
        self.name = name
        self.subregion = subregion

class Subregion:
    def __init__(self, build, tilePosList, name):
        self.tilePosList = tilePosList
        self.build = build
        self.name = name
        self.furnitureList = []

class Building:
    def __init__(self):
        self.id = 0
        self.type = None
        self.name = None
        self.tileSize = 0
        self.tilePosList = []
        self.subregionList = []
        self.boxAABB = []
        self.centerTile = None

    def getTilePosList(self):
        return self.tilePosList

    def getLocation(self):
        return self.name


class ObjectFactory:
    _id = 1
    build_dict = {}
    build_name_dict ={}
    def create_building(self, type, tilePosList, furnitureList=None, name=None):
        build = Building()
        build.id = self._id
        self.build_dict[self._id] = build
        self.build_name_dict[name] = build
        self._id += 1
        build.name = name
        build.type = type
        build.tilePosList = tilePosList
        minx, maxx = tilePosList[0][0], tilePosList[0][0]
        miny, maxy = tilePosList[0][1], tilePosList[0][1]
        for tile in tilePosList:
            minx, maxx, miny, maxy = min(minx, tile[0]), max(maxx, tile[0]), min(miny, tile[1]), max(maxy, tile[1])
        build.boxAABB = [minx, maxx, miny, maxy]
        build.centerTile = [(minx + maxx) / 2  , (miny + maxy) / 2]

        return build

    def create_furniture(self, subregion, tilePosList, name):
        return Furniture(subregion, tilePosList, name)

    def create_subregion(self, build, tilePosList, name):
        return Subregion(build, tilePosList, name)

factor = ObjectFactory()

class BuildingMgr:
    def __init__(self, mapMgr):
        self.mapMgr = mapMgr
        self.builidingDictX = {}
        self.builidingDictY = {}

    def update(self):
        pass

    def findBuildingListByX(self, type, X):
        return self.builidingDictX[type].get(X)

    def findBuildingListByY(self, type, Y):
        return self.builidingDictY[type].get(Y)

    def findNearBuildingByPos(self, type, pos):
        buildingListX, buildingListY = self.builidingDictX[type], self.builidingDictY[type]
        if not buildingListX:
            return None
        minDistanceX = 10000000
        target_idx = 0
        for idx, build in enumerate(buildingListX):
            distanceX = helper.distance(build.centerTile, pos)
            if distanceX < minDistanceX:
                minDistanceX = min(distanceX, minDistanceX)
                target_idx = idx

        return buildingListX[target_idx]

    def findNearBuidingByPos(self, type, pos, num):
        sorted_list = sorted(list(ObjectFactory.build_dict.values()), key=lambda t: (t.centerTile[0]-pos[0])**2 + (t.centerTile[1] - pos[1]) ** 2)
        return sorted_list[:num]

    def findNearBuidingByName(self, name):
        for build in ObjectFactory.build_dict.values():
            if build.name == name:
                return build

    def addBuild(self, type, tilePosList, furnitureList=None, name=None):
        new_build = factor.create_building(type, tilePosList, furnitureList, name)
        idx = 0
        if type not in self.builidingDictX:
            self.builidingDictX[type] = []
            self.builidingDictY[type] = []
        for idx, build in enumerate(self.builidingDictX[type]):
            if build.centerTile[0] > new_build.centerTile[0]:
                break
        self.builidingDictX[type].insert(idx, new_build)
        for idx, build in enumerate(self.builidingDictY[type]):
            if build.centerTile[1] > new_build.centerTile[0]:
                break
        self.builidingDictY[type].insert(idx, new_build)
        for tilePos in tilePosList:
            tile = self.mapMgr.getTile(tilePos[0], tilePos[1])
            tile.building = new_build
        return new_build

    def addSubregion(self, build, tilePosList, name):
        subregion = factor.create_subregion(build, tilePosList, name)
        build.subregionList.append(subregion)
        for tilePos in tilePosList:
            tile = self.mapMgr.getTile(tilePos[0], tilePos[1])
            tile.subregion = subregion

        return subregion

    def addFurniture(self, subregion, tilePosList, name):
        new_furniture = factor.create_furniture(subregion, tilePosList, name)
        subregion.furnitureList.append(new_furniture)
        for tilePos in tilePosList:
            tile = self.mapMgr.getTile(tilePos[0], tilePos[1])
            tile.furniture = new_furniture

    def get_data(self):
        re_data = {}
        for build in self.world.buildingListX:
            re_data['type'] = build.type
            re_data['tilePosList'] = build.tilePosList
            re_data['furniture'] = []
            for furniture in build.furnitureList:
                f_data = {'type': furniture.type, 'tilePosList': furniture.tilePosList}
                re_data.append(f_data)

    def create_building(self, type):
        width = random.randint(2, 4)  # 随机生成建筑宽度
        hight = random.randint(2, 4)  # 随机生成建筑高度
        start_x = 0
        start_y = 0
        for i in range(100):
            start_x = random.randint(0, self.mapMgr.width - width)  # 随机生成起始x坐标
            start_y = random.randint(0, self.mapMgr.hight - hight)  # 随机生成起始y坐标
            if(self.mapMgr.check_area_obstacle(start_x, start_y, start_x + width,
                                                  start_y + hight)):
                break

        tile_pos_list = [(x, y) for x in range(start_x, start_x + width) for y in
                         range(start_y, start_y + hight)]

        build = self.addBuild(type, tile_pos_list)
        return build

    def find_tile_by_location(self, location):
        return ObjectFactory.build_name_dict[location].centerTile

    def find_build_by_location(self, location):
        return ObjectFactory.build_name_dict[location]

    def find_furniture_in_build(self, build):
        furniture_list = []
        for subregion in build.subregionList:
            for furniture in subregion.furnitureList:
                furniture_list.append(furniture)
        return furniture_list

    " Isabella Rodriguez's apartment"