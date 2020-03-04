"""
In this file defined class Dataset and function for creating array of bytes
from array of bool.

Class Dataset loads datasets "CoMNIST" and "Olga" (dataset has no official name)
into memory, preprocesses all images and saves into hdf5 file.
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

Datasets:
    CoMNIST dataset: https://github.com/GregVial/CoMNIST
    "Olga" dataset: https://www.kaggle.com/olgabelitskaya/classification-of-handwritten-letters

Code by Vladimir Sennov

Notes:
29.02.20
Пока не дебажил особо, нужен класс PicHadler для этого  -Vovan

"""

import os
import numpy
import h5py
from PIL import Image
import csv
from PicHandler import PicHandler


class DataSet:

    # pass name of resulting hdf5 file as name
    def __init__(self, name):
        self.name = name
        self.images = []
        self.gt = []
        self.__size = 0
        self.isPacked = 0
        self.__count = 0

    def load_comnist_dataset(self, source, size: int):
        for root, dirs, files in os.walk(source):
            label = os.path.basename(root)
            # if we are currently in directory with .png files
            # we don't need 'I' pictures in dataset
            if len(dirs) == 0 and label != u'I':
                for name in files:
                    if label == 'Ё':
                        index = 64
                    else:
                        index = ord(label) - ord('А')
                    self.__add_picture(os.path.join(source, root, name), index, size)

    def load_olga_dataset(self, source, size: int):
        sections = ['letters', 'letters2', 'letters3']
        for sec in sections:
            with open(os.path.join(source, sec+'.csv')) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    label = int(row['label'])
                    # letter is ё, ё is moved to the back of list
                    if label == 7:
                        label = 65
                    # index should be shifted for letter goes after ё
                    elif label > 7:
                        label += 30
                    # index
                    else:
                        label += 31
                    name = row['file']
                    self.__add_picture(os.path.join(source, sec, name), label, size)

    def create_db(self):
        # inpt = numpy.array(self.images)
        gt = numpy.array(self.gt)
        with h5py.File(self.name+".h5", "w") as f:
            # dset = f.create_dataset("input", numpy.shape(inpt), dtype=h5py.h5t.STD_U8BE, data=inpt)
            dset = f.create_dataset("input", (self.__count, self.__size * self.__size),
                                    dtype=h5py.h5t.STD_U8BE, data=self.images)
            f.create_dataset("gt", (self.__count,), dtype=h5py.h5t.STD_U8BE, data=gt)
            dset.attrs['length'] = self.__size * self.__size
            dset.attrs['bit_packed'] = self.isPacked

    def __add_picture(self, filename, label, size):
        # preprocessing letter, converting to bitmap
        pict = PicHandler(Image.open(filename))
        pict.alter()
        pict.resize((size, size))
        ar = pict.vectorOfPixels()
        if ar.dtype == bool:
            # converting bitfield to array of bytes
            self.images.append(pack_bitfield(ar))
            self.isPacked = 1
        else:
            self.images.append(ar)
        # save unicode of letter
        self.gt.append(label)
        # save size of one side to write in meta-information
        self.__size = size
        self.__count += 1
        print(self.__count, ":", filename, "was added. '", label, "'")


# pack array of bool into array of bytes
def pack_bitfield(bitfield):
    nbytes = len(bitfield)
    nbits = nbytes
    if nbytes % 8 == 0:
        nbytes //= 8
    else:
        nbytes = nbytes // 8 + 1
    res = numpy.zeros(nbytes, dtype=int)
    for i in range(nbytes):
        for j in range(8):
            if i * 8 + j < nbits and bitfield[i * 8 + j] == 1:
                res[i] += 1 << j
    return res
