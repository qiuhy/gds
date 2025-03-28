import sys
import os

sys.path.append(os.getcwd())

import keyboard
from player import Player
from event import Game_Event
from enum import Enum
from out import OutCard
from puke import *
import time


class CSI_Color(Enum):
    # +30 前景色
    # +40 背景色
    # +60 粗体
    Black = 0
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Purple = 5
    Cyan = 6
    White = 7
    Default = 9  # 默认色

    # Other = 8  # 扩展色


class CSI:
    @staticmethod
    def faceColor(c: CSI_Color, bold=False):
        if c is None:
            return 39
        return c.value + 30 + (60 if bold else 0)

    @staticmethod
    def backColor(c: CSI_Color, bright=False):
        if c is None:
            return 49
        return c.value + 40 + (60 if bright else 0)

    @staticmethod
    def move_cursor(x, y):
        sys.stdout.write(f"\033[{y};{x}H")

    @staticmethod
    def set_select_color():
        # 交换前景色和背景色
        sys.stdout.write(f"\033[7m")

    @staticmethod
    def set_underLine():
        # 下划线
        sys.stdout.write(f"\033[4m")
        # 关闭下划线
        # sys.stdout.write(f"\033[23m")

    @staticmethod
    def set_color(face: CSI_Color, back: CSI_Color = CSI_Color.Default, bold=False):
        faceColor = CSI.faceColor(face, bold)
        backColor = CSI.backColor(back, bold)
        if faceColor == 39 and backColor == 49:
            sys.stdout.write(f"\033[0m")
        else:
            sys.stdout.write(f"\033[{faceColor};{backColor}m")

    @staticmethod
    def reset_textStyle():
        sys.stdout.write(f"\033[0m")

    @staticmethod
    def clear():
        sys.stdout.write("\033[2J")  # 清屏

    @staticmethod
    def clearLine(mode=2):
        # 0 的擦除范围是从当前光标位置（含）到行/显示的末尾
        # 1 的擦除范围是从行/显示开始到当前光标位置（含）
        # 2 的擦除范围是整行/显示
        sys.stdout.write(f"\033[{mode}K")  # Clear to the end of line

    @staticmethod
    def set_cursor(mode=-1):
        # 0 用户配置的默认游标形状
        # 1 闪烁块游标形状
        # 2 稳定块游标形状
        # 3 闪烁下划线游标形状
        # 4 稳定下划线游标形状
        # 5 闪烁条游标形状
        # 6 稳定条游标形状
        if mode >= 0 and mode <= 6:
            sys.stdout.write("\033[?25h")  # 恢复光标
            sys.stdout.write("\033[?12h")
            sys.stdout.write(f"\033[{mode}q")
        else:
            sys.stdout.write("\033[?25l")  # 隐藏光标

    @staticmethod
    def initScreen():
        sys.stdout.write("\033[?1049h")  # 使用备用屏幕
        CSI.set_cursor()  # 隐藏光标
        sys.stdout.write("\033[2J")  # 清屏

    @staticmethod
    def quit():
        sys.stdout.write("\033[2J")  # 清屏
        sys.stdout.write("\033[0m")  # 恢复字体
        CSI.set_cursor(0)  # 恢复光标
        sys.stdout.write("\033[?1049l")  # 恢复屏幕
        sys.stdout.write("\033[!p")  # 将某些终端设置重置为默认值。

    @staticmethod
    def flush():
        sys.stdout.flush()

    @staticmethod
    def print(s):
        print(s, end="")


class RECT:
    def __init__(self, left, top, right, bottom):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    @property
    def width(self):
        return self.right - self.left + 1

    @property
    def height(self):
        return self.bottom - self.top + 1

    @property
    def centerX(self):
        return self.left + self.width // 2

    @property
    def centerY(self):
        return self.top + self.height // 2


