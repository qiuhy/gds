import player
from puke import Puke
import out


class human(player.Player):
    def play(self, desk_outs):
        cards = []
        strCard=""
        for c in self.cards:
            strCard += " " +Puke[c]
        strs = input(f"{self.name}(你):{strCard}\n出牌:").split()

    def give(self):
        return super().give()
    
    def back(self, card):
        return super().back(card)
