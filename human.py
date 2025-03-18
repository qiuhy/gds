import game
from puke import Puke
import out


class human(game.Player):
    def play(self, desk_outs, level):
        cards = []
        strCard=""
        for c in self.cards:
            strCard += " " +str(Puke[c])
        strs = input(f"{self.name}(你):{strCard}\n出牌:").split()

    def back(self, card):
        return super().back(card)
