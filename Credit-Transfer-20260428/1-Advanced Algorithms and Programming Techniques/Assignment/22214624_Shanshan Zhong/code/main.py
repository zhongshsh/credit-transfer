from dinic import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

def seg_maxflow(img):
    height, width = img.shape[:2]

    node_list = []
    s_cap = []
    t_cap = []
    node_dict = {}

    for y in range(height):
        for x in range(width):
            node_id = str(y * width + x)
            node_list.append(node_id)

            # 设置源点（前景s）和汇点（背景t）
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                s_cap.append(node_id)
                s_cap.append(0)
                t_cap.append(node_id)
                t_cap.append(0)
            else:
                b, g_, r = img[y, x]
                mean_rgb = (b+g_+r)/3
                s_cap.append(node_id)
                s_cap.append(b+g_+r)
                t_cap.append(node_id)
                t_cap.append(255 - mean_rgb)

            # 设置结点之间的边
            if node_dict.get(node_id, -1) == -1:
                node_dict[node_id] = [[], []]

            if x < width - 1:
                right_node_id = str(y * width + x + 1)
                if node_dict.get(right_node_id, -1) == -1:
                    node_dict[right_node_id] = [[], []]

                diff = np.sum((img[y, x] - img[y, x + 1]) ** 2)
                # diff = np.sum(np.abs(img[y, x] - img[y, x + 1]))
                node_dict[node_id][0].append(right_node_id)
                node_dict[node_id][1].append(diff)
                node_dict[right_node_id][0].append(node_id)
                node_dict[right_node_id][1].append(diff)
            if y < height - 1:
                bottom_node_id = str((y + 1) * width + x)
                if node_dict.get(bottom_node_id, -1) == -1:
                    node_dict[bottom_node_id] = [[], []]

                diff = np.sum((img[y, x] - img[y + 1, x]) ** 2)
                # diff = np.sum(np.abs(img[y, x] - img[y + 1, x]))
                node_dict[node_id][0].append(bottom_node_id)
                node_dict[node_id][1].append(diff)
                node_dict[bottom_node_id][0].append(node_id)
                node_dict[bottom_node_id][1].append(diff)

    # 格式: [节点名, 后继节点的名称, 当前节点到各个后继的流量] （None 代表流量无穷大）
    graph = [
        ["s", node_list, s_cap],
        ["t", [], []],
    ]

    for k in node_dict.keys():
        next_node_list = node_dict[k][0]
        next_cap = node_dict[k][1]

        if k in node_list:
            next_node_list.append("t")
            next_cap.append(t_cap[node_list.index(k)])

        graph.append([k, next_node_list, next_cap])

    name_index_dict = dict()
    node_list = []
    for i in range(len(graph)):
        node_list.append(create_node(graph[i][0], graph[i][1], graph[i][2]))
        name_index_dict[graph[i][0]] = i

    # 调用算法求解最大流
    routes = Dinic_Solve("S", "E", node_list, name_index_dict)

    # 绘制图像分割示意图
    labels = np.zeros_like(img)
    for y in range(height):
        for x in range(width):
            node_id = str(y * width + x)
            if node_id in routes:
                labels[y, x] = [1, 1, 1]

    return labels


def plot(img, labels):
    # 显示原始图像和分割后的图像
    _, ax = plt.subplots(ncols=2, figsize=(8, 4), sharex=True, sharey=True)
    ax[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax[0].set_title('Original image')
    ax[1].imshow(labels, cmap='gray')
    ax[1].set_title('Segmented image')

    # 去除横纵坐标
    for a in ax:
        a.set_axis_off()

    plt.show()


if __name__ == '__main__':
    for i in range(5):
        img = cv2.imread(f'image/{i}.jpg')
        labels = seg_maxflow(img)
        plot(img, labels)
