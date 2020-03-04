from __future__ import annotations
from typing import *
from collections import deque
from Layer import *
import pickle


class Block:
    #n: int # количество слоев
    isFirst: bool
    prevBlocks: List[Block]
    layers: List[Layer]
    res: np.array
    prevBlocksWeights: List[np.array]

    def __init__(self, nns: Tuple[int] =(1, 2), isFirst: bool =True,
                 prevBlocks: List[Block]=None, prevBlocksWeights: List[np.array]=None
                 ):
        # nns -- кол-во нейронов в каждом слое, первый элемент -- кол-во входов,
        # последний -- кол-во выходов
        self.layers = [Layer(  ins=nns[i], outs=nns[i+1]
                        )
                       for i in range(len(nns)-1)]

        self.isFirst = isFirst
        self.prevBlocks = prevBlocks
        self.prevBlocksWeights = prevBlocksWeights


        self.res = None # выходы блока

        self.nIns = self.layers[0].nIns
        self.nOuts = self.layers[-1].nOuts

    def signal(self, ins):
        res = ins
        for layer in self.layers:
            res = layer.signal(res)

        self.res = res
        return res

    def getOuts(self, ins: np.array = None)->np.array:
        # получить сигнал от предыдущих блоков и обработать
        if not self.isFirst:
            ins = np.zeros(self.nIns)
            for i in range(len(self.prevBlocks)):
                ins += self.prevBlocksWeights[i] @ self.prevBlocks[i].getOuts()

        return self.signal(ins)

    def improve(self, errors: np.array, learning_rate):
        t = 0
        for layer in reversed(self.layers):
            t = errors
            errors = layer.improve(errors, learning_rate)

        if not self.isFirst:
            outs = self.layers[0].outs
            weights_deltas = t * outs * (1 - outs)

            for i in range(len(self.prevBlocks)):
                errorsI = self.prevBlocksWeights[i] @ weights_deltas # проверить корректность
                self.prevBlocks[i].improve(errorsI, learning_rate)

    def setNThreads(self, nth: int):
        for lay in self.layers:
            lay.setNThreads(nth)

    def save(self, filename: str, i):
        pass