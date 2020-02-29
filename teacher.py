"""
In this file defined class Teacher and function n_to_unicode.

Class Teacher trains given nn with given dataset, using backpropagation.
Dataset is path to .h5 file with following structure:
Hdf5 file consists of two datasets:
1. "input". Bitfields of processed images in form of byte arrays
    Shape: (number of images, number of inputs of nn // 8). Stored as UINT8
    Has attribute "length" - number of inputs of nn
2. "gt". Labels of images, unicode of cyrillic character. Stored as UINT16
    Shape: (number of images)

Function n_to_unicode returns unicode character corresponding to index in
output array of nn

Code by Vladimir Sennov

29.02.20
Пока не дебажил особо, нужен класс PicHadler для этого

"""

import h5py
import numpy
from random import randrange


class Teacher:
    def __init__(self, dataset, nn):
        self.nn = nn
        with h5py.File(dataset, "r") as f:
            dset = f["/input"]
            byte_arrays = numpy.array(dset)
            self.gt = numpy.array(f["/gt"])
            # number of inputs of nn
            m = dset['length']
        # unpacking all byte arrays
        n = len(byte_arrays)
        self.input = numpy.zeros((n, m), dtype=bool)
        for i in range(n):
            for j in range(m):
                self.input[i][j] = byte_arrays[i][j // 8] & (1 << (j % 8))

    def teach(self, learning_rate: float, epoch: int):
        n = len(self.input)
        for e in range(epoch):
            for i in range(n):
                self.nn.setIns(self.input[i])
                res = self.nn.begin()
                self.nn.improve(self.__expected_output(self.gt[i]) - res, learning_rate)

    """
    divides dataset into two parts: for training and for testing,
    tests nn after each epoch, prints result and gathers statistics
    about test_ratio of all dataset becomes testing data
    test_ratio should be between 0 and 1
    returns list with values of loss function after each epoch
    """
    def teach_test(self, learning_rate: float, epoch: int, test_ratio: float):
        for_test = []
        n = len(self.input)
        # choosing data for testing
        for i in range(n):
            if randrange(0, 100) / 100 <= test_ratio:
                for_test.append(i)
        statistics = []
        for e in range(epoch):
            count = 0
            for i in range(n):
                if i == for_test[count]:
                    count += 1
                    continue
                self.nn.setIns(self.input[i])
                res = self.nn.begin()
                self.nn.improve(self.__expected_output(self.gt[i]) - res, learning_rate)
            loss_sum = 0
            for j in for_test:
                self.nn.setIns(self.input[j])
                error = self.__expected_output(self.gt[j]) - self.nn.begin()
                loss_sum += (error*error).sum()
            loss = loss_sum/len(for_test)
            print("Epoch = ", e, "; Loss = ", loss)
            statistics.append(loss)
        return statistics

    @staticmethod
    def __expected_output(unicode: int):
        res = numpy.zeros(66, dtype=float)
        res[unicode-ord(u'А'[0])] = 1
        return res


def n_to_unicode(index: int):
    return chr(ord(u'А'[0])+index)
