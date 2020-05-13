import numpy as np
import cv2
from pythreshold.utils import *
from operator import mul
from typing import List

from TextBlock import TextBlock
from PicHandler import PicHandler
from Position import Position


__all__ = ['getRectangles']
__version__ = '0.1.1'


def rotate(image, angle, center=None, scale=1.0):
    # grab the dimensions of the image
    (h, w) = image.shape[:2]

    # if the center is None, initialize it as the center of
    # the image
    if center is None:
        center = (w // 2, h // 2)

    # perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    # return the rotated image
    return rotated


def getRectangles(pic : PicHandler) -> List[TextBlock]:

    # PicHandler trap
    pic.img = ~pic.img
    bw = apply_threshold(pic.img, bradley_roth_threshold(pic.img))

    contours, hierarchy = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) # RETR_EXTERNAL

    co = []

    for n, (c, h) in enumerate(zip(contours, hierarchy[0])):
        # not the full-image frame, area is bigger than 64 and contour was count twice, leave the smallest (inner)
        if pic.img.shape[0]*pic.img.shape[1]*0.8 > cv2.contourArea(c) > mul(*pic.img.shape[:2])**.5 and cv2.contourArea(contours[n]) > cv2.contourArea(contours[h[3]]) * 0.2:
            co.append(c)

    rects = []

    for n,con in enumerate(co):
        rect = cv2.minAreaRect(con)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        hy = lambda a,b: ((a[0]-b[0])**2+(a[1]-b[1])**2)**.5

        a, b, c, d = box
        hh, _h = hy(a, d),hy(a, b)
        if hh < _h:
            a, b, c, d = b, c, d, a
        else:
            hh, _h = _h, hh

        x,y,w,h = cv2.boundingRect(box)
        rect = pic.img[y:y+h, x:x+w]
        #cv2.rectangle(pic.img, (x,y), (x+w, y+h), (0, 255, 0), 2)
        #cv2.drawContours(pic.img, [box], 0, (0, 0, 255), 2)

        x,y = d[0]-c[0],d[1]-c[1]
        angle = eval(f'{"-"*(x<0)}{np.degrees(np.arcsin([min(abs(x),abs(y)) / hy(c,d)])[0])}')
        n_rec = rotate(rect, -angle)
        h,w =n_rec.shape[:2]
        nn_rec = n_rec[h//2-int(hh//2):h//2+int(hh//2), w//2-int(_h//2):w//2+int(_h//2)]

        rects.append(TextBlock(Position(x, y, w, h), PicHandler(nn_rec)))
        
        #cv2.imwrite(f'images/____{n}{pic.name}', nn_rec)

    return rects


'''
Usage:

if __name__ == '__main__':
    c = PicHandler('formulas_final')
    rects = getRectangles(c)

    print(len(rects),rects)
    
'''

