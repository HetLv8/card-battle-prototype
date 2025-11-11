# starter_decks.py
from typing import List
from model import CardInstance
from data import CARD_SPECS

def make_card(spec_id: str) -> CardInstance:
    spec = CARD_SPECS[spec_id]
    return CardInstance(
        spec_id=spec_id,
        cost=spec["cost"],
        power=spec["power"],
        card_type=spec["card_type"],
        tags=list(spec.get("tags", [])),
    )

def make_starter_deck(faction: str) -> List[CardInstance]:
    f = faction.upper()
    if f == "HIDEYOSHI":
        ids = (
            ["HIDEYOSHI_COMMAND"] * 1 +
            ["MAEDA_COUNTERSTANCE"] * 1 +
            ["HIDENAGA_WALL"] * 1 +
            ["KANBEI_FORTIFY"] * 1 +
            ["SPEAR_DEFENSE"] * 3 +
            ["SPEAR_COUNTER"] * 2 +
            ["SPEAR_GUARD_POSTURE"] * 1
        )
        return [make_card(i) for i in ids]
    raise ValueError(f"unknown faction: {f}")
