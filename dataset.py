"""
In this file defined class Dataset and function for creating array of bytes
from array of bool.

Class Dataset loads datasets "CoMNIST" and "Olga" (dataset has no official name)
into memory, preprocesses all images and saves into hdf5 file.
Hdf5 file consists of two datasets:
1. "input". Bitfields of processed images in form of byte arrays
    Shape: (number of images, number of inputs of nn // 8), stored as UINT8
    has attribute "length" - number of inputs of nn
2. "gt". Labels of images, unicode of cyrillic character. Stored as UINT16
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


class DataSet:

    # pass name of resulting hdf5 file as name
    def __init__(self, name):
        self.name = name
        self.images = []
        self.gt = []
        self.__size = 0

    def load_comnist_dataset(self, source, size: int):
        for root, dirs, files in os.walk(source):
            label = os.path.basename(root)
            # if we are currently in directory with .png files
            # we don't need 'I' pictures in dataset
            if len(dirs) == 0 and label != u'I':
                for name in files:
                    self.__add_picture(os.path.join(source, name), label, size)

    def load_olga_dataset(self, source, size: int):
        sections = ['letters', 'letters2', 'letters3']
        for sec in sections:
            with open(os.path.join(source, sec+'.csv')) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    label = row['letter']
                    name = row['file']
                    self.__add_picture(os.path.join(source, sec, name), label, size)

    def create_db(self):
        inpt = numpy.array(self.images)
        gt = numpy.array(self.gt)
        with h5py.File(self.name+".h5", "w") as f:
            dset = f.create_dataset("input", numpy.shape(inpt), dtype=h5py.h5t.STD_U8BE, data=inpt)
            f.create_dataset("gt", numpy.shape(gt), dtype=h5py.h5t.STD_U16BE, data=gt)
            dset.attrs['length'] = self.__size * self.__size

    def __add_picture(self, filename, label, size):
        # preprocessing letter, converting to bitmap
        pict = PicHandler(Image.open(filename))
        # altering size of picture
        pict.alter(size)
        # converting bitfield to array of bytes
        self.images.append(pack_bitfield(pict.getPixelVector()))
        # save unicode of letter
        self.gt.append(ord(label[0]))
        # save size of one side to write in meta-information
        self.__size = size

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
