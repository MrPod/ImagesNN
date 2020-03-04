import numpy as np
import cv2
import os
from typing import Optional, Tuple, Union


class PicHandler:

    def __init__(self, o : Union[str, np.ndarray], path='images/'):
        if isinstance(o, str):
            s = lambda a: a.split('.', 1)
            self.name = str(*filter(lambda a: [s(a)[0]==s(o)[0], a==o][len(s(o))>1], {*os.listdir(path)}))

            if not self.name:
                raise ValueError(f'there is no image {o} in the directory {path}')
            img=cv2.imread(f'{path}{self.name}')
        else:
            self.name='.'
            img=o

        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # size = Tuple[int, int]
    resize = lambda self, size: cv2.resize(self.img, size, [cv2.INTER_AREA, cv2.INTER_CUBIC][size < self.img.shape])


    def alter(self):
        self.img = cv2.medianBlur(cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 75, 6), 3)


    _show = lambda self,n=None,i=None: [cv2.imshow(['_',self.name][n is None],[i,self.img][i is None]),cv2.waitKey(0),cv2.destroyAllWindows()]


    def blocksOfPixels(self, mode:Union[str,int]=None) -> np.ndarray:
        if mode:
            try:
                mode = int(mode)
            except (ValueError, TypeError):
                raise Exception(f'"{mode}" cannot be converted to int')
            return np.vectorize(lambda _: min(_, mode))(self.img)
        return self.img


    vectorOfPixels = lambda self: self.img.flatten()