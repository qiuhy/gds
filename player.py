from abc import abstractmethod
from out import OutCard, OutCate
from puke import Puke, Card


class Player:
    def __init__(self):
        self.name = ""
        self.partner = None
        self.sit = None
        self._cards = []
        self.numCards = [[] for i in range(15)]
        self.curLevel = 0

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        for n in self.numCards:
            n.clear()

        for i in cards:
            num = Puke[i].num
            self.numCards[num].append(i)

        self._cards = cards

    def action(self, desk_outs: list[OutCard]):
        select_cards = self.play(desk_outs)
        out = OutCard(select_cards, self.curLevel, self.sit)

        if len(desk_outs):
            if desk_outs[-1] >= out:
                return OutCate.Pass

        desk_outs.append(out)
        self.removeCards(select_cards)

        return out.cate

    @abstractmethod
    def give(self):
        # 贡牌
        for c in self.cards:
            if not (Puke[c].num == self.curLevel and Puke[c].cate_str() == "♥"):
                break
        num = Puke[c].num
        self.numCards[num].remove(c)
        self.cards.remove(c)
        return c

    @abstractmethod
    def back(self, card):
        # 得到贡牌，再还牌
        self.cards.insert(0, card)
        num = Puke[card].num
        self.numCards[num].append(card)

        card = self.cards.pop()
        num = Puke[card].num
        self.numCards[num].remove(card)

        return card

    def get_back(self, card):
        # 拿到还牌
        self.cards.append(card)
        num = Puke[card].num
        self.numCards[num].append(card)

    def removeCards(self,cards):
        for c in cards:
            num = Puke[c].num
            self.numCards[num].remove(c)
            self.cards.remove(c)

    @abstractmethod
    def play(self, desk_outs: list[OutCard]) -> list:
        # 出牌
        if len(desk_outs) == 0:
            # 先出
            return [self.cards[-1]]
        else:
            out = desk_outs[-1]
            if out.player == self.partner:
                # 对家的不要
                return []
            else:
                # 尽量管住
                for num in self.get_cards(out.cate):
                    s = Card.get_num_str(num)
                    i = Card.getCardVal(s)

                for i in reversed(self.cards):
                    select_cards = [i]
                    hand = OutCard(select_cards, self.curLevel, self.sit)
                    if hand > out:
                        return select_cards
            return []

    def get_out(self, prv: OutCard):
        c = []
        if prv.cate == OutCate.Single:
            pass
        return c
