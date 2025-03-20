from enum import Enum


class Game_Event_Cate(Enum):
    GE_Ready = "就绪"  # [playersname] * 4
    GE_Deal = "发牌"   # [Puke] * 27
    GE_Give = "贡牌"   # (giver, Puke)
    GE_Back = "还牌"   # (giver, Puke, backer, Puke)
    GE_Anti = "抗供"   # [Antier]
    GE_Start = "开始"  # (first, level)
    GE_Play = "出牌"   # outCard
    GE_Over = "结束"   # winner[]
    GE_End = "游戏结束"
