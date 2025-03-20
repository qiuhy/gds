import sys
import os
sys.path.append(os.getcwd())
import keyboard
from player import Player
from event import Game_Event_Cate
#define CSI "\e["
#define vcon_end() printf(CSI "?1049l")                   // 恢复终端 ?10947l
#define vcon_beg() printf(CSI "?1049h")                   // 使用备用缓冲区 ?10947h
#define vcon_hide_cursor() printf(CSI "?25l")             // hide cursor
#define vcon_move_cursor(x, y) printf(CSI "%d;%dH", y, x) // move cursor
#define vcon_clear_text() printf(CSI "2J");               // clear
#define vcon_reset_text() printf(CSI "0m")                // reset text color
#define vcon_set_text(x) printf(CSI "%dm", x)

class Looker(Player):
    def __init__(self, name=""):
        super().__init__(name)

    def give(self):
        return super().give()
    
    def back(self, c):
        return super().back(c)
    
    def play(self, desk_outs):
        return super().play(desk_outs)
    
    def onEvent(self, e, info):
        # GE_Ready = "就绪"  # [playersname] * 4
        # GE_Deal = "发牌"   # level
        # GE_Give = "贡牌"   # (giver, Puke)
        # GE_Back = "还牌"   # (giver, Puke, backer, Puke)
        # GE_Anti = "抗供"   # [Antier]
        # GE_Start = "开始"  # firster
        # GE_Play = "出牌"   # outCard
        # GE_Over = "结束"   # winner[]
        # GE_End = "游戏结束"
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

        return super().onEvent(e, info)
    
    def init(self):

        try:
            width,height = os.get_terminal_size()
        except OSError:
            width = -1
            height = -1

        sys.stdout.write("\033[?1047h")
        sys.stdout.write("\033[?25l")
        sys.stdout.write("\033[2J")
        sys.stdout.write(f"\033[{10};{10}H")
        sys.stdout.write("\033[31;47m")
        print(f"屏幕尺寸{width}*{height}")
        sys.stdout.write("\033[0m")
        sys.stdout.write(f"\033[{0};{0}H")
        keyboard.wait("enter")
        keyboard.get_hotkey_name()
        sys.stdout.write("\033[?1047l")

    def afterReady(info)    :
        pass

    def afterDeal(info):
        pass
    def afterAnti(info):
        pass
    def afterGive(info):
        pass
    def afterBack(info):
        pass
    def afterStart(info):
        pass
    def afterPlay(info):
        pass
    def afterOver(info):
        pass

if __name__ == "__main__":    
    lk = Looker()
    lk.init()    
