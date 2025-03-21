from enum import Enum
from puke import Puke, Card
from level import Level


class OutCate(Enum):
    Pass = "过"
    Single = "单张"
    Double = "对子"
    Three = "光三"
    FeiJi = "飞机"
    ShunZi = "顺子"
    ZiMeiDui = "姊妹对"
    GangBan = "钢板"
    ZhaDan4 = "炸弹"
    ZhaDan5 = "五炸"
    ZhaDan5THS = "同花顺"
    ZhaDan6 = "六炸"
    ZhaDan7 = "七炸"
    ZhaDan8 = "八炸"
    ZhaDan9 = "九炸"
    ZhaDanS = "十炸"
    ZhaWang = "王炸"
    Error = "无效"
    
    @property
    def isZhaDan(self):
        return self.name.startswith("Zha")
   
    @property
    def isValid(self):
        return self not in [OutCate.Pass, OutCate.Error]


class OutCard(Level):
    def __init__(self, cards: list, level, player=None):
        super().__init__()
        self.cards: list[Card] = []
        self.red_cards: list[Card] = []
        self.wang_cards: list[Card] = []
        self.other_cards: list[Card] = []
        self.num_count = {}
        self.player = player
        self.cards = [Puke[c] for c in sorted(cards, reverse=True)]

        self.curLevel = level
        for c in self.cards:
            isred = False
            if c.cate_str() == "♥" and c.num == level:
                self.red_cards.append(c)
                isred = True
            elif c.num_str() == "g" or c.num_str() == "G":
                self.wang_cards.append(c)
            else:
                self.other_cards.append(c)

            if not isred:
                if self.num_count.get(c.num) == None:
                    self.num_count[c.num] = 1
                else:
                    self.num_count[c.num] += 1

        self.val = -1
        self.cate = self.get_cate()
        if self.cate in (OutCate.Pass, OutCate.Error):
            return

        if self.val == -1:
            self.val = self.cards[0].num

    @property
    def cardCount(self):
        return len(self.cards)

    @property
    def redCount(self):
        return len(self.red_cards)

    @property
    def numKinds(self):
        return len(self.num_count)

    def get_cate(self) -> OutCate:
        count = self.cardCount
        if count == 0:
            return OutCate.Pass
        elif count == 1:
            return OutCate.Single
        elif count == 2:
            if self.cards[0].num == self.cards[1].num:
                return OutCate.Double
            if len(self.wang_cards):
                return OutCate.Error
            if self.redCount > 0:
                self.cards = self.other_cards + self.red_cards
                return OutCate.Double
            return OutCate.Error
        elif count == 3:
            if len(self.wang_cards):
                return OutCate.Error
            if self.numKinds != 1:
                return OutCate.Error
            self.cards = self.other_cards + self.red_cards
            return OutCate.Three
        elif count == 4:
            if len(self.wang_cards) == 4:
                return OutCate.ZhaWang
            return self.is_ZhaDan()
        elif count == 5:
            if self.is_ZhaDan() != OutCate.Error:
                return OutCate.ZhaDan5
            if self.is_FeiJi() != OutCate.Error:
                return OutCate.FeiJi
            return self.is_ShunZi()
        elif count == 6:
            if self.is_ZiMeiDui() != OutCate.Error:
                return OutCate.ZiMeiDui
            if self.is_GangBan() != OutCate.Error:
                return OutCate.GangBan
            return self.is_ZhaDan()
        else:
            return self.is_ZhaDan()

    def is_ZhaDan(self):
        if len(self.wang_cards):
            return OutCate.Error
        if self.numKinds == 1 and self.cardCount > 3:
            self.cards = self.other_cards + self.red_cards
            if self.cardCount == 4:
                return OutCate.ZhaDan4
            elif self.cardCount == 5:
                return OutCate.ZhaDan5
            elif self.cardCount == 6:
                return OutCate.ZhaDan6
            elif self.cardCount == 7:
                return OutCate.ZhaDan7
            elif self.cardCount == 8:
                return OutCate.ZhaDan8
            elif self.cardCount == 9:
                return OutCate.ZhaDan9
            else:
                return OutCate.ZhaDanS
        return OutCate.Error

    def is_ShunZi(self):
        if len(self.wang_cards):
            return OutCate.Error
        for v in self.num_count.values():
            if v != 1:
                return OutCate.Error

        lastNum = self.other_cards[-1].num
        firstNum = self.other_cards[0].num
        lastA = False
        if firstNum > lastNum + 4:
            if firstNum == 12:  # "A":
                if self.other_cards[1].num > 3:  # A5432
                    return OutCate.Error
                self.other_cards.append(self.other_cards.pop(0))
                lastA = True
            else:
                return OutCate.Error

        redCount = self.redCount
        rt = OutCate.ZhaDan5THS
        self.cards.clear()
        firstCate = self.other_cards[0].cate
        nextnum = self.other_cards[0].num
        for c in self.other_cards:
            if c.cate != firstCate:
                rt = OutCate.ShunZi
            if (lastA and c.num == 12) or c.num < nextnum:
                if lastA and c.num == 12:
                    ln = nextnum + 1
                else:
                    ln = nextnum - c.num
                self.cards.extend(self.red_cards[:ln])
                redCount -= ln
            self.cards.append(c)
            nextnum = c.num - 1

        if redCount:
            if self.cards[0].num < 12:
                ln = min(12 - self.cards[0].num, redCount)
                self.val = self.cards[0].num + ln
                self.cards = self.red_cards[:ln] + self.cards
                redCount -= ln
            if redCount:
                self.cards.extend(self.red_cards[:redCount])
        return rt

    def is_FeiJi(self):
        if self.numKinds != 2:
            return OutCate.Error

        keys = []
        vals = []
        for k, v in self.num_count.items():
            if v > 3:
                return OutCate.Error
            vals.append(v)
            keys.append(k)

        if len(self.wang_cards) == 2:
            self.cards = self.other_cards + self.red_cards + self.wang_cards
            return OutCate.FeiJi
        elif len(self.wang_cards) == 0:
            if self.redCount == 0:
                if vals[1] == 3:
                    self.cards = self.other_cards[-3:] + self.other_cards[:-3]
            elif self.redCount == 1:
                if vals[0] == 3:
                    self.cards = self.other_cards + self.red_cards
                elif vals[1] == 3:
                    self.cards = (
                        self.other_cards[-3:] + self.other_cards[:-3] + self.red_cards
                    )
                else:
                    # 22
                    if keys[1] == self.curLevel:
                        self.cards = (
                            self.other_cards[-2:]
                            + self.red_cards
                            + self.other_cards[:-2]
                        )
                    else:
                        self.cards = (
                            self.other_cards[:2] + self.red_cards + self.other_cards[2:]
                        )
            elif self.redCount == 2:
                if keys[1] == self.curLevel:
                    self.cards = (
                        self.other_cards[vals[0] :]
                        + self.red_cards[: 3 - vals[1]]
                        + self.other_cards[: vals[0]]
                        + self.red_cards[: 2 - vals[0]]
                    )
                else:
                    self.cards = (
                        self.other_cards[: vals[0]]
                        + self.red_cards[: 3 - vals[0]]
                        + self.other_cards[vals[0] :]
                        + self.red_cards[: 2 - vals[1]]
                    )

            return OutCate.FeiJi
        return OutCate.Error

    def is_GangBan(self):
        if len(self.wang_cards):
            return OutCate.Error
        if self.numKinds != 2:
            return OutCate.Error
        for v in self.num_count.values():
            if v > 3:
                return OutCate.Error

        keys = []
        for k in self.num_count:
            keys.append(k)

        if keys[0] - 1 == keys[1]:
            if self.num_count[keys[0]] == 3:
                self.cards = self.other_cards + self.red_cards
            elif self.num_count[keys[0]] == 2:
                self.cards = (
                    self.other_cards[:2] + self.red_cards[0:1] + self.other_cards[2:]
                )
                if self.redCount == 2:
                    self.cards.append(self.red_cards[-1])
            else:
                self.cards = (
                    self.other_cards[:1] + self.red_cards + self.other_cards[1:]
                )
            return OutCate.GangBan
        elif keys[0] == 12 and keys[1] == 0:  # A2
            if self.num_count[keys[0]] == 3:
                self.cards = (
                    self.other_cards[3:] + self.red_cards + self.other_cards[:3]
                )
            elif self.num_count[keys[0]] == 2:
                self.cards = (
                    self.other_cards[2:] + self.other_cards[:2] + self.red_cards[-1:]
                )
                if self.redCount == 2:
                    self.cards.insert(2, self.red_cards[0])
            else:
                self.cards = (
                    self.other_cards[1:] + self.other_cards[:1] + self.red_cards
                )

            return OutCate.GangBan
        return OutCate.Error

    def is_ZiMeiDui(self):
        if len(self.wang_cards):
            return OutCate.Error
        for v in self.num_count.values():
            if v > 2:
                return OutCate.Error
        keys = []
        for k in self.num_count:
            keys.append(k)

        if len(keys) == 2:
            if self.redCount != 2:
                return OutCate.Error
            if (keys[0] - keys[1]) in (1, 2):
                if (keys[0] - keys[1]) == 1:
                    if keys[0] == 12:
                        self.cards = self.other_cards + self.red_cards
                    else:
                        self.cards = self.red_cards + self.other_cards
                        self.val = keys[0] + 1
                else:
                    self.cards = (
                        self.other_cards[:2] + self.red_cards + self.other_cards[2:]
                    )
                return OutCate.ZiMeiDui
            if keys[0] == 12 and keys[1] in (1, 0):  # A 3,2
                if keys[1] == 1:
                    self.cards = (
                        self.other_cards[2:] + self.red_cards + self.other_cards[:2]
                    )
                else:
                    self.cards = (
                        self.red_cards + self.other_cards[2:] + self.other_cards[:2]
                    )
                    self.val = 1
                return OutCate.ZiMeiDui
            return OutCate.Error
        elif len(keys) == 3:
            if (keys[0] == keys[1] + 1 and keys[0] == keys[2] + 2) or (
                keys[0] == 12 and keys[1] == 1 and keys[2] == 0  # A32
            ):
                ln = 0
                for v in self.num_count.values():
                    if v == 1:
                        self.other_cards.insert(ln + 1, self.red_cards.pop())
                    ln += 2
                if keys[0] == 12 and keys[1] == 1 and keys[2] == 0:
                    self.cards = self.other_cards[2:] + self.other_cards[:2]
                else:
                    self.cards = self.other_cards[:]
                return OutCate.ZiMeiDui
            return OutCate.Error
        else:
            return OutCate.Error

    def val_str(self):
        return [str(c) for c in self.cards]

    def __str__(self):
        if self.val == -1:
            return self.cate.value
        else:
            s = "@" if self.val == self.curLevel else " "
            return self.cate.value + s + str(self.val_str())

    def __eq__(self, p):
        if not isinstance(p, OutCard):
            raise TypeError()
        return self.cate == p.cate and self.val == p.val

    def __lt__(self, p):
        if not isinstance(p, OutCard):
            raise TypeError()

        if not (self.cate.isValid and p.cate.isValid):
            return False

        if self.cate.isZhaDan:
            if self.cate == p.cate:
                return self.numOrder.index(self.val) < p.numOrder.index(p.val)
            elif p.cate.isZhaDan:
                return self.cate.name < p.cate.name
            else:
                return False
        elif self.cate == p.cate:
            if self.cate in [OutCate.ShunZi, OutCate.GangBan, OutCate.ZiMeiDui]:
                return self.val < p.val
            else:
                return self.numOrder.index(self.val) < p.numOrder.index(p.val)
        else:
            return p.cate.isZhaDan

    def __le__(self, p):
        return self < p or self == p

    def __gt__(self, p):
        return not (self <= p)

    def __ge__(self, p):
        return self > p or self == p


import random

if __name__ == "__main__":
    # num 2 = 0
    Cate_str = "♦♣♥♠🃟🃏"
    # s = ["♥0", "♥0", "♣0", "♠0", "♠0", "♠0"]
    # s = ["♥0", "♥0", "♣5", "♣4", "♣2"]
    # s = ["♥0", "🃟g", "🃟g", "♣0", "♣0"]
    s = ["♥0", "♥0"]
    s.append(Cate_str[random.randint(0, 1)] + Card.get_num_str(random.randint(9, 12)))
    s.append(Cate_str[random.randint(0, 1)] + Card.get_num_str(random.randint(9, 12)))
    s.append(Cate_str[random.randint(0, 1)] + Card.get_num_str(random.randint(9, 12)))
    # s.append(Cate_str[random.randint(0, 3)] + Card.get_num_str(random.randint(10, 12)))
    cardVals = [Card.getCardVal(c) for c in s]
    o = OutCard(cardVals, 8)
    print(o)
