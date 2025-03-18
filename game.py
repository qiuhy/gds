import random
from puke import Puke, Card
from out import OutCard, OutCate
from abc import classmethod

class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []

    def action(self, desk_outs: list[OutCard], level):

        select_cards = self.play(desk_outs, level)
        out = OutCard(select_cards, level)

        if len(desk_outs):
            if desk_outs[-1] >= out:
                return OutCate.Pass

        desk_outs.append(out)

        for c in select_cards:
            self.cards.remove(c)
        return out.cate

    def give(self, level):
        # 供牌
        for c in self.cards:
            if not (Puke[c].num == level and Puke[c].cate_str() == "♥"):
                break
        self.cards.remove(c)
        return c
    
    @classmethod
    def back(self, card):
        # 还牌
        self.cards.insert(0, card)
        return self.cards.pop()
    
    @classmethod
    def play(self, desk_outs: list[OutCard], level) -> list[int]:
        return [random.choice(self.cards)]


class Team:
    def __init__(self, p1, p2):
        self.players = [p1, p2]
        self.name = p1.name + p2.name
        self.level = 0  # 当前打几 234567890JQKA


def get_teammate(s):
    return (s + 2) % 4


winner_title = ["头游", "二游", "三游", "末游"]


class Table:
    def __init__(self):
        SitName = "南东北西"  # "下右上左" "我下对上"
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

        self.firstPlayer = random.randint(0, 3)
        self.curTeam = self.firstPlayer % 2
        self.gameCount = 0

    def sort_card(self, cards: list):
        cards.sort(
            key=lambda c: (
                Puke[c].num + 13
                if Puke[c].num == self.curLevel or Puke[c].num > 12
                else Puke[c].num
            ),
            reverse=True,
        )

    def get_nextPlayer(self, player):
        n = (player + 1) % len(self.players)
        return n

    def get_level_name(self, level=None):
        if level == None:
            level = self.curLevel

        if level < 12:
            return Card.get_num_str(level)
        else:
            return str(level - 11) + Card.get_num_str(12)

    def begin(self):
        random.shuffle(self.cards)
        i = 0
        for p in self.players:
            p.cards.clear()
            p.cards = self.cards[i : i + 27]
            self.sort_card(p.cards)
            i += 27

        if self.gameCount:
            self.firstPlayer = self.give()

    def back(self, giver, givecard, backer):
        backcard = self.players[backer].back(givecard)
        self.sort_card(self.players[backer].cards)
        self.players[giver].cards.append(backcard)
        self.sort_card(self.players[giver].cards)
        print(
            "{} 贡牌 {} 给 {}, 得到还牌 {}".format(
                self.players[giver].name,
                str(Puke[givecard]),
                self.players[backer].name,
                str(Puke[backcard]),
            )
        )

    def give(self):
        if len(self.winner) == 0:
            return None

        double_give = self.winner[-2] == get_teammate(self.winner[-1])

        G_count = self.players[self.winner[-1]].cards.count(53)
        if double_give:
            G_count += self.players[self.winner[-2]].cards.count(53)

        if G_count == 2:
            if double_give:
                print(self.teams[self.winner[-1] % 2].name, "抗贡!!!")
            else:
                print(self.players[self.winner[-1]].name, "抗贡!!!")
            # 抗贡 头游先出
            return self.winner[0]

        give_card = [self.players[self.winner[-1]].give(self.curLevel)]
        if double_give:
            give_card.append(self.players[self.winner[-2]].give(self.curLevel))

        if double_give:
            # 双贡 供牌大的先出 ，一样大 顺时针方向进贡 头游的下家先出
            card0 = OutCard([give_card[0]], self.curLevel)
            card1 = OutCard([give_card[1]], self.curLevel)
            if card1 != card0:
                if card1 > card0:
                    big_card = give_card[1]
                    big_giver = self.winner[-2]
                    small_card = give_card[0]
                    small_giver = self.winner[-1]
                else:
                    big_card = give_card[0]
                    big_giver = self.winner[-1]
                    small_card = give_card[1]
                    small_giver = self.winner[-2]

                self.back(big_giver, big_card, self.winner[0])
                self.back(small_giver, small_card, self.winner[1])

                return big_giver
            else:
                # 如果双方进贡的牌一样大，则按照顺时针方向进贡,头游的下家先出
                self.back(self.winner[-1], give_card[0], self.winner[0])
                self.back(self.winner[-2], give_card[1], self.winner[1])
                return self.get_nextPlayer(self.winner[0])
        else:
            # 单贡 末游先出
            self.back(self.winner[-1], give_card[0], self.winner[0])
            return self.winner[-1]

    def play(self, showOut):
        firstPlayer = self.firstPlayer
        outCount = 0
        self.winner.clear()
        while not self.is_level_over():
            self.ondesk_cards.clear()

            strFirts = "先出"
            if firstPlayer in self.winner:
                firstPlayer = get_teammate(firstPlayer)
                strFirts = "接风"
            if showOut:
                print(
                    self.players[firstPlayer].name,
                    f"({len(self.players[firstPlayer].cards)})",
                    strFirts,
                )

            nextPlayer = firstPlayer
            while True:
                if len(self.players[nextPlayer].cards):
                    outcate = self.players[nextPlayer].action(
                        self.ondesk_cards, self.curLevel
                    )
                    outCount += 1

                    if showOut:
                        if outcate.isValid():
                            out = self.ondesk_cards[-1]
                            print(
                                self.players[nextPlayer].name,
                                ":",
                                out,
                                out.val_str(),
                                end=" ",
                            )
                            if len(self.players[nextPlayer].cards) == 0:
                                print("\t", winner_title[len(self.winner)])
                            else:
                                print(f"\t({len(self.players[nextPlayer].cards)})")
                        else:
                            print(
                                self.players[nextPlayer].name,
                                ":",
                                outcate.value,
                                f"\t({len(self.players[nextPlayer].cards)})",
                            )

                    if outcate.isValid():
                        if len(self.players[nextPlayer].cards) == 0:
                            self.winner.append(nextPlayer)
                            if self.is_level_over():
                                break
                        firstPlayer = nextPlayer

                nextPlayer = self.get_nextPlayer(nextPlayer)
                if nextPlayer == firstPlayer:
                    break

        self.ondesk_cards.clear()

    def is_level_over(self) -> bool:
        if len(self.winner) < 2:
            return False
        elif len(self.winner) > 2:
            return True
        else:
            return get_teammate(self.winner[0]) in self.winner

    def is_game_over(self):
        if not self.is_level_over():
            return False
        is_over = False
        if len(self.winner) != len(self.players):
            for i in range(len(self.players)):
                if not i in self.winner:
                    self.winner.append(i)
        winscore = 4 - self.winner.index(get_teammate(self.winner[0]))

        self.curTeam = self.winner[0] % 2
        self.firstPlayer = self.winner[-1]
        win_team = self.teams[self.curTeam]
        los_team = self.teams[(self.curTeam + 1) % 2]

        if win_team.level >= 12:
            if winscore >= 2:
                is_over = True
            elif win_team.level >= 14:  # 3把没过A
                win_team.level = winscore
                print(
                    "{}3把A没过, 下次从{}开始".format(
                        win_team.name, self.get_level_name(win_team.level)
                    )
                )
            else:
                win_team.level += 1
        else:
            win_team.level = min(12, win_team.level + winscore)

        self.curLevel = win_team.level

        print(
            "第{}局结束: {}  {} 赢, 得{}分 ".format(
                self.gameCount + 1,
                [self.players[i].name for i in self.winner],
                win_team.name,
                winscore,
                self.get_level_name(self.curLevel),
            )
        )
        if los_team.level >= 14:  # 3把没过A
            los_team.level = 0
            print(
                "{}3把A没过, 下次从{}开始".format(
                    los_team.name, self.get_level_name(los_team.level)
                )
            )
        print()

        if not is_over:
            self.gameCount += 1
            print(
                "第{}局开始: {} 打 {}\t现在比分 {}:{} - {}:{}".format(
                    self.gameCount + 1,
                    self.teams[self.curTeam].name,
                    self.get_level_name(self.curLevel),
                    self.teams[0].name,
                    self.get_level_name(self.teams[0].level),
                    self.teams[1].name,
                    self.get_level_name(self.teams[1].level),
                )
            )
        return is_over

    def __str__(self):
        s = f"第{self.gameCount+1}局 打{self.get_level_name()} {self.players[self.firstPlayer].name }先出"
        for p in self.players:
            s += "\n" + p.name + ":"
            for c in p.cards:
                s += str(Puke[c])
        return s


if __name__ == "__main__":
    t = Table()
    print(f"{t.teams[0].name} VS {t.teams[1].name}")
    while not t.is_game_over():
        t.begin()
        input("Enter to continue ....")
        t.play(False)
    print(f"Game Over {t.teams[t.curTeam].name} 赢了")
