from PicHandler import *
from Position import *
from collections import namedtuple
import numpy as np
from typing import List
import cv2


class Parser:

    def lines_segmentation(pic_handler:PicHandler) -> List[PicHandler]:
        lines = []
        sum_of_lines = []  #сумма пикселей по строкам
        binary_matrix = pic_handler.BlocksOfPixels() #матрица изображения


        #суммируем матрицу по строкам
        for line in binary_matrix:
            sum_of_lines.append(np.sum(line))
        
        minimum = np.min(sum_of_lines)
        maximum = np.max(sum_of_lines)
        delta = maximum - minimum
        borderline = minimum + delta * 0.1 # максимальное значение минимума
        minimum_line_height = 15 #минимальная высота строки

        subarrays = []  #содержит кортежи (начало минимума, конец минимума)

        
        for i in range(len(sum_of_lines)):
            if sum_of_lines[i] <= borderline:
                for j in range(i + 1, len(sum_of_lines)):
                    if sum_of_lines[j] > borderline:
                        if i - j > minimum_line_height: #как раз тут смотрим длину минимума
                            subarrays.append((i, j))
                        i = j + 1
                        break
        

        (width, ) = pic_handler.image.shape


        top = 0
        bottom = 0
        for i in range(len(subarrays)):
            top = bottom
            bottom = np.min(sum_of_lines[subarrays[i][0] : subarrays[i][1]]) #находим самый минимум из минимумов
            #box = (0, top, width, bottom) #координаты строки
            lines.append(PicHandler(binary_matrix[top : bottom + 1]))

        return lines

    

    def words_segmentation(line_pic_handler:PicHandler, minArea = 300)
        SIZE = 40

        image = line_pic_handler.img

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gradX = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 1, dy = 0, ksize = -1)
        gradY = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 0, dy = 1, ksize = -1)
        gradient = cv2.subtract(gradX, gradY)
        gradient = cv2.convertScaleAbs(gradient)
"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (27, 21))
        closed = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, kernel)
        closed = cv2.erode(closed, None, iterations = 4)
        closed = cv2.dilate(closed, None, iterations = 4)

        (components, _) = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blocks = [] 
        for c in components:
            if cv2.contourArea(c) < minArea:
                continue
            currBox = cv2.boundingRect(c) 
            (x, y, w, h) = currBox
            currImg = image[y:y+h, x:x+w]
            blocks.append((currBox, currImg))
        sorted(blocks, key=lambda entry:entry[0][0])

        words = []
        for block in blocks:
            word = PicHandler(block[1])
            word.resize(word.img, (SIZE, SIZE))
            words.append(word)
        return words
 """
        kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (21, 17))  
        closed = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, kernel)
        #closed = cv2.erode(closed, None, iterations = 4)
        closed = cv2.dilate(closed, None, iterations = 2)
        (components, _) = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        res = []
        for c in components:
            if cv2.contourArea(c) < minArea:
                continue
            currBox = cv2.boundingRect(c) 
            (x, y, w, h) = currBox   
            currImg = image[y:y+h, x:x+w]
            res.append((currBox, currImg))
            print(cv2.contourArea(c))
        #return closed
        #Вернется список, отсортированный по х, из ( (x, y, width, height), img ) Тип координаты и слово или компонент связности. 
        return sorted(res, key=lambda entry:entry[0][0])





