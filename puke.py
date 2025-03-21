# hy_qiu 扑克牌基础类
# 花色和牌点
#
Cate_str = "♦♣♥♠gG"  # "♦♣♥♠🃟🃏"
Num_str = "234567890JQKAgG"
Val_str = "🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂡🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂱🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃑🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃁🃟🃏"


class Card:
    @staticmethod
    def get_val_num(v):
        if v >=54:
            v = v % 54
        if v < 52:
            return v // 4
        elif v == 52:
            return 13
        else:
            return 14
    
    @staticmethod
    def get_val_cate(v):
        if v >=54:
            v = v % 54
        if v < 52:
            return v % 4
        elif v == 52:
            return 4
        else:
            return 5
    
    @staticmethod
    def get_num_str(num):
        return Num_str[num]

    @staticmethod
    def get_cate_str(cate):
        return Cate_str[cate]

    @staticmethod
    def get_redVal(num):
        return num * 4 + 2

    @staticmethod
    def getCardVal(cardstr):
        cate = Cate_str.find(cardstr[0])
        num = Num_str.find(cardstr[1])
        if num > 12:
            return num + 39
        return cate + num * 4

    def __init__(self, v):
        self.cate = Card.get_val_cate(v)
        self.num = Card.get_val_num(v)
        self.val = v

    def val_str(self):
        if self.num > 12:
            return Val_str[39 + self.num]
        else:
            return Val_str[self.cate * 13 + self.num]

    def num_str(self):
        return Num_str[self.num]

    def cate_str(self):
        return Cate_str[self.cate]

    def __str__(self):
        return self.cate_str() + self.num_str()

    def __eq__(self, p):
        # return self.num == p.num
        return self.val == p.val

    def __lt__(self, p):
        # return self.num < p.num
        return self.val < p.val

    def __le__(self, p):
        # return self < p or self == p
        return self.val <= p.val

    def __gt__(self, p):
        # return not (self <= p)
        return self.val > p.val

    def __ge__(self, p):
        # return self > p or self == p
        return self.val >= p.val


Puke = [Card(i) for i in range(54)]  # 所有牌
