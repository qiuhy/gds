import random
from puke import Puke, Card
from out import OutCard
import player


class Team:

    _level = 0  # 当前打几 index of 234567890JQKA

    def __init__(self, p1, p2):
        p1.partner = p2.sit
        p2.partner = p1.sit
        self.players = [p1, p2]
        self.name = p1.name + p2.name
        self.levelCount = 0
        self.on_desk = False  # 在台上
        self.level = 0

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if self._level == level:
            self.levelCount += 1
        else:
            self._level = level
            self.levelCount = 1


def get_teammate(s):
    return (s + 2) % 4


winner_title = ["头游", "二游", "三游", "末游"]


class Table:
    def __init__(self):
        self.sitName = "南东北西"  # "下右上左" "我下对上"
        self.players: list[player.Player] = [None for i in range(4)]
        self.winner = []
        self.ondesk_cards = []
        self.teams = []

        self._curTeam = 0
        self.firstPlayer = 0

    @property
    def curTeam(self):
        return self.teams[self._curTeam]

    @property
    def curLevel(self):
        return self.curTeam.level

    def join_player(self, player: player.Player, idx=None):
        if idx == None:
            for idx in range(4):
                if self.players[idx] == None:
                    self.players[idx] = player
                    return True
        elif self.players[idx] == None:
            self.players[idx] = player
            return True

        return False

    def leave_player(self, idx):
        self.players[idx] = None
        pass

    def create_team(self):
        for i in range(len(self.players)):
            if self.players[i] == None:
                return False
            self.players[i].name = self.sitName[i]
            self.players[i].sit = i

        self.teams = [
            Team(self.players[0], self.players[2]),
            Team(self.players[1], self.players[3]),
        ]
        return True

    def start(self):
        if self.create_team():
            self.firstPlayer = random.randint(0, 3)
            self._curTeam = self.firstPlayer % 2
            self.gameCount = 0
            self.winner = []
            self.ondesk_cards = []
            return True
        return False

    def get_nextPlayer(self, player):
        n = (player + 1) % len(self.players)
        return n

    def get_level_name(self, level=None):
        if level == None:
            level = self.curLevel
        levelname = ""
        if level == 12:
            levelname = str(self.curTeam.levelCount)
        levelname += Card.get_num_str(level)
        return levelname

    def deal(self):
        for p in self.players:
            p.curLevel = self.curLevel
        cards = [i % 54 for i in range(2 * 54)]
        random.shuffle(cards)
        i = 0
        for p in self.players:
            p.set_cards(cards[i : i + 27])
            i += 27

    def back(self, giver, givecard, backer):
        backcard = self.players[backer].back(givecard)
        self.players[giver].get_back(backcard)
        print(
            "{} 贡牌 {} 给 {}, 得到还牌 {}".format(
                self.players[giver].name,
                Puke[givecard],
                self.players[backer].name,
                Puke[backcard],
            )
        )

    def give(self):
        if len(self.winner) == 0:
            return

        double_give = self.winner[-2] == get_teammate(self.winner[-1])

        G_count = len(self.players[self.winner[-1]].numCards[14])
        if double_give:
            G_count += len(self.players[self.winner[-2]].numCards[14])

        if G_count == 2:
            if double_give:
                print(self.teams[self.winner[-1] % 2].name, "抗贡!!!")
            else:
                print(self.players[self.winner[-1]].name, "抗贡!!!")
            # 抗贡 头游先出
            self.firstPlayer = self.winner[0]
            return

        give_card = [self.players[self.winner[-1]].give()]
        if double_give:
            give_card.append(self.players[self.winner[-2]].give())

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

                self.firstPlayer = big_giver
            else:
                # 如果双方进贡的牌一样大，则按照顺时针方向进贡,头游的下家先出
                self.back(self.winner[-1], give_card[0], self.winner[0])
                self.back(self.winner[-2], give_card[1], self.winner[1])
                self.firstPlayer = self.get_nextPlayer(self.winner[0])
        else:
            # 单贡 末游先出
            self.back(self.winner[-1], give_card[0], self.winner[0])
            self.firstPlayer = self.winner[-1]

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
                    f"({self.players[firstPlayer].cardCount})",
                    strFirts,
                )
            passed = 0
            nextPlayer = firstPlayer
            while passed < len(self.players) - 1:
                if nextPlayer in self.winner:
                    passed += 1
                else:
                    curPlayer = self.players[nextPlayer]
                    outcate = curPlayer.action(self.ondesk_cards)
                    outCount += 1

                    if showOut:
                        if outcate.isValid():
                            out = self.ondesk_cards[-1]
                            print(
                                curPlayer.name,
                                ":",
                                out,
                                out.val_str(),
                                end=" ",
                            )
                            if curPlayer.cardCount == 0:
                                print("\t", winner_title[len(self.winner)])
                            else:
                                print(f"\t({curPlayer.cardCount})")
                        else:
                            print(
                                curPlayer.name,
                                ":",
                                outcate.value,
                                f"\t({curPlayer.cardCount})",
                            )

                    if outcate.isValid():
                        if curPlayer.cardCount == 0:
                            self.winner.append(nextPlayer)
                        firstPlayer = nextPlayer
                        passed = 0
                    else:
                        passed += 1

                nextPlayer = self.get_nextPlayer(nextPlayer)

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

        if self._curTeam == (self.winner[0] + 1) % 2:
            los_team = self.curTeam
            if los_team.level == 12 and los_team.levelCount == 3:  # 3把没过A
                los_team.level = 0
                print(
                    "{}3把A没过, 下次从{}开始".format(
                        los_team.name, self.get_level_name(los_team.level)
                    )
                )

        self._curTeam = self.winner[0] % 2
        self.firstPlayer = self.winner[-1]
        win_team = self.curTeam
        if win_team.level == 12:
            if winscore >= 2:
                is_over = True
            elif win_team.levelCount > 3:  # 3把没过A
                win_team.level = winscore
                print(
                    "{}3把A没过, 下次从{}开始".format(
                        win_team.name, self.get_level_name(win_team.level)
                    )
                )
        win_team.level = min(12, win_team.level + winscore)

        print(
            "第{}局结束: {}  {} 赢, 得{}分 ".format(
                self.gameCount + 1,
                [self.players[i].name for i in self.winner],
                win_team.name,
                winscore,
            )
        )

        print()

        if not is_over:
            self.gameCount += 1

        return is_over

    def run(self):
        while not self.is_game_over():
            print(
                "第{}局开始: {} 打 {}\t现在比分 {}:{} - {}:{}".format(
                    self.gameCount + 1,
                    self.curTeam.name,
                    self.get_level_name(self.curLevel),
                    self.teams[0].name,
                    self.get_level_name(self.teams[0].level),
                    self.teams[1].name,
                    self.get_level_name(self.teams[1].level),
                )
            )

            self.deal()
            self.give()
            print(self)
            input("Enter to continue ....")
            self.play(True)

    def __str__(self):
        if len(t.teams) == 0:
            return "未组队,或玩家人数不足"
        s = f"第{self.gameCount+1}局 打{self.get_level_name()} {self.players[self.firstPlayer].name }先出"
        for p in self.players:
            s += "\n" + str(p)
        return s


if __name__ == "__main__":
    t = Table()
    for i in range(4):
        t.join_player(player.Player())

    if t.start():
        t.run()
        print(f"Game Over {t.curTeam.name} 赢了")
