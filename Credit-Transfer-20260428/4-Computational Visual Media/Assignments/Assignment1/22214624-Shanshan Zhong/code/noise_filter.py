import os
import time
from PIL import Image, ImageFilter
import cv2
from aip import AipOcr
import numpy as np
import matplotlib.pyplot as plt


def traversalDenois(image):
    # 将黑色干扰线替换为白色
    width = image.size[0]  # 长度
    height = image.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            data = image.getpixel((i, j))  # 打印该图片的所有点
            if data[0] <= 25 and data[1] <= 25 and data[2] <= 25:  # RGBA的r,g,b均小于25
                image.putpixel((i, j), (255, 255, 255, 255))  # 则这些像素点的颜色改成白色
    image = image.convert("RGB")  # 把图片强制转成RGB
    return image


if __name__ == "__main__":
    dir = "./data/"
    captcha = dir + "captcha.png"
    captcha = dir + "people_old.png"
    fgrey = dir + "grey.png"

    # 灰度化
    Grayimage = cv2.cvtColor(cv2.imread(captcha), cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(Grayimage, 160, 255, cv2.THRESH_BINARY)
    cv2.imwrite(fgrey, thresh)

    # 去噪
    image = cv2.imread(captcha, cv2.IMREAD_GRAYSCALE)
    source = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # 循环去噪
    image = Image.open(captcha)
    image = traversalDenois(image)
    image.save("./data/traveral.png")

    # 均值滤波
    result1 = cv2.blur(source, (3, 3))
    result2 = cv2.blur(source, (15, 15))
    cv2.imwrite("./data/mean.png", result1)
    cv2.imwrite("./data/mean15.png", result2)

    # 方框滤波
    result3 = cv2.boxFilter(source, -1, (3, 3), normalize=1)
    result4 = cv2.boxFilter(source, -1, (15, 15), normalize=1)
    cv2.imwrite("./data/box.png", result3)
    cv2.imwrite("./data/box15.png", result4)

    # 高斯滤波
    result5 = cv2.GaussianBlur(source, (3, 3), 0)
    result6 = cv2.GaussianBlur(source, (15, 15), 0)
    cv2.imwrite("./data/gaux.png", result5)
    cv2.imwrite("./data/gaux15.png", result6)

    # 中值滤波
    result7 = cv2.medianBlur(source, 3)
    cv2.imwrite("./data/med.png", result7)

    # 高斯双边滤波
    result8 = cv2.bilateralFilter(source, 15, 50, 50)
    cv2.imwrite("./data/bilater.png", result8)
