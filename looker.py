import sys
import os

sys.path.append(os.getcwd())

import keyboard
from player import Player
from event import Game_Event_Cate
from enum import Enum
from out import OutCard
from puke import *


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


def strlen(s):
    if not isinstance(s, str):
        s = str(s)
    i = 0
    for c in s:
        i += 1 if ord(c) <= 255 else 2
    return i


class Looker(Player):
    def onEvent(self, e, info):
        if e == Game_Event_Cate.GE_Ready:
            self.afterReady(info)
        elif e == Game_Event_Cate.GE_Deal:
            self.afterDeal(info)
        elif e == Game_Event_Cate.GE_Anti:
            self.afterAnti(info)
        elif e == Game_Event_Cate.GE_Give:
            self.afterGive(info)
        elif e == Game_Event_Cate.GE_Back:
            self.afterBack(info)
        elif e == Game_Event_Cate.GE_Start:
            self.afterStart(info)
        elif e == Game_Event_Cate.GE_Play:
            self.afterPlay(info)
        elif e == Game_Event_Cate.GE_Over:
            self.afterOver(info)
        elif e == Game_Event_Cate.GE_End:
            self.afterEnd(info)

        return super().onEvent(e, info)

    def onInit(self):
        try:
            self.width, self.height = os.get_terminal_size()
        except OSError:
            self.width = 80
            self.height = 25
        self.width = min(100, self.width)
        self.outArea = RECT(4, 4, self.width - 3, self.height - 10)
        self.playerNames = []
        self.curTeamName = ""
        self.lookMode = True

        self.markedPos = []
        self.curX = self.curY = -1

        CSI.initScreen()

        def onEsc():
            self.lookMode = not self.lookMode

        keyboard.add_hotkey("esc", onEsc)

    def onQuit(self):
        keyboard.unhook_all()
        CSI.quit()

    def onDraw(self):
        CSI.clear()
        CSI.move_cursor(1, 1)
        CSI.reset_textStyle()
        CSI.print(f"\t当前 {self.curTeamName} 打 {Card.get_num_str(self.curLevel)}")
        self.drawPlayer()
        self.drawAllCard()
        pass

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
        card_beg = strlen(self.name) + 2
        CSI.move_cursor(card_beg + x * 3, self.height - y)
        marked = (x, y) in self.markedPos
        selected = x == self.curX and y == self.curY

        if marked:
            CSI.set_underLine()

        if c == self.redCard:
            if selected:
                CSI.set_color(CSI_Color.Default, CSI_Color.Red)
            else:
                CSI.set_color(CSI_Color.Red, CSI_Color.Default)
        else:
            if marked:
                CSI.set_color(CSI_Color.Blue, bold=True)
            if selected:
                CSI.set_select_color()

        CSI.print(f"{Puke[c]}")
        CSI.reset_textStyle()

    def drawInfo(self, info):
        CSI.move_cursor(1, self.height - 8)
        CSI.reset_textStyle()
        CSI.set_select_color()
        CSI.clearLine()
        CSI.print(info)
        CSI.reset_textStyle()

    def drawOut(self, out: OutCard):
        outstr = str(out)
        outlen = strlen(outstr)
        a = self.outArea
        padlen = a.width // 2 - outlen - 1
        if out.player == self.sit:  # 我
            CSI.move_cursor(a.centerX - outlen // 2, a.bottom)
            CSI.clearLine()
        elif out.player == (self.sit + 1) % 4:  # 下家
            CSI.move_cursor(a.centerX, a.centerY)
            outstr = (" " * padlen) + outstr
        elif out.player == (self.sit + 2) % 4:  # 对家
            CSI.move_cursor(a.centerX - outlen // 2, a.top)
            CSI.clearLine()
        elif out.player == (self.sit + 3) % 4:  # 上家
            CSI.move_cursor(a.left, a.centerY)
            outstr = outstr + (" " * padlen)
        CSI.print(outstr)

        pass

    def drawPlayer(self):
        a = self.outArea
        for i, name in enumerate(self.playerNames):
            CSI.set_color(CSI_Color.Yellow, CSI_Color.Default, True)
            if i == self.sit:  # 我
                CSI.move_cursor(a.centerX - strlen(name) // 2, a.bottom + 1)
                CSI.print(name)
            elif i == (self.sit + 1) % 4:  # 下家
                for j, n in enumerate(name):
                    CSI.move_cursor(a.right + 3, a.centerY - len(name) // 2 + j)
                    CSI.print(n)
            elif i == (self.sit + 2) % 4:  # 对家
                CSI.move_cursor(a.centerX - strlen(name) // 2, a.top - 1)
                CSI.print(name)
            elif i == (self.sit + 3) % 4:  # 上家
                for j, n in enumerate(name):
                    CSI.move_cursor(a.left - 3, a.centerY - len(name) // 2 + j)
                    CSI.print(n)
        CSI.reset_textStyle()
        pass

    def afterReady(self, info):
        self.onInit()
        pass

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
        (giver, givecard) = info
        stip = f"{self.playerNames[giver]} 贡牌 {Puke[givecard]} "
        self.drawInfo(stip)
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterBack(self, info):
        (giver, givecard, backer, backcard) = info
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
        stip = f"{self.playerNames[info]} 先出"
        self.onDraw()
        self.drawInfo(stip)
        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterPlay(self, info):
        if not isinstance(info, OutCard):
            return

        if info.player == self.sit:
            self.drawAllCard()

        self.drawOut(info)

        if self.lookMode:
            keyboard.wait("enter")
        pass

    def afterOver(self, info):
        stip = "本局结束："
        for i, p in enumerate(info):
            stip += f"{self.winner_title[i]}:{self.playerNames[p]} "
        self.drawInfo(stip)
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
        keyboard.hook(self.onKey, True)
        self.giveMode = False
        self.backMode = False
        self._playMode = False
        self.lastOut = None

    @property
    def playMode(self):
        return self._playMode

    @playMode.setter
    def playMode(self, mode: bool):
        if mode and self.numCount > 0:
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

        num = Card.get_val_num(c)
        self.numCards[num].append(c)
        c = self.getCurCard()
        self.removeCards([c])
        self.onDraw()
        return c

    def play(self, desk_outs):
        self.playMode = True
        self.lastOut = desk_outs[-1] if len(desk_outs) else None

        while self.playMode:
            CSI.flush()

        cards = self.getMarkedCards()
        out = OutCard(cards, self.curLevel, self.sit)
        if out.cate.isValid:
            self.markedPos.clear()
            self.onDraw()
            self.drawInfo(out)
            return cards
        else:
            self.drawInfo(out)

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
        # "up,down,left,right,space,esc,enter"
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
