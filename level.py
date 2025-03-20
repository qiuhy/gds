class Level:
    def __init__(self):
        self._curLevel = 12
        self.numOrder = [n for n in range(15)]

    @property
    def curLevel(self):
        return self._curLevel

    @curLevel.setter
    def curLevel(self, level):
        if level > 13:
            return
        if level == self._curLevel:
            return
        self.numOrder.remove(self._curLevel)
        self.numOrder.insert(self._curLevel, self._curLevel)
        self.numOrder.remove(level)
        self.numOrder.insert(-2, level)
        self._curLevel = level

