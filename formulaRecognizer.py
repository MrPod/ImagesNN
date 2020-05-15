from typing import *

import letter_db as ldb
import numpy as np
from TextBlock import TextBlock
from PicHandler import PicHandler
#from _parser import Parser
from ElemBlock import ElemBlock
from formula import Formula
import mask
from _my_parser import Parser
from decoder import math_classes

path = 'C:\\Users\\Юзверь\\PycharmProjects\\math_formulas\\m_math1_1.ldb'
baretsky_path = 'C:\\Users\\Юзверь\\PycharmProjects\\math_formulas\\math_baretksy.ldb'
skel_path = 'C:\\Users\\Юзверь\\PycharmProjects\\math_formulas\\s_math1_1.ldb'



class FormulaRecognizer:
    @staticmethod
    def recBlock(textBlock: TextBlock):
        my_ldb = ldb.LetterDB(path, ldb.Comparator())
        my_ldb.comparator = mask.Comparator
        #mask.Comparator.proportional = False

        c = ldb.Classificator(my_ldb)
        ar = textBlock.getImg().blocksOfPixels()
        out = c.signal(ar)

        for i in range(len(out)):
            if out[i] == out.max():
                res = math_classes.label_to_char(i)
                break

        return ElemBlock(res, textBlock.position)

    @staticmethod
    def read(img: Union[str, PicHandler], path: str='D:\\Project\\'):
        if isinstance(img, str):
            ph = PicHandler(img, path=path)
        else:
            ph = img
        blocks = Parser().divBlocks(img, sensivity=4, math=True)

        elemBlocks = [FormulaRecognizer.recBlock(block) for block in blocks]

        f = Formula(elemBlocks)
        print(f.texCode)
        ph._show()

if __name__ == '__main__':
    FormulaRecognizer.read("strong_1_4.jpg", "D:\\Project\\")

    for n in range(2, 10):
        print("\nf" + str(n) + ".jpg:")
        FormulaRecognizer.read("f" + str(n)+".jpg", "D:\\Project\\")
    for n in '013':
        print("\nstrong" + str(n) + ".jpg:")
        FormulaRecognizer.read("strong" + str(n) + ".jpg", "D:\\Project\\")
    for n in '01234':
        print("\nstrong_1_" + str(n) + ".jpg:")
        FormulaRecognizer.read("strong_1_" + str(n) + ".jpg", "D:\\Project\\")



# ~6, 8?
#str_1_1