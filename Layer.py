import numpy as np
from math import *

from QueueTh import *

def sigmoid(x):
    return 1/(1+e**(-x))

def dsigmoid(x):
    s = sigmoid(x)
    return s*(1-s)

def improveLast(error, res, weights, ins, learning_rate):
    # корректно работает только для функции sigmoid
    #error = res - correct
    weights_delta = error * res * (1 - res)

    for i in range(len(ins)):
        weights[i] = weights[i] - ins[i] * weights_delta * learning_rate
    return weights_delta

def improveHidden(weights, weights_delta, res, ins, learning_rate):
    error = weights * weights_delta
    return improveLast(error, res, weights, ins, learning_rate)

class Layer:
    nIns : int
    nOuts : int
    weights: np.array # [int, int]
    ins: np.array
    outs: np.array
    nThreads: int
    #func: function
    #dfunc: function

    def __init__(self, ins: int, outs: int, weights: np.array =None,
                 func = sigmoid, dfunc=dsigmoid, nThreads=4):
        try:
            if not weights:
                weights = np.random.sample((outs, ins))
                weights *= 2
                weights -= 1 # значения из отрезка [-1, 1]
        except:
            pass

        if weights.shape != (outs, ins):
            raise Exception("Матрица весов")
        self.nIns = ins
        self.nOuts = outs
        self.nThreads = nThreads

        self.weights = weights
        print(weights)
        self.func = func
        self.dfunc = dfunc

    def signal(self, ins: np.array):
        if len(ins) != self.nIns:
            raise Exception("Количество входов")

        self.ins = ins
        res = self.weights.dot(ins)

        #res /= len(ins) # убрать это к черту
        for i in range(len(res)):
            res[i] = self.func(res[i])
        self.outs = res
        return res

    def setNThreads(self, nth: int):
        self.nThreads = nth

    def improveOne(self, j, weights_delta, learning_rate):
        # изменяет значение весов связей, входящих в j-й нейрон
        for i in range(len(self.ins)):
            self.weights[j][i] -= self.ins[i] * weights_delta * learning_rate

    def improve(self, errors: np.array, learning_rate):
        # корректно работает только для функции sigmoid
        weights_deltas = errors * self.outs * (1 - self.outs) # столбец дельт весов для каждого выхода
        QueueTh(funcs=[lambda: self.improveOne(i, weights_deltas[i], learning_rate) for i in range(len(errors))],
                args=[
                    tuple() for i in range(len(errors))
                ],
                nThreads=self.nThreads
        ).start()
        # запускается черырехпоточная обработка указанных функций с указанными аргументами


        return weights_deltas.dot(self.weights) # столбец ошибок предыдущих нейронов

