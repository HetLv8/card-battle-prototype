#model.py
#Dataclass
#Actor/Player/Enemy/CardInstance

from dataclasses import dataclass, field
from typing import List, Literal

@dataclass
class Actor:
    def __init__(self, name: str, max_hp: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.buffs: List[Buff] = []

    energy: int = 3

    def __post_init__(self):
        if self.hp is None:
            self.hp = self.max_hp

    # v1.10 は簡単のため、被ダメ計算はここに残してOK
    def take_damage(self, dmg: int) -> int:
        absorb = min(self.block, dmg)
        self.block -= absorb
        dealt = dmg - absorb
        self.hp = max(0, self.hp - dealt)
        return dealt

    def reset_turn(self, energy_cap: int = 3):
        self.block = 0            # v1.10はブロック持ち越し無しにするならここで0
        self.energy = energy_cap

@dataclass
class Player(Actor):
    pass

@dataclass
class Enemy(Actor):
    # 旧コードの turn_index / intent() は battle 側で扱う予定なら外してOK
    turn_index: int = 0

@dataclass
class CardInstance:
    spec_id: str                       # "ASHIGARU_STRIKE" など
    cost: int
    power: int
    card_type: str                     # "attack" / "block"
    tags: List[str] = field(default_factory=list)

    def play_text(self) -> str:
        return f"{self.card_type}:{self.power}"


BuffTrigger = Literal["turn_start", "turn_end", "on_card_play", "on_attack_calc", "on_hit"]


@dataclass
class Buff:
    """
    すべてのバフ/デバフ/陣形を一元管理するためのモデル。
    - kind   : バフID（"WEAK" / "COUNTER" / "FORM_SHIELDWALL" など）
    - power  : 効果の強さ（Block量・反撃量・弱体段数など）
    - turns  : 残りターン数（0以下になったら消滅）
    - trigger: どのタイミングで評価するか
    """
    kind: str
    power: int
    turns: int
    trigger: BuffTrigger