class Looker(Player):
    def onEvent(self, e, info):
        super().onEvent(e, info)
        if e == Game_Event.GE_Ready:
            self.afterReady(info)
        elif e == Game_Event.GE_Dealing:
            self.set_cards(info)
        elif e == Game_Event.GE_Deal:
            self.afterDeal(info)
        elif e == Game_Event.GE_Anti:
            self.afterAnti(info)
        elif e == Game_Event.GE_Give:
            self.afterGive(info)
        elif e == Game_Event.GE_Back:
            self.afterBack(info)
        elif e == Game_Event.GE_Start:
            self.afterStart(info)
        elif e == Game_Event.GE_Wind:
            self.afterWind(info)
        elif e == Game_Event.GE_Play:
            self.afterPlay(info)
        elif e == Game_Event.GE_Over:
            self.afterOver(info)
        elif e == Game_Event.GE_End:
            self.afterEnd(info)

        CSI.flush()

    def onInit(self):
        try:
            self.width, self.height = os.get_terminal_size()
        except OSError:
            self.width = 80
            self.height = 25
        self.width = min(100, self.width)
        self.outArea = RECT(11, 4, self.width - 11, self.height - 10)
        self.playerRestCards = [27, 27, 27, 27]
        self.winner = []
        self.curTeamName = ""
        self.lookMode = True

        self.markedPos = []
        self.curX = self.curY = -1

        CSI.initScreen()

        def onEsc():
            self.lookMode = not self.lookMode

        keyboard.add_hotkey("f12", onEsc)

    def onQuit(self):
        keyboard.unhook_all()
        CSI.quit()

    def onDraw(self):
        CSI.clear()
        self.drawHead()
        self.drawPlayer()
        self.drawAllCard()

    def drawHead(self, info=None):
        CSI.reset_textStyle()
        CSI.move_cursor(1, 1)
        stip = f"\t当前 {self.curTeamName} 打 {Card.get_num_str(self.curLevel)}"
        CSI.print(f"{stip:{self.width}}")
        if not info is None:
            CSI.move_cursor(1, 2)
            CSI.print(f"{info:{self.width}}")

    def drawAllCard(self, pos=[]):
        CSI.reset_textStyle()
        if len(pos) == 0:
            for i in range(8):
                CSI.move_cursor(1, self.height - i)
                CSI.clearLine()

        CSI.move_cursor(1, self.height)
        CSI.print(f"{self.name}:")
        for x, num in enumerate(self.allNums):
            for y, c in enumerate(self.numCards[num]):
                if len(pos) == 0 or (x, y) in pos:
                    self.drawCard(x, y, c)

    def drawCard(self, x, y, c):
        card_beg = (self.width - self.numCount * 3) // 2
        CSI.move_cursor(card_beg + x * 3, self.height - y)
        marked = (x, y) in self.markedPos
        selected = x == self.curX and y == self.curY

        cate_color = [
            CSI_Color.Blue,
            CSI_Color.Green,
            CSI_Color.Yellow,
            CSI_Color.Purple,
            CSI_Color.Cyan,
            CSI_Color.Cyan,
        ]

        if c == self.redCard:
            color = CSI_Color.Red
        else:
            color = cate_color[Card.get_val_cate(c)]

        if marked:
            CSI.set_color(CSI_Color.Default, color, bold=True)
        else:
            CSI.set_color(color, CSI_Color.Default, bold=True)
        if selected:
            CSI.set_underLine()

        CSI.print(str(Puke[c]))
        CSI.reset_textStyle()

    def drawInfo(self, info):
        CSI.move_cursor(1, self.height - 8)
        CSI.reset_textStyle()
        CSI.set_select_color()
        CSI.print(f"{str(info):<{self.width}}")
        CSI.reset_textStyle()

    def drawOut_str(self, player, outstr):
        a = self.outArea
        if player == self.sit:  # 我
            CSI.move_cursor(a.left, a.bottom)
            CSI.print(f"{outstr:^{a.width}}")
        elif player == (self.sit + 1) % 4:  # 下家
            CSI.move_cursor(a.centerX, a.centerY)
            CSI.print(f"{outstr:^{a.width//2}}")
        elif player == (self.sit + 2) % 4:  # 对家
            CSI.move_cursor(a.left, a.top)
            CSI.print(f"{outstr:^{a.width}}")
        elif player == (self.sit + 3) % 4:  # 上家
            CSI.move_cursor(a.left, a.centerY)
            CSI.print(f"{outstr:^{a.width//2}}")

    def drawOut(self, out: OutCard):
        self.drawOut_str(out.player, str(out))

    def drawPlayer(self):
        a = self.outArea
        name: str
        for i, name in enumerate(self.playerNames):
            info = ""
            if self.playerRestCards[i] == 0:
                if i not in self.winner:
                    self.winner.append(i)
                info = f"({self.winner_title[self.winner.index(i)]})"
            elif self.playerRestCards[i] <= 10:
                info = f"({self.playerRestCards[i]})"

            CSI.set_color(CSI_Color.Yellow, CSI_Color.Default, True)
            if i == self.sit:  # 我
                CSI.move_cursor(a.left, a.bottom + 1)
                CSI.print(f"{name + " "+ info :^{a.width}}")
            elif i == (self.sit + 2) % 4:  # 对家
                CSI.move_cursor(a.left, a.top - 1)
                CSI.print(f"{name + " "+ info:^{a.width}}")
            elif i == (self.sit + 1) % 4:  # 下家
                CSI.move_cursor(a.right + 1, a.centerY)
                CSI.print(f"{name:^10}")
                CSI.move_cursor(a.right + 1, a.centerY + 1)
                CSI.print(f"{info:^10}")
            elif i == (self.sit + 3) % 4:  # 上家
                CSI.move_cursor(a.left - 11, a.centerY)
                CSI.print(f"{name:^10}")
                CSI.move_cursor(a.left - 11, a.centerY + 1)
                CSI.print(f"{info:^10}")
        CSI.reset_textStyle()
        pass

    def drawOutTip(self, player):
        a = self.outArea
        outTip = "↓→↑←"
        CSI.move_cursor(a.centerX, a.centerY)
        CSI.reset_textStyle()
        CSI.set_color(CSI_Color.Yellow)
        CSI.print(outTip[(4 + player - self.sit) % 4])
        CSI.reset_textStyle()

    def afterReady(self, info):
        self.onInit()

    def afterDeal(self, info):
        self.curTeamName = info
        self.onDraw()
        pass

    def afterAnti(self, info):
        self.drawInfo(f"{[self.playerNames[p] for p in info]} 抗贡!!!")
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterGive(self, info):
        giver = info[0]
        givecard= info[1]
        # (giver, givecard) = info
        self.drawInfo(f"{self.playerNames[giver]} 贡牌 {Puke[givecard]} ")
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterBack(self, info):
        giver = info[0]
        givecard= info[1]
        backer = info[2]
        backcard= info[3]
        # (giver, givecard, backer, backcard) = info
        stip = "{} 贡牌 {} 给 {}, 得到还牌 {}".format(
            self.playerNames[giver],
            Puke[givecard],
            self.playerNames[backer],
            Puke[backcard],
        )
        self.drawInfo(stip)
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterStart(self, info):
        self.onDraw()
        self.drawInfo(f"{self.playerNames[info]} 先出")
        self.drawOutTip(info)
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterWind(self, info):
        self.onDraw()
        self.drawInfo(f"{self.playerNames[info]} 接风")
        self.drawOutTip(info)
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterPlay(self, info):
        if len(info) != 3:
            return
        outer = info[0]
        outcards = info[1]
        cardCount = info[2]
        # (outer, outcards, cardCount) = info
        out = OutCard(outcards, self.curLevel, outer)

        self.playerRestCards[out.player] = cardCount
        self.drawPlayer()

        if out.player == self.sit:
            self.drawAllCard()

        self.drawOut(out)
        self.drawInfo(f"{self.playerNames[out.player]}:{out}")

        nextplayer = (out.player + 1) % 4
        while nextplayer in self.winner:
            nextplayer = (nextplayer + 1) % 4

        self.drawOutTip(nextplayer)

        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterOver(self, info):
        stip = "本局结束："
        for i, p in enumerate(info):
            stip += f"{self.winner_title[i]}:{self.playerNames[p]} "
        self.drawInfo(stip)
        self.winner = []
        self.playerRestCards = [27, 27, 27, 27]
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterEnd(self, info):
        stip = f"游戏结束 {[self.playerNames[p] for p in info]}赢了！"
        self.drawInfo(stip)
        if self.lookMode:
            keyboard.wait("enter")
        self.onQuit()
        pass


