class ElemBlock:
    def __init__(self, text, pos, ok: bool =True):
        self.text=text
        self.pos=pos
        self.ok = ok

    def isOk(self) -> bool:
        return self.ok

    def getOutput(self):
        return self.text

    def getPos(self):
        return self.pos

    def __repr__(self):
        return f'({self.text}, {self.pos})'

    def __eq__(self, other):
        return self.text == other.text and self.pos == other.pos