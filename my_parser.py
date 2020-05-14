from main_points import wave, components, bounding_rect, any_point
from PicHandler import PicHandler
from TextBlock import TextBlock
from position import Position
from collections import deque
import _parser as ps
import cv2
import numpy as np
import os
from Triangle import getRectangles


def assert_p(ar, p):
    return 0 <= p[0] < ar.shape[0] and 0 <= p[1] < ar.shape[1]
    
def close_range2d(min_val, max_val):
    for s in range(min_val * 2, 2 * max_val - 1):
        for i in range(min_val, s + 1):
            if i < max_val and s - i < max_val and s - i >= min_val:
                yield i, s - i


def wave_v2(ar, start, sensivity):
    q = deque()
    q.append(start)
    #print('started')
    visited = np.zeros_like(ar)
    visited[start] = 1
    max_x = 0
    while len(q):
        #print(len(q))
        p = q.pop()
        #if p[0] - max_x > sensivity:
        #    print(p)
        if p[0] > max_x:
            max_x = p[0]
        #if ar[max(0, p[0] - sensivity // 2):min(ar.shape[0], p[0] - sensivity // 2), \
        #    max(0, p[1] + sensivity // 2):min(ar.shape[1], p[1] + sensivity // 2)].sum() < \
        #    sensivity * sensivity / 4:
        #        continue
        count = 0
        for i in range(sensivity):
            for j in range(sensivity - i + 1):
                points = [(p[0] + i, p[1] + j), (p[0] - i, p[1] + j), (p[0] + i, p[1] - j), (p[0] - i, p[1] - j)]
                for p1 in points:
                    if assert_p(ar, p1) and ar[p1] and not visited[p1]:
                            if p1[0] - p[0] > sensivity:
                                print(p1)
                            visited[p1] = 1
                            q.appendleft(p1)
        yield p


        '''
        for i, j in close_range2d(1, sensivity):
            if i + j >= sensivity * 0.7 and count == 0:
                break
            points = [(p[0] + i, p[1] + j), (p[0] - i, p[1] + j), (p[0] + i, p[1] - j), (p[0] - i, p[1] - j)]
            for p1 in points :
                if assert_p(ar, p1) and ar[p1]:
                    count +=1 
                    if not visited[p1]:
                        visited[p1] = 1
                        q.appendleft(p1)
        '''
                       

def components_v2(ar, sensivity):
    ar2 = ar.copy()
    while ar2.sum() > 0:
        p = any_point(ar2)
        comp = np.zeros_like(ar2)
        max_x = -1 
        for p1 in wave_v2(ar2, p, sensivity):
            comp[p1] = 1
        ar2 -= comp
        yield comp, p


def ph_from_array(ar):
    return PicHandler(np.full_like(ar, 255) - 255 * ar)

def slice_from_pos(ar, pos):
    return ar[pos.x : pos.x + pos.w, pos.y : pos.y + pos.h]


