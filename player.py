from abc import abstractmethod
from out import OutCard, OutCate
from puke import Puke, Card
from level import Level
from event import *


class Player(Level):

    def __init__(self, name=""):
        super().__init__()
        self.partner = None
        self.sit = None
        self.numCards = [[] for i in range(15)]  # "234567890JQKAgG"
        self.name = name
        self.curLevel = 0
    
    @property 
    def winner_title(self):
        return ["头游", "二游", "三游", "末游"]


    @property
    def cardCount(self):
        return sum(len(cards) for cards in self.numCards)

    @property
    def allNums(self):
        for num in reversed(self.numOrder):
            if len(self.numCards[num]) == 0:
                continue
            yield num

    @property
    def numCount(self):
        return sum(1 for _ in self.allNums)

    def set_cards(self, cards):
        for n in self.numCards:
            n.clear()

        for c in cards:
            num = Card.get_val_num(c)
            self.numCards[num].append(c)

        for n in self.allNums:
            self.numCards[num].sort()

    def action(self, desk_outs: list[OutCard]):
        select_cards = self.play(desk_outs)
        out = OutCard(select_cards, self.curLevel, self.sit)

        if len(desk_outs):
            if desk_outs[-1] >= out:
                return OutCard([], self.curLevel, self.sit)

        desk_outs.append(out)
        self.removeCards(select_cards)

        return out

    @abstractmethod
    def give(self):
        # 贡牌
        for num in self.allNums:
            for c in self.numCards[num]:
                if c != self.redCard:
                    self.numCards[num].remove(c)
                    return c
        return None

    @abstractmethod
    def back(self, c):
        # 得到贡牌，再还牌
        num = Card.get_val_num(c)
        self.numCards[num].append(c)
        self.numCards[num].sort()

        # 优先还最小单张
        for num in self.numOrder:
            if len(self.numCards[num]) == 1:
                if self.isValidBackCard(self.numCards[num][0]):
                    return self.numCards[num].pop()

        for num in self.numOrder:
            if len(self.numCards[num]):
                return self.numCards[num].pop()

        return None

    def get_back(self, c):
        # 拿到还牌
        num = Card.get_val_num(c)
        self.numCards[num].append(c)
        self.numCards[num].sort()

    def removeCards(self, cards):
        for c in cards:
            num = Card.get_val_num(c)
            self.numCards[num].remove(c)

    @abstractmethod
    def play(self, desk_outs: list[OutCard]) -> list:
        # 出牌
        curOut = []
        if len(desk_outs) == 0:
            return self.get_out(None)
        else:
            prvOut = desk_outs[-1]
            if prvOut.player == self.partner:
                # 对家的不要
                pass
            else:
                return self.get_out(prvOut)

        return curOut

    def get_out(self, prvOut: OutCard):
        c = []
        if prvOut is None:
            # 先出最小的
            for n in self.numOrder:
                if len(self.numCards[n]) < 4 and len(self.numCards[n]) > 0:
                    return self.numCards[n].copy()

            for n in self.numOrder:
                if len(self.numCards[n]):
                    return self.numCards[n].copy()

        else:
            prvOrder = self.numOrder.index(prvOut.val)
            # 尽量管住   同类牌，炸
            if not prvOut.cate.isZhaDan:
                for n in self.numOrder[prvOrder + 1 :]:
                    if len(self.numCards[n]) == prvOut.cardCount:
                        out = OutCard(self.numCards[n], self.curLevel)
                        if out > prvOut:
                            return self.numCards[n].copy()

            for n in self.numOrder:
                if len(self.numCards[n]) >= 4:
                    out = OutCard(self.numCards[n], self.curLevel)
                    if out > prvOut:
                        return self.numCards[n].copy()

        return c

    def find_out(self,cate:OutCate):
        #TODO
        pass

    @abstractmethod
    def onEvent(self, e: Game_Event_Cate, info):
        if e == Game_Event_Cate.GE_Ready:
            self.playerNames = info

    def __str__(self):
        s = f"{self.name}:"
        for n in reversed(self.numOrder):
            for c in self.numCards[n]:
                s += f" {Puke[c]}"
        return s
