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

        CSI.move_cursor(1, self.height)
        CSI.clearLine()
        CSI.print(f"{e.value} {info}")
        return super().onEvent(e, info)

    def onInit(self):
        try:
            self.width, self.height = os.get_terminal_size()
        except OSError:
            self.width = 80
            self.height = 25

        self.playerNames = []
        self.curTeamName = ""
        self.waitLook = True

        CSI.initScreen()

        def onEsc():
            self.waitLook = not self.waitLook

        keyboard.add_hotkey("esc", onEsc)

    def onQuit(self):
        keyboard.unhook_all()
        CSI.quit()

    def onDraw(self, info=None):
        CSI.clear()
        CSI.move_cursor(1, 1)
        CSI.reset_textStyle()
        CSI.print(f"玩家：{self.playerNames}")
        CSI.print(f"\t当前 {self.curTeamName} 打 {Card.get_num_str(self.curLevel)}")
        self.drawAllCard()
        if not info is None:
            CSI.move_cursor(1, self.height)
            CSI.print(info)
        pass

    def drawAllCard(self):
        CSI.move_cursor(1, self.height - 1)
        CSI.clearLine()
        CSI.print(f"{self}")

    def afterReady(self, info):
        self.onInit()
        pass

    def afterDeal(self, info):
        self.curTeamName = info
        self.onDraw()
        pass

    def afterAnti(self, info):
        pass

    def afterGive(self, info):
        pass

    def afterBack(self, info):
        pass

    def afterStart(self, info):
        stip = f"{self.playerNames[info]} 先出"
        self.onDraw(stip)
        if self.waitLook:
            keyboard.wait("enter")
        pass

    def afterPlay(self, info):
        if not isinstance(info, OutCard):
            return

        outstr: str = ""
        if info.player == self.sit:
            outstr = "我：" + self.name + " " + str(info)
            CSI.move_cursor((self.width - len(outstr.encode())) // 2, self.height - 3)
            CSI.clearLine()
        elif info.player == (self.sit + 1) % 4:
            outstr = "下家：" + self.playerNames[info.player] + " " + str(info)
            CSI.move_cursor(self.width // 2, self.height // 2)
            CSI.clearLine(0)
            CSI.move_cursor(self.width - len(outstr.encode()), self.height // 2)
        elif info.player == (self.sit + 2) % 4:
            outstr = "对家：" + self.playerNames[info.player] + " " + str(info)
            CSI.move_cursor((self.width - len(outstr.encode())) // 2, 2)
            CSI.clearLine()
        elif info.player == (self.sit + 3) % 4:
            outstr = "上家：" + self.playerNames[info.player] + " " + str(info)
            CSI.move_cursor(self.width // 2, self.height // 2)
            CSI.clearLine(1)
            CSI.move_cursor(1, self.height // 2)
        CSI.print(outstr)

        if info.player == self.sit:
            CSI.move_cursor(1, self.height - 1)
            CSI.clearLine()
            CSI.print(self)

        if self.waitLook:
            keyboard.wait("enter")
        pass

    def afterOver(self, info):
        pass

    def afterEnd(self, info):
        self.onQuit()
        pass


class JPX(Looker):
    def onInit(self):
        super().onInit()
        keyboard.unhook_all()
        self.name = "键盘侠"
        self.select_beg = 0
        self.marked = []
        self.curX = self.curY = -1

    @property
    def playMode(self):
        return self.curX != -1

    @playMode.setter
    def playMode(self, mode: bool):
        if mode and self.numCount > 0:
            self.curX = 0
            self.curY = 0
            self.drawCurCard()
            keyboard.hook(self.onKey, True)
        else:
            keyboard.unhook_all()
            self.curX = self.curY = -1

    def play(self, desk_outs):
        self.playMode = True
        while self.playMode:
            CSI.flush()

        return self.getMarkedCard()

    def getMarkedCard(self):
        makredCard = []
        for x, num in enumerate(self.allNums):
            for y, c in enumerate(self.numCards[num]):
                if (x + y * 100) in self.marked:
                    makredCard.append(c)

        out = OutCard(makredCard, self.curLevel, self.sit)
        if out.cate.isValid:
            self.marked.clear()
            self.onDraw(f"{out}")
            return makredCard
        else:
            CSI.move_cursor(1, self.height)
            CSI.clearLine()
            CSI.print(out)
            return []

    def onKey(self, e: keyboard.KeyboardEvent):
        # "up,down,left,right,space,esc,enter"
        if self.playMode:
            if e.event_type == "up" and e.name == "q":
                self.marked.clear()
                self.playMode = False
            elif e.event_type == "up" and e.name == "enter":
                if len(self.marked):
                    if self.checkMarkedCard():
                        self.playMode = False
            if e.event_type == "down" and e.name == "esc":
                self.marked.clear()
                self.drawAllCard()
            elif e.event_type == "down" and e.name in ["left", "right", "up", "down"]:
                self.drawCurCard(False)
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
                self.drawCurCard()
            elif e.event_type == "down" and e.name == "space":
                t = self.curX + self.curY * 100
                if t in self.marked:
                    self.marked.remove(t)
                else:
                    self.marked.append(t)
                self.drawCurCard()

        else:
            # giveMode backMode
            pass

        return False

    def checkMarkedCard(self):
        makredCard = []
        for x, num in enumerate(self.allNums):
            for y, c in enumerate(self.numCards[num]):
                if (x + y * 100) in self.marked:
                    makredCard.append(c)

        out = OutCard(makredCard, self.curLevel, self.sit)

        CSI.move_cursor(1, self.height)
        CSI.clearLine()
        CSI.print(out)

        return out.cate.isValid

    def onDraw(self, info=None):
        return super().onDraw(info)
    
    def drawAllCard(self):
        CSI.move_cursor(1, self.height - 1)
        CSI.print(f"{self.name}:")
        self.select_beg = len(self.name) + 2

        for x, num in enumerate(self.allNums):
            for y, c in enumerate(self.numCards[num]):
                self.drawCard(x, y, c)

    def drawCard(self, x, y, c, selected=True):
        CSI.move_cursor(self.select_beg + x * 3, self.height - y - 1)
        t = x + y * 100
        mark = (x + y * 100) in self.marked
        if c == self.redCard:
            if mark:
                CSI.set_color(CSI_Color.Default, CSI_Color.Red, bold=self.marked)
            else:
                CSI.set_color(CSI_Color.Red, CSI_Color.Default, bold=self.marked)
        else:
            CSI.set_color(CSI_Color.Default, bold=self.marked)
            if mark:
                CSI.set_select_color()

        if selected and x == self.curX and y == self.curY:
            CSI.set_underLine()
        CSI.print(f"{Puke[c]}")
        CSI.reset_textStyle()

    def drawCurCard(self, selected=True):
        for x, num in enumerate(self.allNums):
            if x != self.curX:
                continue
            for y, c in enumerate(self.numCards[num]):
                if y == self.curY:
                    self.drawCard(x, y, c, selected)


import random

if __name__ == "__main__":
    cards = [i % 54 for i in range(54 * 2)]
    random.shuffle(cards)
    player = JPX()
    player.curLevel = 8
    player.set_cards(cards[0:27])
    player.onInit()
    player.onDraw("\t\t\t" "测试... [Q]Pass [Enter]出牌")
    player.playMode = True
    while player.playMode:
        CSI.flush()
    CSI.move_cursor(1, player.height)
    CSI.print("\t\t\tPress [Enter] to quit")
    keyboard.wait("enter")
    player.onQuit()
