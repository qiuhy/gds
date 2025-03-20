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
    def cardCount(self):
        return sum(len(cards) for cards in self.numCards)

    def set_cards(self, cards):
        for n in self.numCards:
            n.clear()

        for c in cards:
            num = Puke[c].num
            self.numCards[num].append(c)

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
        redcard = Card.getCardVal("♥" + Card.get_num_str(self.curLevel))
        for num in reversed(self.numOrder):
            for c in self.numCards[num]:
                if c != redcard:
                    self.numCards[num].remove(c)
                    return c
        return None

    @abstractmethod
    def back(self, c):
        # 得到贡牌，再还牌
        num = Puke[c].num
        self.numCards[num].append(c)

        for num in self.numOrder:
            if len(self.numCards[num]):
                return self.numCards[num].pop()
        return None

    def get_back(self, c):
        # 拿到还牌
        num = Puke[c].num
        self.numCards[num].append(c)

    def removeCards(self, cards):
        for c in cards:
            num = Puke[c].num
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

    def get_out(self, prv: OutCard):
        c = []
        if prv is None:
            # 先出最小的
            for n in self.numOrder:
                if len(self.numCards[n]) < 4 and len(self.numCards[n]) > 0:
                    return self.numCards[n].copy()

            for n in self.numOrder:
                if len(self.numCards[n]):
                    return self.numCards[n].copy()

        else:
            prvOrder = self.numOrder.index(prv.val)
            # 尽量管住   同类牌，炸
            for n in self.numOrder[prvOrder + 1 :]:
                if len(self.numCards[n]) == prv.cardCount:
                    return self.numCards[n].copy()

            for n in self.numOrder:
                if len(self.numCards[n]) >= 4:
                    return self.numCards[n].copy()

        return c

    @abstractmethod
    def onEvent(self, e: Game_Event_Cate, info):
        # GE_Ready = "就绪"  # [playersname] * 4
        # GE_Deal = "发牌"   # level
        # GE_Give = "贡牌"   # (giver, Puke)
        # GE_Back = "还牌"   # (giver, Puke, backer, Puke)
        # GE_Anti = "抗供"   # [Antier]
        # GE_Start = "开始"  # firster
        # GE_Play = "出牌"   # outCard
        # GE_Over = "结束"   # winner[]
        # GE_End = "游戏结束"
        if e == Game_Event_Cate.GE_Ready:
            self.playerNames = info
        elif e == Game_Event_Cate.GE_Deal:
            self.curLevel = info


    def __str__(self):
        s = f"{self.name}:"
        for n in reversed(self.numOrder):
            for c in self.numCards[n]:
                s += " " + str(Puke[c])
        return s

