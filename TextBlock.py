from PicHandler import PicHandler
import numpy as np

from Position import *

class TextBlock:

    def __init__ (self, position:Position, pic_handler:PicHandler):
        self.position = position
        self.pic_handler = pic_handler

    __repr__ = __str__ = lambda self: f'{self.position} {self.pic_handler}'

    def getPos(self) -> Position:
        return self.position

    def getImg(self) -> PicHandler:
        return self.pic_handler