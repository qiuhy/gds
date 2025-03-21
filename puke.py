# hy_qiu 扑克牌基础类
# 花色和牌点
#
Cate_str = "♦♣♥♠gG"#"♦♣♥♠🃟🃏"
Num_str = "234567890JQKAgG"
Val_str = "🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂡🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂱🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃑🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃁🃟🃏"


class Card:
    @staticmethod
    def get_num_str(num):
        return Num_str[num]

    @staticmethod
    def get_cate_str(idx):
        idx = idx % 54
        if idx < 52:            
            return Cate_str[idx % 4]
        elif idx == 52:            
            return Cate_str[4]
        else:
            return Cate_str[5]
        

    @staticmethod
    def getCardVal(cardstr):
        cate = Cate_str.find(cardstr[0])
        num = Num_str.find(cardstr[1])
        if num > 12:
            return num + 39
        return cate + num * 4

    def __init__(self, v):
        v = v % 54
        if v < 52:
            self.cate = v % 4
            self.num = v // 4
        elif v == 52:
            self.cate = 4
            self.num = 13
        else:
            self.cate = 5
            self.num = 14
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
