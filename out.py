from enum import Enum
from puke import Puke, Card


class OutCate(Enum):
    Pass = "过"
    Single = "单张"
    Double = "对子"
    Three = "光三"
    FeiJi = "飞机"
    ShunZi = "顺子"
    ZiMeiDui = "姊妹对"
    GangBan = "钢板"
    THS = "同花顺"
    ZhaDan = "炸弹"
    WangZha = "王炸"
    Error = "无效"


class OutCard:
    def __init__(self, cards: list, red_num):
        self.cards: list[Card] = []
        self.other_cards: list[Card] = []
        self.other_numCount = {}

        self.cards = [Puke[c] for c in sorted(cards, reverse=True)]
        self.red_index = []

        self.red_num = red_num
        self.redCount = 0
        self.g_Count = 0
        self.G_Count = 0
        self.cardCount = len(self.cards)
        for i in range(self.cardCount):
            c = self.cards[i]
            if c.cate_str() == "♥" and c.num == red_num:
                self.redCount += 1
                self.red_index.append(i)
            elif c.num_str() == "g":
                self.g_Count += 1
            elif c.num_str() == "G":
                self.G_Count += 1
            else:
                self.other_cards.append(c)
                if self.other_numCount.get(c.num) == None:
                    self.other_numCount[c.num] = 1
                else:
                    self.other_numCount[c.num] += 1

        self.other_count = len(self.other_cards)
        self.cate = self.get_cate()
        self.val = self.cards[0].num

    def get_cate(self):
        count = self.cardCount
        if count == 0:
            return OutCate.Pass
        elif count == 1:
            self.val = self.cards[0].num
            return OutCate.Single
        elif count == 2:
            if self.cards[0].num == self.cards[1].num:
                return OutCate.Double
            if self.redCount > 0:
                self.cards[0]
                return OutCate.Double
            return OutCate.Error
        elif count == 3:
            if self.g_Count > 0 or self.G_Count > 0:
                return OutCate.Error
            if len(self.other_numCount) > 1:
                return OutCate.Error
            return OutCate.Three
        elif count == 4:
            if self.G_Count == 2 and self.g_Count == 2:
                return OutCate.WangZha
            return self.is_ZhaDan()
        elif count == 5:
            if self.is_ZhaDan() != OutCate.Error:
                return OutCate.ZhaDan
            if self.is_FeiJi() != OutCate.Error:
                return OutCate.FeiJi
            return self.is_ShunZi()
        elif count == 6:
            if self.is_ZhaDan() != OutCate.Error:
                return OutCate.ZhaDan
            if self.is_GangBan() != OutCate.Error:
                return OutCate.GangBan
            return self.is_ZiMeiDui()
        else:
            return self.is_ZhaDan()

    def is_ZhaDan(self):
        if len(self.other_cards) == 0:
            return OutCate.Error
        if len(self.other_numCount) > 1:
            return OutCate.Error
        return OutCate.ZhaDan

    def is_ShunZi(self):
        if self.g_Count > 0 or self.G_Count > 0:
            return OutCate.Error
        for v in self.other_numCount.values():
            if v != 1:
                return OutCate.Error

        redCount = self.redCount
        firstCate = self.other_cards[0].cate

        rt = OutCate.THS
        nextnum = self.other_cards[-1].num
        for i in reversed(range(len(self.other_cards))):
            c = self.other_cards[i]
            if c.cate != firstCate:
                rt = OutCate.ShunZi
            if c.num == nextnum:
                nextnum = c.num + 1
            elif c.num <= nextnum + redCount:
                redCount -= c.num - nextnum
                nextnum = c.num + 1
            elif i == 0 and c.num_str() == "A" and self.other_cards[-1].num <= redCount:
                continue
            else:
                return OutCate.Error
        return rt

    def is_FeiJi(self):
        if len(self.other_numCount) == 2 and self.g_Count == 0 and self.G_Count == 0:
            return OutCate.FeiJi
        elif len(self.other_numCount) == 1:
            if (self.g_Count == 2 and self.G_Count == 0) or (
                self.g_Count == 0 and self.G_Count == 2
            ):
                return OutCate.FeiJi

        return OutCate.Error

    def is_GangBan(self):
        if self.g_Count > 0 or self.G_Count > 0:
            return OutCate.Error
        if len(self.other_numCount) != 2:
            return OutCate.Error
        for v in self.other_numCount.values():
            if v > 3:
                return OutCate.Error

        keys = []
        for k in self.other_numCount:
            keys.append(k)

        if keys[0] - 1 == keys[1]:
            return OutCate.GangBan
        elif keys[0] == 12 and keys[1] == 0:
            return OutCate.GangBan
        return OutCate.Error

    def is_ZiMeiDui(self):
        if self.g_Count > 0 or self.G_Count > 0:
            return OutCate.Error
        for v in self.other_numCount.values():
            if v > 2:
                return OutCate.Error
        keys = []
        for k in self.other_numCount:
            keys.append(k)

        if len(keys) == 2:
            if self.redCount != 2:
                return OutCate.Error
            if (keys[0] - keys[1]) in (1, 2):
                return OutCate.ZiMeiDui
            if keys[0] == 12 and keys[1] in (1, 0):  # A 3,2
                return OutCate.ZiMeiDui
            return OutCate.Error
        elif len(keys) == 3:
            if keys[0] - 1 == keys[1] and keys[0] - 2 == keys[2]:
                return OutCate.ZiMeiDui
            if keys[0] == 12 and keys[1] == 1 and keys[2] == 0:  # A32
                return OutCate.ZiMeiDui
            return OutCate.Error
        else:
            return OutCate.Error

    def __eq__(self, p):
        if not isinstance(p, OutCard):
            raise TypeError()

        return self.cate == p.cate and self.val == p.val

    def __lt__(self, p):
        if not isinstance(p, OutCard):
            raise TypeError()

        if self.cate == OutCate.WangZha:
            return False
        elif self.cate == OutCate.THS:
            if p.cate == OutCate.WangZha:
                return True
            elif p.cate == OutCate.THS:
                return self.val < p.val
            elif p.cate == OutCate.ZhaDan:
                return p.cardCount > 5
            return False
        elif self.cate == OutCate.ZhaDan:
            if p.cate == OutCate.WangZha:
                return True
            elif p.cate == OutCate.THS:
                return self.cardCount <= 5
            elif p.cate == OutCate.ZhaDan:
                if self.cardCount == p.cardCount:
                    return self.val < p.val
                return self.cardCount < p.cardCount
            return False
        elif self.cate == p.cate:
            return self.val < p.val

        return p.cate in [OutCate.THS, OutCate.ZhaDan, OutCate.WangZha]

    def __le__(self, p):
        return self < p or self == p

    def __gt__(self, p):
        return not (self <= p)

    def __ge__(self, p):
        return self > p or self == p


if __name__ == "__main__":
    # num 2 = 0
    # Cate_str = "♦♣♥♠🃟🃏"
    # s = ["♥0", "♣A", "♠A", "♠K", "♠K", "♠K"]
    s = ["♥0", "♥0", "♣A", "♠5", "♠4"]
    cardVals = [Card.getCardVal_str(c) for c in s]
    o = OutCard(cardVals, 8)
    print(o.cate.value)
    for c in o.cards:
        print(c, end="")
