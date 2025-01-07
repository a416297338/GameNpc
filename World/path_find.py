import heapq
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
    print("find path")
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

        #print(current_node.f)
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # 返回反转的路径
        find_node += 1
        #print(current_node.position)
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