# battle_deck.py
import random
from typing import List
from model import CardInstance

class BattleDeck:
    """戦闘用デッキ：山札・手札・捨て札を管理。"""
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

    def discard(self, card: CardInstance):
        self.discard_pile.append(card)

    def add_card(self, card: CardInstance, where: str = "discard"):
        if where == "hand":
            self.hand.append(card)
        elif where == "top":
            self.draw_pile.insert(0, card)
        else:
            self.discard_pile.append(card)

    def discard_from_hand(self, idx: int):
        self.discard_pile.append(self.hand.pop(idx))

    def _reshuffle(self):
        if self.discard_pile:
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.draw_pile)
