from __future__ import annotations
import pickle

def saveObj(obj, filename: str) -> None:
    file = open(filename, 'wb')
    try:
        pickle.dump(obj, file)
    except:
        raise Exception("Saving "+filename+" exception")
    file.close()

def loadObj(filename: str):
    file = open(filename, 'rb')
    try:
        obj = pickle.load(file)
    except:
        raise Exception("Loading "+filename+" exception")
    file.close()
    return obj