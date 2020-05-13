"""
Формула -- совокупность математических символов, составляющая единую семантическую единицу
Класс Formula используется для представления мат. формул; при вызове конструктора формируется tex-код,
соответствующий данной формуле
"""

from __future__ import annotations
from typing import *
from ElemBlock import ElemBlock
from pylatex import Math, NoEscape
from position import Position


FRAC = '\\frac'

class Formula:
    texCode: str
    rank: int  # ранг (важность)
    center: Tuple[int, int]
    subformulas: Dict[Union[Formula.TOP, Formula.LOW], Formula] # пределы: верхний и нижний

    TOP = 'top'
    LOW = 'low'
    HAS_LIMITS = {'\\frac', '\\int', '\\sum'}
    INF = 9999
    CENTER_DY = 0.65
    NOSYMB = {'\\frac'}
    LIMIT_DY = 0.6


    def __init__(self, elemBlocks: List[ElemBlock]):
        self.subformulas = dict()
        limits, elemBlocks = self.recognizeLimits(elemBlocks)
        self.recognize_structure(elemBlocks, limits)
        self.pos = elemBlocks[0].getPos()

    def recognizeLimits(self, elemBlocks: List[ElemBlock]) \
            -> Tuple[List[Tuple[ElemBlock, Dict[Union[Formula.TOP, Formula.LOW], ElemBlock]]], List[ElemBlock]]:
        # данный метод выделяет все подформулы, которые являются пределами; возвращает список кортежей:
        # блок-родитель -- словарь с пределами;
        # а также список оставшихся elemBlock'ов

        done = []
        res = []

        for block in elemBlocks:
            if Formula.hasLimits(block):
                topBlocks = Formula.findBlocks(block, elemBlocks, Formula.TOP)
                lowBlocks = Formula.findBlocks(block, elemBlocks, Formula.LOW)

                topLimit = Formula.uniteBlocks(topBlocks)
                lowLimit = Formula.uniteBlocks(lowBlocks)

                res.append(
                    (block, {Formula.TOP : topLimit, Formula.LOW: lowLimit})
                )

                [done.append(block) for block in (topBlocks + lowBlocks)]

        return res, [block for block in elemBlocks if block not in done]

    @staticmethod
    def uniteBlocks(blocks) -> ElemBlock:
        # метод создает tex-код для данной формулы
        Formula.sortBlocks(blocks)
        content = ''
        yLine = blocks[0].getPos().center().y
        position = blocks[0].getPos()

        for block in blocks:
            position = position.bounding_rect(block.getPos())
            direct = Formula.findDirection(yLine, block)
            if direct == 0:
                yLine = block.getPos().center().y

            content += f'{["","^","_"][direct]}{block.getOutput()}' # 0 - empty; 1 - ^; -1 - _

        content = "{" + content + "}"

        return ElemBlock(content, position)

    @staticmethod
    def hasLimits(block: ElemBlock) -> bool:
        # Возвращает True, если block содержит символ, имеющий верхний и нижний пределы, иначе False
        return block.getOutput() in Formula.HAS_LIMITS

    @staticmethod
    def findBlocks(block: ElemBlock, elemBlocks: List[ElemBlock], side: Union[Formula.TOP, Formula.LOW]) \
             -> List[ElemBlock]:
        # возвращает список блоков из elemBlocks, находящихся в стороне side от block

        def findBorders(block: ElemBlock, elemBlocks: List[ElemBlock]) -> Tuple[int, int]:
            # функция находит левую и правую границы зоны, отводимой для записи пределов block
            limitBlocks = [b for b in elemBlocks if Formula.hasLimits(b) and b != block]
            left, right = 0, Formula.INF

            for b in limitBlocks:
                pos = b.getPos()
                if pos.left() > left:
                    left = pos.left()
                elif pos.right() < right:
                    right = pos.right()

            bl, br = block.getPos().left(), block.getPos().right()

            return bl - (bl - left) / 2, br + (right - br) / 2

        res = []
        if side == Formula.TOP:
            yLine = block.getPos().top()
            sign = -1
        else:
            yLine = block.getPos().bottom()
            sign = 1

        bl, br = findBorders(block, elemBlocks)
        for b in elemBlocks:
            if b != block and bl < b.getPos().left() and br > b.getPos().right():
                if Formula.inDirection(yLine + sign * Formula.LIMIT_DY * b.getPos().h, b, side):
                    res.append(b)

        return res

    @staticmethod
    def onLine(yLine: int, block: ElemBlock) -> bool:
        cy = block.getPos().center().y
        return abs(cy - yLine) / block.getPos().h < Formula.CENTER_DY

    @staticmethod
    def inDirection(yLine: int, block: ElemBlock, side: Union[Formula.TOP, Formula.LOW]) -> bool:
        return side == Formula.TOP and block.getPos().top() < yLine or block.getPos().bottom() > yLine and side == Formula.LOW

    @staticmethod
    def sortBlocks(elemBlocks: List[ElemBlock]) -> None:
        # сортирует список блоков (в порядке возрастания горизонтальной координаты)
        elemBlocks.sort(key=lambda _: _.getPos().center().x)

    @staticmethod
    def findLimits(elemBlock: ElemBlock, limits: List) -> Dict:
        for b, d in limits:
            if b == elemBlock:
                return d

    @staticmethod
    def noSymb(string: str) -> bool:
        # Возвращает True, если данная команда Latex имеет пределы, передаваемые в аргументах {}{}
        return string in Formula.NOSYMB

    @staticmethod
    def findDirection(yLine: int, second: ElemBlock) -> int:
        # 0 -- на одном уровне; 1 -- second - степень first; -1 -- second - индекс first
        y2 = second.getPos().center().y
        if Formula.onLine(yLine, second):
            return 0
        elif yLine > y2:
            return 1
        else:
            return -1

    def recognize_structure(self, elemBlocks: List[ElemBlock], limits: List[Tuple[ElemBlock, Dict[Union, ElemBlock]]]) -> None:
        # метод создает tex-код для данной формулы
        Formula.sortBlocks(elemBlocks)
        self.texCode = ''
        yLine = elemBlocks[0].getPos().center().y

        for block in elemBlocks:
            direct = Formula.findDirection(yLine, block)
            if direct == 0:
                yLine = block.getPos().center().y

            # добавление пределов для block (если они есть)
            if Formula.hasLimits(block):
                self.texCode += block.getOutput()
                lims = Formula.findLimits(block, limits)

                symb = not Formula.noSymb(block.getOutput())


                self.texCode += '^' * symb + lims[Formula.TOP].getOutput()

                self.texCode += '_' * symb + lims[Formula.LOW].getOutput()

            else:
                self.texCode += f'{["","^","_"][direct]}{block.getOutput()}' # 0 - empty; 1 - ^; -1 - _


    def getFormula(self) -> ElemBlock(Math, Position) :
        '''
        The function to return the results
        :return: ElemBlock with Math instance, which represents the obtained formula
        '''
        return ElemBlock(Math(inline=True, data=[NoEscape(self.texCode)]), self.pos)