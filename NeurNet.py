from Block import *
import saving


def interpretRes(res: np.array):
    #vars = [i for i in range(10)]
    t = max(res)

    return list(res).index(t)



class NeurNet:
    first : Block
    last : Block
    ins : np.array
    def __init__(self, first: Block, last: Block):
        self.first = first
        self.last = last

        self.ins = None # входы нейросети

    def begin(self) -> np.array:
        return self.last.getOuts(self.ins)

    def setIns(self, ins): # установить входы в нейросеть
        if (len(ins) != self.first.nIns):
            print(len(ins))
            raise Exception("Длина столбца входов")

        self.ins = ins

    def getIns(self):
        return self.ins

    def improve(self, errors, learning_rate):
        self.last.improve(errors, learning_rate)

    def save(self, filename: str ='default'):
        saving.saveObj(self, filename + '.nn')

    def load(self, filename: str ='default'):
        nn = saving.loadObj(filename + '.nn')
        self.first, self.last, self.ins = nn.first, nn.last, nn.ins

    def stopRes(self):
        pass