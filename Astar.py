class Point:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def is_equal(self, point):
        if self.row == point.row and self.column == point.column:
            return True
        return False


class Node:
    def __init__(self, point, end_point):
        self.point = point
        self.father = None
        self.steps_to_start_point = 0
        self.steps_to_end_point = abs(
            end_point.row - point.row) + abs(end_point.column - point.column)


class AStar:
    def __init__(self, map, start_node, end_node, pass_tag):
        # Nodes need to explore
        self.open_list = []
        # Explored nodes
        self.close_list = []
        self.map = map
        self.start_node = start_node
        self.end_node = end_node
        self.pass_tag = pass_tag

    def find_optimal_node(self):
        optimal_node = self.open_list[0]
        for node in self.open_list:
            if node.steps_to_start_point + node.steps_to_end_point < optimal_node.steps_to_start_point + optimal_node.steps_to_end_point:
                optimal_node = node
        return optimal_node

    def is_in_close_list(self, node):
        for n in self.close_list:
            if n.point.is_equal(node.point):
                return True
        return False

    def is_in_open_list(self, node):
        for n in self.open_list:
            if n.point.is_equal(node.point):
                return True
        return False

    def search_neighbor_node(self, node, offset_x, offset_y):
        neighbor_point = Point(node.row + offset_x, node.column + offset_y)
        neighbor_node = Node(neighbor_point, self.end_node.point)
        if neighbor_point.row < 0 or neighbor_point.column < 0 \
                or neighbor_point.row > len(self.map) - 1 \
                or neighbor_point.column > len(self.map[0]) - 1:
            return None
        if self.map[neighbor_point.row][neighbor_point.column] != self.pass_tag\
                and not neighbor_point.is_equal(self.end_node.point):
            return None
        if self.is_in_close_list(neighbor_node):
            return None
        if not self.is_in_open_list(neighbor_node):
            self.open_list.append(neighbor_node)
            neighbor_node.father = node
            step = 1
            tmp = neighbor_node.father
            while not tmp.point.is_equal(self.start_node.point):
                step += 1
                tmp = tmp.father
            neighbor_node.steps_to_start_point = step
        return neighbor_node

    def start(self):
        if self.map[self.end_node.point.row][self.end_node.point.column] == self.pass_tag:
            return

        self.open_list.append(self.start_node)
        while True:
            optimal_node = self.find_optimal_node()
            self.open_list.remove(optimal_node)
            self.close_list.append(optimal_node)
            self.search_neighbor_node(optimal_node, 0, -1)
            self.search_neighbor_node(optimal_node, 1, 0)
            self.search_neighbor_node(optimal_node, 0, 1)
            self.search_neighbor_node(optimal_node, -1, 0)
            self.is_in_close_list(self.end_node)
            if self.end_node:
                path = []
                node = self.end_node
                while not node.point.is_equal(self.start_node.point):
                    path.append(node)
                    if node.father:
                        node = node.father
                path.reverse()
                return path
            if len(self.open_list) == 0:
                return None
