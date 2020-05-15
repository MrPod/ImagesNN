import os

from my_parser import Parser
from formulaRecognizer import FormulaRecognizer
from Translator import Translator
from my_rec import Recognizer
from letter_db import Classificator, LetterDB
import letter_db as ldb
from formula import Formula
from ElemBlock import ElemBlock
from position import Position

rec_path = "C:\\Users\\Юзверь\\PycharmProjects\\math_formulas\\test2.ldb"

class Reader:

    def __init__(self, filename: str, path='images/'):
        s = lambda a: a.split('.', 1)
        *a, = filter(lambda a: [s(a)[0] == s(filename)[0], a == filename][len(s(filename)) > 1], {*os.listdir(path)})

        if len(a) > 1:
            raise ValueError(f'there are two or more files with such a name "{filename}" in the directory "{path}" - '
                             'try to specify the extension of a file')
        elif not len(a):
            raise ValueError(f'there is no image "{filename}" in the directory "{path}"')
        else:
            self.name = a[0]

    @staticmethod
    def read(img_name: str, path="D:\\Project\\"):
        text_blocks, formula_blocks = Parser.divBlocks(img_name, path)
        #[block.getImg()._show() for block in text_blocks + formula_blocks]
        blocks = [FormulaRecognizer.read(block.getImg()) for block in formula_blocks]


        cl = Classificator(LetterDB(rec_path, ldb.Comparator()))
        for tb in text_blocks:
            rc = Recognizer(tb, cl)
            blocks.append(rc.recognize())
        #blocks = [ElemBlock(str(i), Position(i*5, i*5, 50, 50)) for i in range(0, 401, 100)]
        t = Translator(blocks)
        t.translate('test')

if __name__ == '__main__':
    Reader.read("test_2.jpg")