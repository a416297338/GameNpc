import random
import json
# 生成随机的建筑
def generate_random_building(s_x, s_y, end_x, end_y):
    building_types = ["residential", "commercial", "industrial", "school", "hospital"]  # 建筑类型列表
    probabilities = [0.3, 0.2, 0.1, 0.2, 0.2]  # 对应建筑类型的选择概率
    building_type = random.choices(building_types, probabilities)[0]  # 根据概率选择建筑类型
    width = random.randint(2, 4)  # 随机生成建筑宽度
    hight = random.randint(2, 4)  # 随机生成建筑高度
    start_x = random.randint(s_x, end_x - width)  # 随机生成起始x坐标
    start_y = random.randint(s_y, end_y - hight)  # 随机生成起始y坐标
    tile_pos_list = [(x, y) for x in range(start_x, start_x + width) for y in range(start_y, start_y + hight)]  # 生成占用的地块列表
    return {
        'type': building_type,
        'tilePosList': tile_pos_list,
        'furniture': None,
    }

# 输出随机生成的建筑
Out_list = []
for i in range(9):
    for k in range(9):
        Out_list.append(generate_random_building(5+i*10, 5+k*10, 15+i*10, 15+k*10))

print(json.dumps(Out_list))
