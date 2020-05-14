from __future__ import annotations
from typing import *
import numpy as np
from position import Position
from TextBlock import TextBlock
from PicHandler import PicHandler
from collections import deque

INF = 999999

def distance(pos1: Position, pos2: Position) -> int:
    if pos1.intersects(pos2):
        return 0

    dx = min(abs(pos1.x - pos2.x), abs(pos1.x + pos1.w - pos2.x), abs(pos1.x + pos1.w - pos2.x - pos2.w), abs(pos1.x - pos2.x - pos2.w))
    dy = min(abs(pos1.y - pos2.y), abs(pos1.y + pos1.h - pos2.y), abs(pos1.y + pos1.h - pos2.y - pos2.h), abs(pos1.y - pos2.y - pos2.h))

    return max(dx, dy)

def components_near(c1: List[int], c2: List[int], table: List[Tuple[int, int]], max_dist: int =1) -> bool:
    d = distance(find_component_position(c1, table), find_component_position(c2, table))
    if d > max_dist:
        return False
    else:
        # прямоугольники, описанные около компонент, пересекаются или находятся на малом расстоянии
        for v1 in c1:
            for v2 in c2:
                p1 = table[v1]
                p2 = table[v2]
                if max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1])) <= d:
                    return True

        return False


def get_near_positions(position: Tuple[int, int], maxX: int, maxY: int, minX: int =0, minY: int =0, max_dist: int =1)\
        -> List[Tuple[int, int]]:
    res = []
    for dx in range(-max_dist, max_dist + 1):
        for dy in range(-max_dist, max_dist + 1):
            pos = (position[0]+dx, position[1]+dy)
            if minX <= pos[0] <= maxX and minY <= pos[1] <= maxY and pos != position:
                res.append(pos)
    return res

def create_lists(img_matrix: np.ndarray, max_dist: int =1) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
    # возвращает списки смежности для графа, соответствующего изображению, и таблицу соответствий № -- позиция
    res = []
    table = []
    for i in range(len(img_matrix)):
        for j in range(len(img_matrix[i])):
            if img_matrix[i, j]:
                pos = (i, j)
                table.append(pos)

    l = len(img_matrix)
    for v in range(len(table)):
        res.append([])
        pos = table[v]
        near_positions: List[Tuple[int, int]] = get_near_positions(pos, len(img_matrix) - 1, len(img_matrix[0]) - 1, max_dist=max_dist)

        for near_pos in near_positions:
            if img_matrix[near_pos]:
                res[-1].append(table.index(near_pos))

    return res, table

def find_connected_components(lst: List[List[int]]) -> List[List[int]]:
    # возвращает список компонент связности в графе
    used: List[bool] = [False for _ in range(len(lst))]
    res = []
    d = deque()

    for v in range(len(lst)):
        if not used[v]:
            res.append([])
            d.append(v)

            while len(d):
                v = d.pop()
                used[v] = True
                res[-1].append(v)
                for u in lst[v]:
                    if not used[u]:
                        used[u] = True
                        d.append(u)
                        res[-1].append(u)

    return res

def find_component_position(verteces: List[int], table) -> Position:
    # возвращает Position, соответствующую данной компоненте связности (вписывает множество вершин в прямоугольник)
    r, b = 0, 0
    l, t = INF, INF

    for v in verteces:
        x, y = table[v]
        if x < l:
            l = x
        if x > r:
            r = x
        if y < t:
            t = y
        if y > b:
            b = y

    return Position(l, t, r - l, b - t)

def unite_components(components: List[List[int]], pos_table: List[Tuple[int, int]], max_dist: int) -> List[List[int]]:
    res = []
    to_unite = [[] for _ in range(len(components))]

    for i in range(len(components)):
        c = components[i]
        for j in range(len(components)):
            c_other = components[j]

            if components_near(c, c_other, pos_table, max_dist):
                to_unite[i].append(j)

    comps = find_connected_components(to_unite)
    for comp_comp in comps:
        cmp = []
        for comp in comp_comp:
            cmp += components[comp]
        res.append(cmp)

    return res

def create_segment_matrix(img_matrix: np.ndarray, pos: Position, component: List[int], table: List[Tuple[int, int]]) -> np.ndarray:
    img_matrix = img_matrix.copy()
    for i in range(pos.x, pos.x + pos.w + 1):
        for j in range( pos.y, pos.y + pos.h + 1):
            if img_matrix[i, j] and (table.index((i, j)) not in component):
                img_matrix[i, j] = 0

    return img_matrix[pos.x: pos.x + pos.w + 1, pos.y: pos.y + pos.h + 1]

