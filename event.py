from enum import Enum
import json


class Game_Event(Enum):
    GE_Name = "报名"  # name
    GE_Join = "加入"  # sit
    GE_Ready = "就绪"  # [playersname] * 4
    GE_Dealing = "发牌"  # cards: int[27] retrun OK
    GE_Deal = "发牌结束"  # curTeam.name
    GE_Giveing = "贡牌"  # return GE_Giveing (giver, Puke)
    GE_Give = "贡牌结束"  # (giver, Puke)
    GE_Backing = "还牌"  # return GE_Backing (backer, Puke)
    GE_Back = "还牌结束"  # (giver, Puke, backer, Puke)
    GE_Anti = "抗供"  # [Antier]
    GE_Start = "开始"  # firster
    GE_Wind = "接风"  # winder
    GE_Playing = "出牌"  # last_outValues return GE_Playing outValues
    GE_Play = "出牌结束"  # (outer,cards ,restCards)
    GE_Over = "结束"  # winner[]
    GE_Quit = "退出"  # quiter
    GE_End = "游戏结束"  # winner[] 2
    GE_Error = "错误"  # reason
    GE_OK = "成功"  #


class Messgae:
    def __init__(self, e: Game_Event, info=None):
        self.e = e
        self.info = info
        pass

    def toJson(self):
        return json.dumps({"e": self.e.name, "i": self.info})

    @staticmethod
    def fromJson(msgStr):
        obj = json.loads(msgStr)
        if not isinstance(obj, dict):
            return
        if obj.get("e") is None:
            return
        if not "i" in obj.keys():
            return

        for e in Game_Event:
            if e.name == obj["e"]:
                break
        else:
            return

        return Messgae(e, obj["i"])

    @staticmethod
    def OK(info=None):
        return Messgae(Game_Event.GE_OK, info)

    @staticmethod
    def Error(info):
        return Messgae(Game_Event.GE_Error, info)

    def __str__(self):
        if self.info:
            return f"{self.e.name}:{self.info }"
        else:
            return f"{self.e.name}"
