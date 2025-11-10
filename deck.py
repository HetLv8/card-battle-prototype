# deck.py
import random
from typing import List
from model import CardInstance

class DeckState:
    def __init__(self, draw_pile: List[CardInstance]):
        self.draw_pile = list(draw_pile)
        self.hand: List[CardInstance] = []
        self.discard_pile: List[CardInstance] = []
        random.shuffle(self.draw_pile)

    def draw(self, n: int):
        for _ in range(n):
            if not self.draw_pile:
                self._reshuffle()
                if not self.draw_pile:
                    break
            self.hand.append(self.draw_pile.pop())

    def discard_from_hand(self, idx: int):
        self.discard_pile.append(self.hand.pop(idx))

    def discard_card(self, card: CardInstance):
        self.discard_pile.append(card)

    def _reshuffle(self):
        if self.discard_pile:
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.draw_pile)
