# master_deck.py
from typing import List
from model import CardInstance
from data import CARD_SPECS

class MasterDeck:
    """恒久デッキ：報酬/強化/削除などの恒久変化を保持。"""
    def __init__(self, card_ids: List[str]):
        self.card_ids = list(card_ids)

    def add_card(self, spec_id: str):
        self.card_ids.append(spec_id)

    def remove_card(self, spec_id: str) -> bool:
        if spec_id in self.card_ids:
            self.card_ids.remove(spec_id)
            return True
        return False

    def instantiate(self) -> List[CardInstance]:
        """戦闘開始時に実体化して返す。"""
        out: List[CardInstance] = []
        for sid in self.card_ids:
            spec = CARD_SPECS[sid]
            out.append(CardInstance(
                spec_id=sid,
                cost=spec["cost"],
                power=spec["power"],
                card_type=spec["card_type"],
                tags=list(spec.get("tags", [])),
            ))
        return out
