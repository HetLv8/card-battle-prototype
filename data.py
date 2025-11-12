# data.py
from typing import Dict

CARD_SPECS: Dict[str, dict] = {
    # --- 槍兵科（Spear） ---
    "S1": {
        "name": "槍足軽：防御",
        "card_type": "defense",
        "cost": 1, "power": 6,
        "tags": ["ashigaru", "spear"],
        "desc": "ブロック6を獲得する。"
    },
    "S2": {
        "name": "槍足軽：反撃突き",
        "card_type": "attack",
        "cost": 1, "power": 5,
        "tags": ["ashigaru", "spear", "counter"],
        "desc": "ブロックの20%を追加ダメージに変換。"
    },
    "S3": {
        "name": "槍足軽：防御姿勢",
        "card_type": "defense",
        "cost": 1, "power": 8,
        "tags": ["ashigaru", "spear", "retain_block"],
        "desc": "ブロック8。次ターン開始時、ブロック半分を保持。"
    },
    "S4": {
        "name": "足軽：打ち払い",
        "card_type": "attack",
        "cost": 1, "power": 4,
        "tags": ["ashigaru", "spear", "debuff"],
        "desc": "4ダメージ。敵の攻撃力を1下げる（1T）。"
    },

    # --- 固有（羽柴家） ---
    "H1": {
        "name": "羽柴秀吉：不撓の采配",
        "card_type": "skill",
        "cost": 1, "power": 2,
        "tags": ["commander", "spear", "buff"],
        "desc": "このターン中、防御効果+2。次の防御カードの効果2倍。"
    },
    "H2": {
        "name": "前田利家：逆襲の構え",
        "card_type": "attack",
        "cost": 1, "power": 6,
        "tags": ["commander", "spear", "counter"],
        "desc": "ブロック半分を消費し、その値を追加ダメージに変換。"
    },
    "H3": {
        "name": "羽柴秀長：堅実なる防御",
        "card_type": "defense",
        "cost": 1, "power": 9,
        "tags": ["commander", "spear"],
        "desc": "ブロック9。次ターンの最初の攻撃ダメージ-25%。"
    },
    "H4": {
        "name": "黒田官兵衛：堅陣の策",
        "card_type": "skill",
        "cost": 1, "power": 0,
        "tags": ["commander", "spear", "support"],
        "desc": "次の2枚の防御カードのコスト-1。"
    },
}