def unite_equal(connected_components: List[List[int]], table: List[Tuple[int, int]]) -> List[List[int]]:
    deleted = set()
    l = len(connected_components)
    i = 0
    while i < l:
        if i in deleted:
            i += 1
            continue
        j = i + 1
        while j < l:
            if j in deleted:
                j += 1
                continue
            p1, p2 = find_component_position(connected_components[i], table), find_component_position(connected_components[j], table)
            if Parser.is_equals_sign(p1, p2):
                connected_components[i] += connected_components.pop(j)
                deleted.add(j)
                j -= 1
                l -= 1

            j += 1
        i += 1

    return connected_components

class Parser:
    MIN_SPACE_TEXT = 60
    MIN_SPACE_FORMULA = 3
    MIN_COMPONENT_SIZE = 40
    @staticmethod
    def divBlocks(img_name: str, path: str ='D:\\Project\\', math: bool =True) -> List[TextBlock]:
        # math -- режим математических формул -> миним. расст. между разными блоками min_dist = 2
        text_blocks = []

        if math:
            min_dist = Parser.MIN_SPACE_FORMULA
        else:
            min_dist = Parser.MIN_SPACE_TEXT

        ph = PicHandler(img_name, path=path)
        ph.alter()._show()
        img_matrix = ph.blocksOfPixels()

        lists, table = create_lists(img_matrix, 1)

        connected_components = find_connected_components(lists)
        l = len(connected_components)
        i = 0
        while i < l:
            if len(connected_components[i]) < Parser.MIN_COMPONENT_SIZE:
                connected_components.pop(i)
                l -= 1
            else:
                i += 1

        connected_components = unite_components(connected_components, table, min_dist-1)
        connected_components = unite_equal(connected_components, table)

        for comp in connected_components:
            position = find_component_position(comp, table)

            sm = create_segment_matrix(img_matrix, position, comp, table)
            pic_handler = PicHandler(np.full_like(sm, 255) - 255 * sm)

            position.x, position.y = position.y, position.x
            position.w, position.h = position.h, position.w


            text_blocks.append(TextBlock(position, pic_handler))

        return text_blocks

    @staticmethod
    def is_equals_sign(p1, p2):
        if p1.h / p1.w > 2 and p2.h / p2.w > 2 \
                and (p1.y <= p2.y < p1.y + p1.h or p2.y <= p1.y < p2.y + p2.h) \
                and abs(p1.h - p2.h) < 0.4 * (p1.h + p2.h) \
                and abs(p1.x - p2.x) < 2 * min(p1.h, p2.h):
            return True
        return False

    @staticmethod

    def line_segmentation(img: np.ndarray) -> List[TextBlock]:
        empty = True
        v_borders = []
        top = 0

        for i in range(len(img)):
            if empty and img[i].any():
                # пустые строки закончились
                top = i
                empty = False

            elif not empty and img[i].any() == False:
                # в данной строке все нули, и до данного момента были непустые строки
                empty = True
                v_borders.append((top, i))


        res = []
        for top, bottom in v_borders:
            if (top, bottom) == (0, 0):
                continue

            m = img[top: bottom]
            if not len(m):
                continue
            ph = PicHandler(np.full_like(m, 255) - 255 * m)

            res.append(TextBlock(Position(0, top, len(img[0]), len(m)), ph))

        return res

    @staticmethod
    def word_segmentation(img: np.ndarray, y: int, min_space: int =1) -> List[TextBlock]:
        # min_space -- минимальный размер пробела
        empty = True
        h_borders = []
        left = 0
        last_not_empty = -1

        for i in range(len(img[0])):
            if img[:, i].any():
                if empty:
                    left = i
                    empty = False
                last_not_empty = i
            elif not empty and (i - last_not_empty >= min_space):
                empty = True
                h_borders.append((left, last_not_empty + 1))


        res = []
        for left, right in h_borders:
            if (left, right) == (0, 0):
                continue

            m = img[: , left: right]
            if not len(m):
                continue
  
            ph = PicHandler(np.full_like(m, 255) - 255 * m)

            res.append(TextBlock(Position(left, y, len(m[0]), len(m)), ph))

        return res


def test_sementation(img_name):
    p = PicHandler(img_name, path='D:\\Project\\')
    p.alter()
    p._show()
    bs = Parser.line_segmentation(p.blocksOfPixels())
    line = None
    for b in bs:
        print(b.getPos())
        if b.getPos().h > 10 and line == None:
            words = Parser.word_segmentation(b.getImg().blocksOfPixels(), b.getPos().top(), min_space=15)
            for word in words:
                word.getImg()._show()



def main(img_name):
    bs = Parser().divBlocks(img_name, math=True)
    for b in bs:
        print(b.getPos())

        b.getImg()._show()

if __name__ == '__main__':
    '''test_sementation('formulas_final.jpg')'''
    for i in range(10):
        img_name = 'f'+str(i)+'.jpg'
        main(img_name)