# img - либо путь (str), либо PicHandler, либо np.ndarray (да и вообще все, что можно в пикхендлер положить)
# если img - это np.ndarray, то если в нем максимальное значение 1, а минимальное 0, то все автоматически инвертируется
class Parser:
    @staticmethod
    def divBlocks(img, path: str=None, sensivity=15, swap_coordinates=True):
        ph = None
        if isinstance(img, str):
            if path != None:
                ph = PicHandler(img, path)
            else:
                head, tail = os.path.split(img)
                if head:
                    ph = PicHandler(tail, head)
                else:
                    ph = PicHandler(img)
        elif isinstance(img, PicHandler):
            ph = img
        elif isinstance(img, np.ndarray):
            if min(img) == 0 and max(img) == 1:
                ph = PicHandler(np.full_like(img, 255) - 255 * img)
            else:
                ph = PicHandler(img)
        else:
            ph = PicHandler(img)
        ph.alter()
        rects = sorted(getRectangles(ph), key=lambda tb: tb.getPos().y)
        for r in rects:
            pos = r.getPos()
            # хочу стереть формулу с листа
            ph.img[pos.y - 5: pos.y + pos.h + 10, pos.x - 5: pos.x + pos.w + 10].fill(255)
            #pre_parsed = Parser.parse(<массив>, sensivity=4, merge='math')

        lines = [tb for tb in ps.Parser.line_segmentation(ph.blocksOfPixels()) if tb.getPos().h > 10]
        text_blocks = []
        for line in lines:
            words = Parser.word_segmentation(line, sensivity)
            text_blocks.extend(words)
        return text_blocks, rects
        
    @staticmethod
    def line_segmentation(img):
        return [tb for tb in ps.Parser.line_segmentation(img) if tb.getPos().h > 10]
        
    @staticmethod
    def word_segmentation(line, sensivity):
        pre_parsed = ps.Parser.word_segmentation(line.getImg().blocksOfPixels(), line.getPos().y, sensivity * 1.5)
        res = []
        for tb in pre_parsed:
            if tb.getPos().w < sensivity:
                continue
            merge = (sensivity > 10)
            parsed = sorted(Parser.parse(tb.getImg().blocksOfPixels(), sensivity, merge), key=lambda x: x.getPos().y)
            Parser.swap_coordinates(parsed)
            for tb2 in parsed:
                tb2.position.x += tb.getPos().x
                tb2.position.y += tb.getPos().y
                res.append(tb2)
        return res
            
        
    
    @staticmethod
    def swap_coordinates(pos):
        if isinstance(pos, list):
            for tb in pos:
                Parser.swap_coordinates(tb.position)
        else:
            pos.x, pos.y = pos.y, pos.x
            pos.w, pos.h = pos.h, pos.w
    
    @staticmethod            
    def parse(ar, sensivity, merge):
        blocks = []
        if isinstance(merge, str):
            can_merge = Parser.is_equals_sign
        elif merge:
            can_merge = Parser.can_merge
            #print('Мёржим пацаны')
        else:
            can_merge = lambda p1, p2: False
        for comp, p in components_v2(ar, sensivity):
            if comp.sum() < 3 * sensivity:
                continue
            x, y, w, h = bounding_rect(comp)
            pos = Position(x, y, w, h)
            to_merge = []
            for b in blocks:
                if can_merge(b[0], pos):
                    to_merge.append(b)
            for b in to_merge:
                #print('merging', pos, b[0])
                comp += b[1]
                pos = pos.bounding_rect(b[0])
                blocks.remove(b)
            blocks.append((pos, comp))
        return [TextBlock(b[0], ph_from_array(slice_from_pos(b[1], b[0]))) for b in blocks]
        
    # разделяем на диакритику и буквы
    # -> List[TextBlock], List[TextBlock]: не диакритика, диакритика
    @staticmethod
    def divide_diacritic(text_blocks):
        if len(text_blocks) == 0:
            return [], []
        diacritic = []
        non_diactic = []
        h_line = 0
        for tb in text_blocks:
            h_line += tb.getPos().x
        h_line /= len(text_blocks)
        for tb in text_blocks:
            if tb.getPos().x + tb.getPos().w < 1.5 * h_line:
                diacritic.append(tb)
            else:
                non_diactic.append(tb)
        return non_diactic, diacritic
        
        
    @staticmethod
    def pre_parse(line):
        print('')
        
    @staticmethod    
    def is_equals_sign(p1, p2):
        if p1.h / p1.w > 2 and p2.h / p2.w > 2 \
        and (p1.y <= p2.y < p1.y + p1.h or p2.y <= p1.y < p2.y + p2.h) \
        and abs(p1.h - p2.h) < 0.4 * (p1.h + p2.h) \
        and abs(p1.x - p2.x) < 2 * min(p1.h, p2.h):
            return True
        return False

    @staticmethod    
    def can_merge(p1, p2):
        h_dif = abs(p1.center().y - p2.center().y)
        #print(p1, p2)
        if (p1.y <= p2.y <= p1.y + p1.h or p2.y <= p1.y <= p2.y + p2.h):
            #print('yes')
            return True
        #print('no')
        return False
    
    '''
    @staticmethod    
    def can_merge(p1, p2):
        h_dif = abs(p1.center().y - p2.center().y)
        if not (p1.x <= p2.x <= p2.x + p2.w <= p1.x + p1.w or p2.x <= p1.x <= p1.x + p1.w <= p2.x + p2.w) and \
            (p1.y <= p2.y <= p2.y + p2.h <= p1.y + p1.h or p2.y <= p1.y <= p1.y + p1.h <= p2.y + p2.h) and \
            h_dif < max(p1.h, p2.h) * 1.8:            
            return True
        return False
    '''
if __name__ == '__main__':
    Parser.divBlocks('test_parse.jpg')
