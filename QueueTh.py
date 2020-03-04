from __future__ import annotations
from typing import *

from collections import deque

import threading as th

class QueueTh:
    def __init__(self, funcs, args, nThreads=4):
        if len(funcs) != len(args):
            raise Exception("Queue params")

        self.funcs = funcs
        self.args = args
        self.n = nThreads
        self.executing: List[th.Thread] = []

    def start(self):
        self.threads = deque([ th.Thread(target=self.funcs[i], args=self.args[i])
                         for i in range(self.n) ])

        self.executing = [self.threads.pop().start() for i in range(self.n)]

        self.control()

    def control(self):
        counter = 0
        while len(self.threads):
            while counter < self.n:
                counter += 1
                thr = self.threads.pop()
                thr.start()
                thr.join() # запрет завершения порождающего потока
                self.executing.append(thr)

            for thread in self.executing:
                if not thread.is_alive():
                    self.executing.remove(thread)
                    counter -= 1
