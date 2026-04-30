import numpy as np


class Node:
    def __init__(self, name, arc_dict):
        self.name = name
        self.arc_dict = arc_dict


def create_node(name, next_list, flow_list):
    arc_dict = {}
    for i in range(len(next_list)):
        arc_dict[next_list[i]] = flow_list[i]
    return Node(name, arc_dict)


def create_level_graph(s, e, node_list, name_index_dict):
    level_graph = np.zeros((len(node_list), len(node_list))).tolist()
    cur_layer = [s]
    all_node = set()
    all_node.add(s)
    next_layer = set()
    while len(cur_layer) > 0:
        for node_name in cur_layer:
            node = node_list[name_index_dict[node_name]]
            for key in node.arc_dict.keys():
                if key not in all_node and (node.arc_dict[key] is None or node.arc_dict[key] > 0):
                    level_graph[name_index_dict[node_name]
                                ][name_index_dict[key]] = node.arc_dict[key]
                    next_layer.add(key)
                    all_node.add(key)
        cur_layer = list(next_layer)
        next_layer = set()
    return level_graph if e in all_node else None


def Dinic_Solve(s, e, node_list, name_index_dict):
    routes = []
    s_index = name_index_dict[s]
    e_index = name_index_dict[e]
    level_graph = create_level_graph(s, e, node_list, name_index_dict)
    while level_graph is not None:
        res_list = []
        while True:
            res = bfs(e_index, [s_index], None, level_graph)
            if res is None:
                break
            # 更新 level graph
            route, flow = res
            for i in range(len(route) - 1):
                if level_graph[route[i]][route[i + 1]] is not None:
                    level_graph[route[i]][route[i + 1]] -= flow
            # 追加记录增广路径
            res_list.append(res)
            routes.append([[node_list[n].name for n in res[0]], res[1]])
        # 更新残存网络
        for res in res_list:
            update(res, node_list)
        # 重新构造 level graph
        level_graph = create_level_graph(s, e, node_list, name_index_dict)
    return routes


def update(res, node_list):
    route, flow = res
    for i in range(len(route) - 1):
        n1 = node_list[route[i]]
        n2 = node_list[route[i + 1]]
        # 正向更新 n1 -> n2 剩余流量减少
        if n2.name in n1.arc_dict.keys() and n1.arc_dict[n2.name] is not None:
            n1.arc_dict[n2.name] = n1.arc_dict[n2.name] - flow
        # 反向更新 n2 -> n1 剩余流量增加
        if n1.name in n2.arc_dict.keys() and n2.arc_dict[n1.name] is not None:
            n2.arc_dict[n1.name] = n2.arc_dict[n1.name] + flow


def bfs(e_index, cur_route, last_flow, level_graph):
    if cur_route[-1] == e_index:
        return cur_route, last_flow
    for next_node in range(len(level_graph)):
        if next_node not in cur_route:
            if level_graph[cur_route[-1]][next_node] is None or level_graph[cur_route[-1]][next_node] > 0:
                flow = min_flow(
                    level_graph[cur_route[-1]][next_node], last_flow)
                cur_route.append(next_node)
                res = bfs(e_index, cur_route, flow, level_graph)
                if res is not None:
                    return res
                cur_route.pop(-1)


def min_flow(f1, f2):
    return f1 if f2 is None else (f2 if f1 is None else min(f1, f2))
