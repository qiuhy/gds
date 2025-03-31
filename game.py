import sys
import os

sys.path.append(os.getcwd())

import random
from puke import Puke, Card
from out import OutCard
import player
import logging
from event import Game_Event
import time

logger = logging.getLogger()


class Team:
    def __init__(self, p1, p2):
        p1.partner = p2.sit
        p2.partner = p1.sit
        self.players = [p1, p2]
        self.name = p1.name + p2.name
        self.levelCount = 0
        self._level = 0  # 当前打几 index of 234567890JQKA
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


class Table:

    def __init__(self):
        self.players: list[player.Player] = [None for i in range(4)]
        self.winner: list[int] = []
        self.teams: list[Team] = []
        self.ondesk_cards: list[OutCard] = []

        self._curTeam = 0
        self.firstPlayer = 0
        self.sitName = "南东北西"  # "下右上左" "我下对上"

    @property
    def curTeam(self):
        return self.teams[self._curTeam]

    @property
    def curLevel(self):
        return self.curTeam.level

    @property
    def isFull(self):
        for i in range(4):
            if self.players[i] is None:
                return False
        return True

    def reset(self):
        self.__init__()

    def join_player(self, player: player.Player, idx=None):
        sit = None
        if idx == None:
            for idx in range(4):
                if self.players[idx] == None:
                    self.players[idx] = player
                    sit = idx
                    break
        elif self.players[idx] == None:
            self.players[idx] = player
            sit = idx

        if sit is None:
            return False
        else:
            self.broadcast(Game_Event.GE_Join, (sit, player.name))

    def leave_player(self, idx):
        self.players[idx] = None
        pass

    def create_team(self):
        for i in range(len(self.players)):
            if self.players[i] == None:
                return False
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
            self.broadcast(Game_Event.GE_Ready)
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
            p.curLevel = self.curTeam.level
        cards = [i % 54 for i in range(2 * 54)]
        random.shuffle(cards)
        i = 0
        for p in self.players:
            p.set_cards(cards[i : i + 27].copy())
            i += 27
        self.broadcast(Game_Event.GE_Deal)

    def back(self, giver, givecard, backer):
        backcard = self.players[backer].back(givecard)
        self.players[giver].get_card(backcard)
        self.broadcast(Game_Event.GE_Back, (giver, givecard, backer, backcard))

    def anti(self):
        if len(self.winner) < 2:
            return True
        # 抗贡
        double_give = self.winner[-2] == get_teammate(self.winner[-1])

        G_count1 = len(self.players[self.winner[-1]].numCards[14])
        G_count2 = len(self.players[self.winner[-2]].numCards[14]) if double_give else 0

        if G_count1 + G_count2 == 2:
            antier = []
            if G_count1:
                antier.append(self.winner[-1])
            if G_count2:
                antier.append(self.winner[-2])

            self.broadcast(Game_Event.GE_Anti, antier)
            # 抗贡 头游先出
            self.firstPlayer = self.winner[0]

            return True
        return False

    def give_back(self):
        if len(self.winner) == 0:
            return

        double_give = self.winner[-2] == get_teammate(self.winner[-1])

        give_card = [self.players[self.winner[-1]].give()]
        self.broadcast(Game_Event.GE_Give, (self.winner[-1], give_card[0]))
        if double_give:
            give_card.append(self.players[self.winner[-2]].give())
            self.broadcast(Game_Event.GE_Give, (self.winner[-2], give_card[1]))

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

    def play(self):
        firstPlayer = self.firstPlayer
        outCount = 0

        self.winner.clear()
        while not self.is_level_over():
            self.ondesk_cards.clear()

            strFirts = "先出"
            if firstPlayer in self.winner:
                firstPlayer = get_teammate(firstPlayer)
                strFirts = "接风"
                self.broadcast(Game_Event.GE_Wind, firstPlayer)
            else:
                self.broadcast(Game_Event.GE_Start, firstPlayer)

            curPlayer = self.players[firstPlayer]

            passed = 0
            nextPlayer = firstPlayer
            while passed < len(self.players) - 1 and not self.is_level_over():
                if nextPlayer in self.winner:
                    passed += 1
                else:
                    curPlayer = self.players[nextPlayer]
                    out = curPlayer.action(self.ondesk_cards)
                    self.broadcast(
                        Game_Event.GE_Play,
                        (nextPlayer, out.cardValues, curPlayer.cardCount),
                    )
                    outCount += 1

                    if out.cate.isValid:
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
        self.gameCount += 1

        curTeamWin = self._curTeam == self.winner[0] % 2
        if self.curTeam.level == 12:
            if curTeamWin and winscore >= 2:
                is_over = True
            elif self.curTeam.levelCount == 3:  # 3把没过A
                self.curTeam.level = 0
                # logger.debug(f"{self.curTeam.name}3把A没过, 回到2")

        self._curTeam = self.winner[0] % 2
        self.firstPlayer = self.winner[-1]

        if not is_over:
            self.curTeam.level = min(12, self.curTeam.level + winscore)

        return is_over

    def run(self):
        while not self.is_game_over():
            self.deal()
            if not self.anti():
                self.give_back()
            self.play()
            self.broadcast(Game_Event.GE_Over)
        self.broadcast(Game_Event.GE_End)

    def broadcast(self, e: Game_Event, info=None):
        if e == Game_Event.GE_Join:
            sit = info[0]
            playerName = info[1]
            logger.info(f"Table: {playerName} join {self.sitName[sit]}")
        elif e == Game_Event.GE_Ready:
            info = [p.name if p else None for p in self.players]
            logger.info(
                f"Table: Ready [{self.teams[0].name}] VS [{self.teams[1].name}]"
            )
        elif e == Game_Event.GE_Deal:
            info = [self.curTeam.name, self.curLevel]
        elif e == Game_Event.GE_Start:
            if info is None:
                info = self.firstPlayer
        elif e == Game_Event.GE_Wind:
            # logger.debug(f"[{self.sitName[firstPlayer]}] {curPlayer.name} {strFirts}")
            pass
        elif e == Game_Event.GE_Over:
            info = self.winner
            # logger.debug(
            #     "第{}局结束: {}  {} 赢 {}分 \n".format(
            #         self.gameCount,
            #         [self.players[i].name for i in self.winner],
            #         self.curTeam.name,
            #         winscore,
            #     )
            # )
            # logger.debug(
            #     "第{}局开始: {} 打 {}\t现在比分 {}:{} - {}:{}".format(
            #         self.gameCount + 1,
            #         self.curTeam.name,
            #         self.get_level_name(self.curLevel),
            #         self.teams[0].name,
            #         self.get_level_name(self.teams[0].level),
            #         self.teams[1].name,
            #         self.get_level_name(self.teams[1].level),
            #     )
            # )
        elif e == Game_Event.GE_End:
            info = [p.sit for p in self.curTeam.players]
            logger.info(
                "Table: End [{}] 获胜 {}把过A 打了{}局, 比分 [{}]:{} - [{}]:{} \n".format(
                    self.curTeam.name,
                    self.curTeam.levelCount,
                    self.gameCount,
                    self.teams[0].name,
                    self.get_level_name(self.teams[0].level),
                    self.teams[1].name,
                    self.get_level_name(self.teams[1].level),
                )
            )
        elif e == Game_Event.GE_Back:
            # logger.debug(
            #     "{} 贡牌 {} 给 {}, 得到还牌 {}".format(
            #         self.players[giver].name,
            #         Puke[givecard],
            #         self.players[backer].name,
            #         Puke[backcard],
            #     )
            # )
            pass
        elif e == Game_Event.GE_Anti:
            # antier_name = [self.players[p].name for p in antier]
            # logger.debug(f"{antier_name} 抗贡!!!")
            pass
        elif e == Game_Event.GE_Play:
            # tip = str(curPlayer)
            # if out.cate.isValid:
            #     val = out
            #     if curPlayer.cardCount == 0:
            #         tip = curPlayer.winner_title[len(self.winner)]
            # else:
            #     val = out.cate.value
            # logger.debug(
            #     f"[{self.sitName[curPlayer.sit]}] {curPlayer.name}:{val}\t{tip}"
            # )
            pass
        elif info is None:
            return
        for p in self.players:
            if p:
                p.onEvent(e, info)
        time.sleep(1)

    def __str__(self):
        if len(self.teams) == 0:
            return "未组队,或玩家人数不足"
        s = f"第{self.gameCount+1}局 打{self.get_level_name()} {self.players[self.firstPlayer].name }先出"
        for i in range(len(self.sitName)):
            s += f"\n[{self.sitName[i]}] {self.players[i]}"
        return s


def new(user: player.Player):
    t = Table()
    t.join_player(user)  # t.join_player(player.Player("东邪"))
    for i in range(3):
        t.join_player(player.Player(f"电脑({i+1})"))
    if t.start():
        t.run()


def main():
    t = Table()
    t.join_player(player.Player("南帝"))
    t.join_player(player.Player("东邪"))
    t.join_player(player.Player("北丐"))
    t.join_player(player.Player("西毒"))

    if t.start():
        t.run()


if __name__ == "__main__":
    main()
