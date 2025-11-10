# data.py
from typing import Dict

# 最小2種だけ（ID主義。後でJSON化）
CARD_SPECS: Dict[str, dict] = {
    "ASHIGARU_STRIKE": {
        "name": "足軽斬り",
        "card_type": "attack",
        "cost": 1,
        "power": 6,
        "tags": ["spear"],
    },
    "SAMURAI_SHIELD": {
        "name": "侍の防御",
        "card_type": "block",
        "cost": 1,
        "power": 5,
        "tags": ["guard"],
    },
}
