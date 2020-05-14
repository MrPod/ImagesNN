import numpy as np
import cv2

from PicHandler_ import PicHandler
import Triangle
import SymSpell
from Translator import Translator
from ElemBlock import ElemBlock

def pic():
    # passing different types to constructor
    a = PicHandler('A')
    a._show()
    b = PicHandler(a.img)
    b._show()
    print(np.all(a.img == b.img))

    c = a.img.copy()

    # from GRAY scale to binarized
    a.alter()
    a._show()

    # resizing
    a.resize((a.img.shape[0]//4, a.img.shape[1]//4))
    a._show()

    blocks = a.blocksOfPixels(square=True, resize=True)
    line = a.vectorOfPixels()

    a.img = c

    thin = np.vectorize(lambda _: 255 if _ else 0)(a.thinning())
    a._show(i=thin.astype(np.uint8))


def rect():
    pic = PicHandler('formulas_final')
    rects = Triangle.getRectangles(pic)
    print(rects)

    # skewed rect
    pic = PicHandler('test')
    rects = Triangle.getRectangles(pic)
    print(rects)


def spell():
    sp = SymSpell.createSymSpell()

    for word in 'папугай пчта пчто'.split():
        print(f'{word} - {SymSpell.lookupSymSpell(sp, word)[:20]}')


def tex():
    Translator([ElemBlock('a', (0, 0)), ElemBlock(r'\frac{5}{4}', (0, 1)), ElemBlock('b', (0, 2))]).translate('f')


if __name__ == '__main__':
    pic()
    rect()
    spell()
    tex()
