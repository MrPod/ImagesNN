"""
In this file defined class Teacher and function n_to_unicode.

Class Teacher trains given nn with given dataset, using backpropagation.
Supported training with and without testing.
After each epoch state of nn is saved in file; if nn was trained with testing, stats file is also saved

Dataset is path to .h5 file with following structure:
Hdf5 file consists of two datasets:
    1. "input". Bitfields of processed images in form of byte arrays
    Shape: (number of images, number of inputs of nn // 8), stored as UINT8
    has attribute "length" - number of inputs of nn
    2. "gt". Labels of images, byte number of index in nn output vector, stored as UINT8
        index coded according to following rules:
            1. if letter == Ё then index = 64
            2. if letter == ё then index = 65
            3. otherwise index = ord(letter) - ord('А') # = ord(letter) - 1040
        Shape: (number of images)

Global constants, related to Teacher:
DEFAULT_LR: default learning rate
DEFAULT_EP: default number of epochs
DEFAULT_TR: default testing ratio - part of all dataset that was chosen for testing

Function n_to_unicode returns unicode character corresponding to index in
output array of nn

Code by Vladimir Sennov

29.02.20
Пока не дебажил особо, нужен класс PicHadler для этого
02.03.20
Обновил распаковку файла с учетом возможности представления информации незапакованными байтами
Обновил формат файла - добавил атрибут 'bit_packed', обновил описание
04.03.20
Добавил константы и сохранение в файл, протестировал обратное распространение ошибки, что-то учит
"""

import h5py
import numpy
from random import randrange
import os


DEFAULT_LR = 0.003
DEFAULT_EP = 30
DEFAULT_TR = 0.1


class Teacher:
    """
    dataset: path to '.h5' file with dataset
    nn: a NeurNet instance
    setup_name: name for this nn, subdirectory in training directory and saved nn will be named with 'setup_name'
    dir_name: name or path to training directory
    """
    def __init__(self, dataset, nn, setup_name="my_nn", dir_name="training"):
        self.nn = nn
        if os.path.isdir(dir_name):
            self.dir_name = dir_name
        else:
            self.dir_name = os.path.join(os.path.dirname(__file__), dir_name)
        if os.path.exists(os.path.join(self.dir_name, setup_name)):
            print("Warning! Setup with given name already exists! 0: change name of setup, 1: delete old setup?")
            while True:
                try:
                    i = int(input())
                    if i == 0:
                        self.setup_name = input()
                        break
                    elif i == 1:
                        self.setup_name = setup_name
                        for root, dirs, files in os.walk(os.path.join(self.dir_name, setup_name)):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(os.path.join(self.dir_name, setup_name))
                        break
                except ValueError:
                    print("Error")
                print("Invalid input")
        else:
            self.setup_name = setup_name
        os.mkdir(os.path.join(self.dir_name, self.setup_name))
        with h5py.File(dataset, "r") as f:
            dset = f["/input"]
            byte_arrays = numpy.array(dset)
            self.gt = numpy.array(f["/gt"])
            # number of inputs of nn
            m = dset.attrs.get('length')
            if dset.attrs.get('bit_packed') == 1:
                # unpacking all byte arrays
                n = len(byte_arrays)
                self.input = numpy.zeros((n, m), dtype=bool)
                for i in range(n):
                    for j in range(m):
                        self.input[i][j] = byte_arrays[i][j // 8] & (1 << (j % 8))
            else:
                self.input = byte_arrays / 255

    def teach(self, learning_rate=DEFAULT_LR, epoch=DEFAULT_EP):
        n = len(self.input)
        for e in range(epoch):
            for i in range(n):
                self.nn.setIns(self.input[i])
                res = self.nn.begin()
                self.nn.improve(self.__expected_output(self.gt[i]) - res, learning_rate)
            self.save_nn(e)

    """
    divides dataset into two parts: for training and for testing,
    tests nn after each epoch, prints result and gathers statistics
    about test_ratio of all dataset becomes testing data
    test_ratio should be between 0 and 1
    returns list with values of loss function and percentage of images where max of output is gt after each epoch
    saves nn after each epoch, after all epochs saves stats
    """
    def teach_test(self, learning_rate=DEFAULT_LR, epoch=DEFAULT_EP, test_ratio=DEFAULT_TR):
        for_test = []
        n = len(self.input)
        # choosing data for testing
        for i in range(n):
            if randrange(0, 100) / 100 <= test_ratio:
                for_test.append(i)
        m = len(for_test)
        statistics = [[], []]
        for e in range(epoch):
            count = 0
            for i in range(n):
                if count < m and i == for_test[count]:
                    count += 1
                    continue
                self.nn.setIns(self.input[i])
                res = self.nn.begin()
                self.nn.improve(res - self.__expected_output(self.gt[i]), learning_rate)
                print("Epoch:", e + 1, ". Picture", i - count + 1, "/", n - m, "picture learned")
            loss_sum = 0
            matched = numpy.zeros(m)
            i = 0
            for j in for_test:
                self.nn.setIns(self.input[j])
                out = self.nn.begin()
                error = self.__expected_output(self.gt[j]) - out
                if out.argmax() == self.gt[j]:
                    matched[i] = 1
                loss_sum += (error*error).sum()
                i += 1
            loss = loss_sum / m
            matched_avg = matched.sum() / m * 100
            print("Epoch = ", e + 1, "; Loss = ", loss, "; Max matched in", matched_avg, "%")
            statistics[0].append(loss)
            statistics[1].append(matched_avg)
            self.save_nn(e, epoch)
        with open(os.path.join(self.dir_name, self.setup_name, self.setup_name + "_stats.txt"), "w") as f:
            for i in range(epoch):
                f.write(str(i) + ' ' + str(statistics[0][i]) + ' ' + str(statistics[1][i]) + '\n')
        return statistics

    @staticmethod
    def __expected_output(label: int):
        res = numpy.zeros(66, dtype=float)
        res[label] = 1
        return res

    def save_nn(self, epoch: int, max_epoch=DEFAULT_EP):
        name = os.path.join(self.dir_name, self.setup_name, self.setup_name
                            + '_' + '0' * (len(str(max_epoch - 1)) - len(str(epoch))) + str(epoch))
        self.nn.save(name)


def n_to_unicode(index: int):
    if index < 64:
        return chr(ord(u'А'[0])+index)
    elif index == 64:
        return 'Ё'
    else:
        return 'ё'
