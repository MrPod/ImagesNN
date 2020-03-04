from math import sqrt
from random import randrange


# Point on 2D plane
class Point:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # sum of two vectors
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    # product of vector by number
    def __mul__(self, other: float):
        return Point(int(self.x*other),int(self.y*other))

    # division of vector by number
    def __truediv__(self, other):
        return Point(int(self.x/other), int(self.y/other))

    # difference of two vectors
    def __sub__(self, other):
        return self + (-1)*other

    # dot product of two vectors
    def dot_prod(self, other):
        return self.x * other.x + self.y * other.y

    # length of vector from origin to point
    def length(self):
        return sqrt(self.dot_prod(self))

    # distance between two points
    def distance(self, point):
        return (self - point).length()


# Rect on 2D plane
class Position:
    x: int
    y: int
    w: int
    h: int

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # normalize: h >=0, w >= 0
        if h < 0:
            self.y = y - h
            self.h = -h
        if w < 0:
            self.x = x - w
            self.w = -w

    # returns Point in center of position
    def center(self):
        return Point(self.x + self.w /2, self.y + self.h/2)

    # returns true if two positions intersect
    def intersects(self, other):
        if (self.x + self.w >= other.x or other.x + other.w >= self.x) \
                and (self.y + self.h >= other.y or other.y+other.height >= self.y):
            return True
        else:
            return False

    # diameter of position, length of diagonal
    def diameter(self):
        return sqrt(self.w*self.w + self.h*self.h)

    # distance between Point p and center of position
    def center_distance(self, p: Point):
        return self.center().distance(p)

    # distance between centers of two positions
    def distance(self, other):
        return self.center().distance(other.center())

    # returns true, if Point p is within position
    def includes(self, p: Point):
        if self.x <= p.x <= self.x + self.w and self.y <= p.y <= self.y + self.h:
            return True
        else:
            return False

    # returns position, that contains self and other
    def bounding_rect(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x+self.w - x, other.x+other.w - x)
        h = max(self.y+self.h - y, other.y+other.h - y)
        return Position(x,y,w,h)

    # returns random point in position
    def random_point(self):
        return Point(randrange(self.x, stop=self.x+self.w), randrange(self.y, stop=self.y+self.h))