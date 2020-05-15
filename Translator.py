from operator import methodcaller, attrgetter
from typing import List

from ElemBlock import ElemBlock
from pylatex import Document, Package, NoEscape
from formula import Formula


__version__ = '0.1.2'


class Translator:

    def __init__(self, blocks: List[ElemBlock]):
        blocks.sort(key=lambda _: attrgetter('y','x')(methodcaller('getPos')(_)))
        t, self.blocks = 0, []
        e = lambda _: "".join(map(methodcaller("getOutput"), blocks[t:_]))

        for n, (f, s) in enumerate(zip(blocks, blocks[1:])):
            if t != n and (s.getPos().y - f.getPos().y) > Formula.LIMIT_DY*(f.getPos().h + s.getPos().h)//2:
                self.blocks.append(ElemBlock(e(n), blocks[t].getPos()))
                t = n
        if t != len(blocks):
            self.blocks.append(ElemBlock(e(len(blocks)+1), blocks[t].getPos()))


    def translate(self, filename: str):
        doc = Document('basic')

        doc.append(NoEscape(r'\noindent'))

        for block in self.blocks:
            doc.append(NoEscape(block.getOutput()+'\\\\'))

        babel = Package('babel', 'english, russian')
        fontenc = Package('fontenc', 'T2A')
        inputenc = Package('inputenc', 'utf8')
        doc.packages.items = [fontenc,  inputenc, babel]

        doc.generate_tex(filename)
        try:
            doc.generate_pdf(filename, clean_tex=False)
        except Exception as e:
            print(e)

'''
Usage

if __name__ == '__main__':

    r = __import__('random').randint
    blocks = [ElemBlock(chr(_%26+65), Position(r(0, 80),r(0, 80),r(0, 80),r(0, 80)))for _ in range(40)]
    Translator(blocks).translate('g')
    Translator([ElemBlock('a', Position(0,0, 0, 0)), ElemBlock(r'$\frac{5}{4}$', Position(0,1, 0, 0)), ElemBlock('b', Position(0,2, 0, 0))]).translate('f')
    
'''
