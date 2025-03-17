
import random
from puke import Puke


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []

    def action(self, desk_outs: list[list[int]] = None):
        # TODO
        outs = []
        if len(desk_outs) ==0:
            pass
        last_out = desk_outs[-1]
        
        for c in outs:
            self.cards.remove(c)
        return len(outs)


class Team:
    def __init__(self, name, p1, p2):
        self.name = name
        self.p1 = p1
        self.p2 = p2
        self.step = 0  # 当前打几 234567890JQKA


# Match > Round > Game

SitName = "SENW"


def get_teammate(s):
    return (s + 2) % 4


def get_next(s):
    return (s + 1) % 4


class Table:

    def __init__(self):
        self.cards = [i % 54 for i in range(2 * 54)]
        self.players = [Player(SitName[i]) for i in range(4)]
        self.teams = [
            Team("NS", self.players[0], self.players[2]),
            Team("EW", self.players[1], self.players[3]),
        ]
        self.curTeam = 0
        self.firstPlayer = 0
        self.winner = []
        self.ondesk_cards = []

    def begin(self):
        random.shuffle(self.cards)
        i = 0
        for p in self.players:
            p.cards.clear()
            p.cards = self.cards[i : i + 27]
            p.cards.sort(reverse=True)
            i += 27

        i = random.randint(0, 3)
        self.firstPlayer = i
        self.curTeam = i % 2

    def play(self, firstPlayer):
        self.winner.clear()
        while not self.is_over():
            self.ondesk_cards.clear()
            if firstPlayer in self.winner:
                firstPlayer = get_teammate(firstPlayer)

            outs = self.players[firstPlayer].action()
            self.ondesk_cards.append(outs)
            nextPlayer = get_next(firstPlayer)
            while True:
                if len(self.players[nextPlayer].cards):
                    outs = self.players[nextPlayer].action()
                    if len(outs):
                        self.ondesk_cards.append(outs)
                        if len(self.players[nextPlayer].cards) == 0:
                            self.winner.append(nextPlayer)
                        firstPlayer = nextPlayer

                nextPlayer = get_next(nextPlayer)
                if nextPlayer == firstPlayer:
                    break

    def is_over(self) -> bool:
        if len(self.winner) == 0:
            return False
        return get_teammate(self.winner[0]) in self.winner

    def print(self):
        for p in self.players:
            print("Player:", p.name, "'s cards:")
            for c in p.cards:
                print(Puke[c], end="")
            print()


if __name__ == "__main__":
    t = Table()
    t.begin()
    t.print()
