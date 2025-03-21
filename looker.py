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
    # Other = 38  # 前景扩展色
    # Default = 39  # 前景默认色
    # 7 交换前景色和背景色
    # 4 下划线
    # 1 粗体


class CSI:
    @staticmethod
    def faceColor(c: CSI_Color, bold=False):
        if c is None:
            return 39
        return c.value + 30 + 60 if bold else 0

    @staticmethod
    def backColor(c: CSI_Color, bright=False):
        if c is None:
            return 49
        return c.value + 40 + 60 if bright else 0

    @staticmethod
    def move_cursor(x, y):
        sys.stdout.write(f"\033[{y};{x}H")

    @staticmethod
    def set_select_color():
        # 交换前景色和背景色
        sys.stdout.write(f"\033[7m")

    @staticmethod
    def set_color(face: CSI_Color, back: CSI_Color = None):
        faceColor = CSI.faceColor(face)
        backColor = CSI.backColor(back)
        if faceColor == 39 and backColor == 49:
            sys.stdout.write(f"\033[0m")
        else:
            sys.stdout.write(f"\033[{faceColor};{backColor}m")

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
    def reset():
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
        self.waitfor = True
        self.select_beg = 0
        self.select_end = 0
        CSI.initScreen()
        keyboard.hook(self.onKey, True)

    def onQuit(self):
        keyboard.unhook_all()
        CSI.reset()

    def onDraw(self, info=None):
        CSI.clear()
        CSI.move_cursor(1, 1)
        CSI.print(f"玩家：{self.playerNames}")
        CSI.print(f"\t当前 {self.curTeamName} 打 {Card.get_num_str(self.curLevel)}")
        CSI.move_cursor(1, self.height - 1)
        CSI.print(f"{self.name}:")
        self.select_beg = len(self.name) + 2
        self.drawCards()
        if not info is None:
            CSI.move_cursor(1, self.height)
            CSI.print(info)
        pass

    def drawCards(self):
        CSI.move_cursor(self.select_beg, self.height - 1)
        for num in reversed(self.numOrder):
            for c in self.numCards[num]:
                CSI.print(f" {Puke[c]}")


    @property
    def selectMode(self):
        return self.select_end > 0

    @selectMode.setter
    def selectMode(self, mode):
        if mode:
            self.select_end = self.cardCount
            CSI.move_cursor(self.select_beg, self.height - 1)
            self.curX = 0
        else:
            self.select_end = 0

    def onKey(self, e: keyboard.KeyboardEvent):
        # keyboard.add_hotkey("up,down,left,right,space,esc,enter",self.onKey,'')
        if e.event_type == "down" and e.name == "esc":
            self.waitfor = not self.waitfor
        elif e.event_type == "down" and e.name in ["left", "right"]:
            if self.selectMode:
                if e.name == "left":
                    self.curX = (self.curX - 1) % self.select_end
                else:
                    self.curX = (self.curX + 1) % self.select_end
                CSI.move_cursor(self.select_beg + self.curX * 3, self.height - 1)
            return False
        elif e.event_type == "up" and e.name == "space":
            return False
        return True

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
        if self.waitfor:
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

        if self.waitfor:
            keyboard.wait("enter")
        pass

    def afterOver(self, info):
        pass

    def afterEnd(self, info):
        self.onQuit()
        pass


import random

if __name__ == "__main__":
    cards = [i % 54 for i in range(54 * 2)]
    random.shuffle(cards)
    lk = Looker()
    lk.curLevel = 8
    lk.set_cards(cards[0:27])
    lk.onInit()
    lk.onDraw("测试中... 按Esc退出")
    lk.selectMode = True
    while lk.waitfor:
        CSI.flush()
    lk.onQuit()
