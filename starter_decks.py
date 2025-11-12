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
            ["H2"] +
            ["S1"] * 3 +
            ["S2"] * 2    
        )
        return [make_card(i) for i in ids]
    raise ValueError(f"unknown faction: {f}")
