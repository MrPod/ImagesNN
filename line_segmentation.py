from collections import namedtuple
import numpy as np
import os
from typing import List
import cv2
import PicHandler
import TextBlock


# from PicHandler import*
class Line:
    @staticmethod
    def lines_segmentation(path):

        img = cv2.imread(path)

        _, img_matrix = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY_INV)
        binary_matrix = (img_matrix == 255).astype(int)
        sum_of_lines = []  # сумма пикселей по строкам
        # np.logical_not(closed, out=closed)
        # суммируем матрицу по строкам
        for line in binary_matrix:
            sum_of_lines.append(np.sum(line))

        minimum = np.min(sum_of_lines)
        maximum = np.max(sum_of_lines)
        delta = maximum - minimum
        borderline = minimum + delta * 0.07  # максимальное значение минимума
        minimum_line_height = 25  # минимальная высота строки

        min_intervals = []
        while i < len(sum_of_lines) - 2:
            i = min(i + 1, len(sum_of_lines) - 1)
            if sum_of_lines[i] <= borderline:
                j = min(i + 1, len(sum_of_lines) - 2)
                while sum_of_lines[j] <= borderline:
                    j = min(j + 1, len(sum_of_lines) - 2)
                min_intervals.append((i, j))
                i = j
            if i == 1500:
                break
        (_, width, _) = img.shape
        lines_y = []
        top = 0
        bottom = 0
        for i in range(len(min_intervals) - 1):
            current_minimum = 999999
            minimum_index = 0
            for j in range(min_intervals[i][0], min_intervals[i][1] + 1):
                if current_minimum > sum_of_lines[j]:
                    current_minimum = sum_of_lines[j]
                    minimum_index = j
            lines_y.append(minimum_index)

        for i in range(len(lines_y) - 1):
            if i + 1 < len(lines_y):
                if lines_y[i + 1] - lines_y[i] < minimum_line_height:
                    lines_y.pop(i)

        lines = []
        for i in range(len(lines_y) - 1):
            top = lines_y[i]
            bottom = lines_y[i + 1]
            box = (0, top, width, bottom)  # координаты строки
            cur_line = img[top:top + bottom, 0:width]
            pos = Position(0, top, width, abs(top - bottom))
            lines.append(TextBlock(pos, PicHandler(cur_line)))
            lines.append((box, cur_line))
            # cv2.rectangle(img, (0, top), (width, bottom + top), 0, 1)
            cv2.line(img, (0, top), (width, top), 0, 1)
        cv2.imshow("img", img)
        return lines
