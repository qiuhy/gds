import random
from puke import Puke,Card
from out import OutCard, OutCate


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []

    def action(self, desk_outs: list[OutCard], level):

        select_cards = [random.choice(self.cards)]
        out = OutCard(select_cards, level)

        if len(desk_outs):
            if desk_outs[-1] >= out:
                return OutCate.Pass

        desk_outs.append(out)

        for c in select_cards:
            self.cards.remove(c)
        return out.cate


class Team:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.name = p1.name + " & " + p2.name
        self.level = 0  # 当前打几 234567890JQKA


def get_teammate(s):
    return (s + 2) % 4


class Table:
    def __init__(self):
        SitName = "我下对上"  # "下右上左"
        self.cards = [i % 54 for i in range(2 * 54)]
        self.players = [Player(SitName[i]) for i in range(4)]
        self.teams = [
            Team(self.players[0], self.players[2]),
            Team(self.players[1], self.players[3]),
        ]
        self.curTeam = 0
        self.curLevel = 0
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

    def play(self):
        firstPlayer = self.firstPlayer
        self.winner.clear()
        while not self.is_over():
            self.ondesk_cards.clear()

            strFirts = "先出"
            if firstPlayer in self.winner:
                firstPlayer = get_teammate(firstPlayer)
                strFirts = "接风"

            print(
                self.players[firstPlayer].name,
                f"({len(self.players[firstPlayer].cards)})",
                strFirts,
            )

            nextPlayer = firstPlayer
            while True:
                if len(self.players[nextPlayer].cards):
                    outs = self.players[nextPlayer].action(
                        self.ondesk_cards, self.curLevel
                    )
                    if outs.isValid():
                        out = self.ondesk_cards[-1]
                        print(
                            self.players[nextPlayer].name,
                            ":",
                            out,
                            out.val_str(),
                            end=" ",
                        )
                        if len(self.players[nextPlayer].cards) == 0:
                            self.winner.append(nextPlayer)
                            print("\tWIN", len(self.winner))
                            if self.is_over():
                                break
                        else:
                            print(f"\t({len(self.players[nextPlayer].cards)})")
                        firstPlayer = nextPlayer
                    else:
                        print(
                            self.players[nextPlayer].name,
                            ":",
                            outs.value,
                            f"\t({len(self.players[nextPlayer].cards)})",
                        )

                nextPlayer = self.get_nextPlayer(nextPlayer)
                if nextPlayer == firstPlayer:
                    break
        print("结束:", [self.players[i].name for i in self.winner])

    def is_over(self) -> bool:
        if len(self.winner) < 2:
            return False
        elif len(self.winner) > 2:
            return True
        else:
            return get_teammate(self.winner[0]) in self.winner

    def get_nextPlayer(self, player):
        n = (player + 1) % len(self.players)
        return n

    def print(self):
        for p in self.players:
            print("Player:", p.name, "'s cards:")
            for c in p.cards:
                print(Puke[c], end="")
            print()
        print("本局打:",  Card.get_num_str(self.curLevel), self.players[self.firstPlayer].name, "先出")


if __name__ == "__main__":
    t = Table()
    t.begin()
    t.print()
    t.play()
