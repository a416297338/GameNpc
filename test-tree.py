import math

class Node:
    def __init__(self, point, split, left, right):
        self.point = point
        self.split = split
        self.left = left
        self.right = right

def build_kdtree(points, depth=0):
    if not points:
        return None

    k = len(points[0])  # assuming all points have the same dimension
    axis = depth % k

    sorted_points = sorted(points, key=lambda point: point[axis])
    mid = len(sorted_points) // 2

    return Node(
        point=sorted_points[mid],
        split=axis,
        left=build_kdtree(sorted_points[:mid], depth + 1),
        right=build_kdtree(sorted_points[mid + 1:], depth + 1)
    )

def find_nearest_point(root, target):
    best = [None, float('inf')]

    def nearest_point(node):
        if node is not None:
            axis = node.split
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(target, node.point)))
            if distance < best[1]:
                best[0], best[1] = node.point, distance
            diff = target[axis] - node.point[axis]
            nearest_point(node.left if diff < 0 else node.right)
            if abs(diff) < best[1]:
                nearest_point(node.left if diff >= 0 else node.right)

    nearest_point(root)
    return best[0]

# 示例用法
points = [(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)]
kd_tree = build_kdtree(points)
nearest = find_nearest_point(kd_tree, (3.1245, 0.567))
print(f"The nearest point is at {nearest}")