# -*- coding: utf-8 -*-

import numpy as np

# 4邻域的连通域和8邻域的连通域
# [row, col]
NEIGHBOR_HOODS_4 = True

OFFSETS_4 = [[0, -1], [-1, 0], [0, 0], [1, 0], [0, 1]]

NEIGHBOR_HOODS_8 = False

OFFSETS_8 = [
    [-1, -1],
    [0, -1],
    [1, -1],
    [-1, 0],
    [0, 0],
    [1, 0],
    [-1, 1],
    [0, 1],
    [1, 1],
]


def reorganize(binary: np.array):
    index_map = []
    points = []
    index = -1
    rows, cols = binary_img.shape
    for row in range(rows):
        for col in range(cols):
            var = binary_img[row][col]
            if var < 0.5:  # 如果是背景，抬走下一位
                continue
            if var in index_map:
                index = index_map.index(var)
                num = index + 1
            else:
                index = len(index_map)
                num = index + 1
                index_map.append(var)
                points.append([])
            binary_img[row][col] = num
            points[index].append([row, col])
    return binary_img, points


def neighbor_value(binary_img: np.array, offsets, reverse=False):
    rows, cols = binary_img.shape
    label_index = 0
    rows_ = [0, rows, 1] if reverse == False else [rows - 1, -1, -1]
    cols_ = [0, cols, 1] if reverse == False else [cols - 1, -1, -1]
    for row in range(rows_[0], rows_[1], rows_[2]):
        for col in range(cols_[0], cols_[1], cols_[2]):
            label = 256
            if binary_img[row][col] < 0.5:
                continue
            for offset in offsets:  # 遍历几点自身的value以及邻域的value
                neighbor_row = min(max(0, row + offset[0]), rows - 1)  # 避免行数超出矩阵或者图像边界
                neighbor_col = min(max(0, col + offset[1]), cols - 1)  # 避免列数超出矩阵或者图像边界
                neighbor_val = binary_img[neighbor_row, neighbor_col]
                if neighbor_val < 0.5:  # 说明是背景点，无需分离
                    continue
                label = (
                    neighbor_val if neighbor_val < label else label
                )  # 将label赋值为左上（reverse为False，即正序遍历）的label值
            if label == 255:  # 如果左上还没有被赋予过任何lable值，那么就赋予新的label值
                label_index += 1
                label = label_index
            binary_img[row][col] = label
    return binary_img


def two_pass(binary_img: np.array, neighbor_hoods):
    if neighbor_hoods == NEIGHBOR_HOODS_4:
        offset = OFFSETS_4
    elif neighbor_hoods == NEIGHBOR_HOODS_8:
        offset = OFFSETS_8
    else:
        raise ValueError

    binary_img = neighbor_value(binary_img, offset, False)
    binary_img = neighbor_value(binary_img, offset, True)

    return binary_img


def recursive_seed(binary_img, seed_row, seed_col, offsets, num, max_num):
    rows, cols = binary_img.shape
    binary_img[seed_row][seed_col] = num
    for offset in offsets:
        neighbor_row = min(max(0, seed_row + offset[0]), rows - 1)
        neighbor_col = min(max(0, seed_col + offset[1]), cols - 1)
        var = binary_img[neighbor_row][neighbor_col]
        if var < max_num:
            continue
        binary_img = recursive_seed(
            binary_img, neighbor_row, neighbor_col, offsets, num, max_num
        )
    return binary_img
    pass


def seed_filling(binary_img, neighbor_hoods, max_num=100):
    if neighbor_hoods == NEIGHBOR_HOODS_4:
        offsets = OFFSETS_4
    elif neighbor_hoods == NEIGHBOR_HOODS_8:
        offsets = OFFSETS_8
    else:
        raise ValueError

    num = 1
    rows, cols = binary_img.shape
    for row in range(rows):   # 遍历图片中的每一个点
        for col in range(cols):
            var = binary_img[row][col]
            if var <= max_num:  # 排除所有背景点
                continue
            binary_img = recursive_seed(binary_img, row, col, offsets, num, max_num)
            num += 1
    return binary_img


if __name__ == "__main__":
    binary_img = np.zeros((4, 7), dtype=np.int16)
    index = [
        [0, 2],
        [0, 5],
        [1, 0],
        [1, 1],
        [1, 2],
        [1, 4],
        [1, 5],
        [1, 6],
        [2, 2],
        [2, 5],
        [3, 1],
        [3, 2],
        [3, 4],
        [3, 6],
    ]
    for i in index:
        binary_img[i[0], i[1]] = np.int16(255)

    print("原始二值图")
    print(binary_img)
    # print("hello")

    # print("Two_pass")
    # binary_img = two_pass(binary_img, NEIGHBOR_HOODS_4)
    # binary_img, points = reorganize(binary_img)
    # print(binary_img, points)

    # print(np.iinfo(np.int16))

    print("Seed_Filling")
    binary_img = seed_filling(binary_img, NEIGHBOR_HOODS_4)
    binary_img, points = reorganize(binary_img)
    print(binary_img, points)
