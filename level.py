class Level:
    _curLevel = 0
    numOrder = [n for n in range(15)]

    @property
    def curLevel(self):
        return self._curLevel

    @curLevel.setter
    def curLevel(self, level):
        if level > 13:
            return
        self.numOrder.remove(self._curLevel)
        self.numOrder.insert(self._curLevel, self._curLevel)
        self.numOrder.remove(level)
        self.numOrder.insert(-2, level)
        self._curLevel = level