class JPX(Looker):
    def __init__(self, name=""):
        super().__init__(name)
        if self.name == "":
            self.name = "键盘侠"

    def onInit(self):
        super().onInit()
        self.lookMode = False
        keyboard.unhook_all()
        self._playMode = False
        self.giveMode = False
        self.backMode = False
        self.lastOut = None
        keyboard.hook(self.onKey, True)

    @property
    def playMode(self):
        return self._playMode

    @playMode.setter
    def playMode(self, mode: bool):
        if mode and self.numCount > 0:
            # for x, num in enumerate(self.allNums):
            #     if x == self.curX:
            #         break
            # else:
            #     self.curX = 0
            # if self.curY >= len(self.numCards[num]):
            #     self.curY = len(self.numCards[num]) - 1
            if self.curX == -1:
                self.curX = 0
                self.curY = 0
            self.drawAllCard([(self.curX, self.curY)])
            self._playMode = True
        else:
            self._playMode = False

    def give(self):
        ## 贡牌
        self.drawInfo(f"贡牌：[Enter]")

        self.giveMode = True
        while self.giveMode:
            CSI.flush()

        c = self.getCurCard()
        self.removeCards([c])
        self.onDraw()
        return c

    def back(self, c):
        # 得到贡牌，再还牌
        self.drawInfo(f"得到贡牌:{Puke[c]} 还牌：[Enter]")

        self.backMode = True
        while self.backMode:
            CSI.flush()

        backcard = self.getCurCard()
        self.removeCards([backcard])
        num = Card.get_val_num(c)
        self.numCards[num].append(c)
        self.onDraw()
        return backcard

    def play(self, desk_outs):
        self.playMode = True
        self.lastOut = desk_outs[-1] if len(desk_outs) else None
        # self.drawOut_str(self.sit, "")
        while self.playMode:
            CSI.flush()

        cards = self.getMarkedCards()
        out = OutCard(cards, self.curLevel, self.sit)
        if out.cate.isValid:
            self.markedPos.clear()
        return cards

    def getCurCard(self):
        cards = self.getPosCards([(self.curX, self.curY)])
        if len(cards):
            return cards[0]
        else:
            return None

    def getMarkedCards(self):
        return self.getPosCards(self.markedPos)

    def getPosCards(self, pos):
        cards = []
        for x, num in enumerate(self.allNums):
            for y, c in enumerate(self.numCards[num]):
                if (x, y) in pos:
                    cards.append(c)
        return cards

    def onKey(self, e: keyboard.KeyboardEvent):
        if self.playMode:
            if e.event_type == "up" and e.name == "q":
                self.markedPos.clear()
                self.playMode = False
            elif e.event_type == "up" and e.name == "enter":
                if len(self.markedPos):
                    if self.checkPlayCards():
                        self.playMode = False
        elif self.giveMode:
            if e.event_type == "up" and e.name == "enter":
                if self.checkGiveCard():
                    self.giveMode = False
        elif self.backMode:
            if e.event_type == "up" and e.name == "enter":
                if self.checkBackCard():
                    self.backMode = False

        if self.cardCount:
            if e.event_type == "down" and e.name == "esc":
                self.markedPos.clear()
                self.drawAllCard()
            elif e.event_type == "down" and e.name in ["left", "right", "up", "down"]:
                prvX = self.curX
                prvY = self.curY
                if e.name == "left":
                    self.curX = (self.curX - 1) % self.numCount
                elif e.name == "right":
                    self.curX = (self.curX + 1) % self.numCount

                for x, num in enumerate(self.allNums):
                    if x == self.curX:
                        break
                if e.name == "up":
                    self.curY = (self.curY + 1) % len(self.numCards[num])
                elif e.name == "down":
                    self.curY = (self.curY - 1) % len(self.numCards[num])

                if self.curY >= len(self.numCards[num]):
                    self.curY = len(self.numCards[num]) - 1

                self.drawAllCard([(prvX, prvY), (self.curX, self.curY)])
            elif e.event_type == "down" and e.name == "space":
                curPos = (self.curX, self.curY)
                if curPos in self.markedPos:
                    self.markedPos.remove(curPos)
                else:
                    self.markedPos.append(curPos)
                self.drawAllCard([curPos])
            elif e.event_type == "up" and e.name == "z":
                if len(self.markedPos):
                    self.onSaveCard()

        CSI.flush()
        return False

    def checkGiveCard(self):
        for num in self.allNums:
            if num == self.curLevel:
                for c in self.numCards[num]:
                    if c != self.redCard:
                        break
            else:
                break
        c = self.getCurCard()
        return num == Card.get_val_num(c)

    def checkBackCard(self):
        c = self.getCurCard()
        return self.isValidBackCard(c)

    def checkPlayCards(self):
        markedCard = self.getMarkedCards()
        out = OutCard(markedCard, self.curLevel, self.sit)
        self.drawInfo(out)
        if self.playMode:
            if self.lastOut is None:
                return out.cate.isValid
            elif self.lastOut >= out:
                return False
            else:
                return True
        else:
            return out.cate.isValid

    def onSaveCard(self):
        markedCard = self.getMarkedCards()
        out = OutCard(markedCard, self.curLevel, self.sit)
        if out.cate.isValid:
            # self.savedOut.append(markedCard)
            # TODO
            pass

    def afterPlay(self, info):
        super().afterPlay(info)
        time.sleep(random.random() * 3)


import random

if __name__ == "__main__":
    cards = [i % 54 for i in range(54 * 2)]
    random.shuffle(cards)
    player = JPX()
    player.curLevel = 8
    player.set_cards(cards[0:27].copy())
    player.onInit()
    player.onDraw()
    player.drawInfo("[Q]退出 [Enter]出牌")
    player.playMode = True
    while player.playMode:
        CSI.flush()
    player.onQuit()
