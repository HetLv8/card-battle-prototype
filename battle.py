# battle.py

from dataclasses import dataclass
from typing import List, Optional

# カードデータ構造
@dataclass
class Card:
    spec_id: str
    name: str
    card_type: str  # "attack", "defense" など
    cost: int
    power: int
    tags: List[str] = None


# ここが簡易版 make_card
def make_card(spec_id: str) -> Card:
    """
    カードIDを受け取り、最低限のCardインスタンスを返す。
    data.py がなくても動くフォールバック仕様。
    """
    # IDに応じて仮データを返す（あとでdata.py連携する）
    presets = {
        "ASHIGARU_STRIKE": {"name": "足軽：打ち込み", "type": "attack", "cost": 1, "power": 7},
        "SAMURAI_SHIELD": {"name": "侍：守勢", "type": "defense", "cost": 1, "power": 5},
    }
    base = presets.get(spec_id, {"name": spec_id, "type": "attack", "cost": 1, "power": 6})
    return Card(
        spec_id=spec_id,
        name=base["name"],
        card_type=base["type"],
        cost=base["cost"],
        power=base["power"],
        tags=[]
    )


class BattleManager:
    """
    戦闘状態と進行管理。
    - ターン開始/終了
    - カード解決（最小セット）
    - 敵の簡易行動
    - 時限バフ（ターンで減衰→0で削除）
    """

    def __init__(self, player, enemy, pdeck, edeck, *, max_energy: int = 3, hand_size: int = 5):
        self.player = player
        self.enemy = enemy
        self.pdeck = pdeck
        self.edeck = edeck
        self.turn = 1
        self.max_energy = max_energy
        self.hand_size = hand_size
        self.temp_buffs = {"player": {}, "enemy": {}}
        self.logger = print
        setattr(self.player, "battle", self)
        setattr(self.enemy, "battle", self)
    def _akey(self, actor):
            return "player" if actor is self.player else "enemy"
        
        
    # ========= 戦闘/ターン進行 =========

    def start_battle(self) -> int:
        self.logger(f"=== ⚔️  戦闘開始: {self.player.name} vs {self.enemy.name} ===")
        self.player.block = 0
        self.enemy.block = 0
        self.player.energy = self.max_energy
        self._draw_player_to(self.hand_size)
        self._draw_enemy_to(self.hand_size)
        return self.turn
    
    def start_turn(self):
        self.logger(f"\n=== 🧭 ターン {self.turn} 開始 ===")
        # ブロック持ち越し無し
        self.player.block = 0
        self.enemy.block = 0
        # エナジー補充
        self.player.energy = self.max_energy
        # 時限バフ減衰/削除
        self._decrement_temp_buffs()
        # ドローして手札を規定枚数へ
        self._draw_player_to(self.hand_size)

    def end_turn(self):
        self.logger(f"=== 🔚 ターン {self.turn} 終了 ===")
        self.turn += 1

    # ========= プレイヤーのカードプレイ =========

    def play_player_card(self, idx: int) -> str:
        if idx < 0 or idx >= len(self.pdeck.hand):
            return "⚠ 無効な番号です。"
        card = self.pdeck.hand[idx]
        # コスト
        cost = self._effective_cost(self.player, card)
        if self.player.energy < cost:
            return f"⚠ エナジー不足（必要:{cost}, 残り:{self.player.energy}）"
        # 支払い＆取り出し
        self.player.energy -= cost
        card = self.pdeck.hand.pop(idx)
        # 効果解決
        log = self._resolve_card_effect(card, user=self.player, target=self.enemy)
        # 捨て札へ
        self._discard(self.pdeck, card)
        return log

    # ========= 敵行動（要全面工事） =========

    def enemy_act(self) -> str:
        # 手札補充（簡易）
        self._draw_enemy_to(self.hand_size)
        # 攻撃優先→防御
        attack_idx = self._find_first_by_type(self.edeck.hand, "attack")
        defense_idx = self._find_first_by_type(self.edeck.hand, "defense")
        if attack_idx is None and defense_idx is None:
            return f"…{self.enemy.name} は様子をうかがっている"
        idx = attack_idx if attack_idx is not None else defense_idx
        card = self.edeck.hand.pop(idx)
        log = self._resolve_card_effect(card, user=self.enemy, target=self.player)
        self._discard(self.edeck, card)
        return f"▶ 敵行動：{log}"

    # ========= 勝敗判定 =========

    def is_battle_over(self):
        if self.player.hp <= 0 and self.enemy.hp <= 0:
            return True, "相打ちだ…"
        if self.player.hp <= 0:
            return True, "敗北…"
        if self.enemy.hp <= 0:
            return True, "勝利！"
        return False, ""

    # ========= 効果解決（要全面工事） =========

    def _resolve_card_effect(self, card, *, user, target) -> str:
        ctype = getattr(card, "card_type", None) or getattr(card, "type", None)
        power = getattr(card, "power", 0)
        name = getattr(card, "spec_id", getattr(card, "name", "???"))
        tags = getattr(card, "tags", []) or []

        # 例：戦術カード：足軽大将（号令） → このターン足軽パワー+X
        if name in ("TC_ASHIGARU_COMMANDER", "足軽大将：号令"):
            bonus = power if power else 2
            self.add_temp_buff(user, "ashigaru_power_bonus", bonus, duration=1)
            return f"{user.name} は『{name}』で足軽を鼓舞（このターン+{bonus})！"
        
        if name in ("TC_DEF_FORMATION", "戦術：防陣"):
            bonus = power if power else 3
            self.add_temp_buff(user, "defense_up_this_turn", bonus, duration=1)
            return f"{user.name} は『{name}』を展開（このターン 防御+{bonus})！"
        
        if ctype == "attack":
            # 足軽タグなら号令ボーナスを乗せる
            atk_bonus = 0
            if "足軽" in tags:
                atk_bonus = self.get_temp_buff_value(user, "ashigaru_power_bonus")
            dmg = power + atk_bonus
            dealt = target.take_damage(dmg)
            return f"{user.name} の『{name}』→ {target.name} に {dealt} ダメージ（+{atk_bonus}）"

        if ctype == "defense":
            def_bonus = self.get_temp_buff_value(user, "defense_up_this_turn")
            gain = power + def_bonus
            user.block += gain
            return f"{user.name} の『{name}』→ ブロック {gain} 獲得（+{def_bonus}）"

        if ctype == "skill":
            return f"{user.name} は『{name}』を使用した。"

        return f"{user.name} は『{name}』を使った（未定義）"

# ========= 時限バフ =========

def add_temp_buff(self, actor, name: str, value: int, duration: int = 1):
    k = self._akey(actor)
    buffs = self.temp_buffs.setdefault(k, {})
    buffs[name] = {"value": value, "duration": duration}
    self.logger(f"🟢 {actor.name} に {name}+{value}（{duration}T）")

def get_temp_buff_value(self, actor, name: str) -> int:
    k = self._akey(actor)
    buffs = self.temp_buffs.get(k, {})
    return buffs.get(name, {}).get("value", 0)

def _decrement_temp_buffs(self):
    for k, buffs in self.temp_buffs.items():
        expired = []
        for name, info in buffs.items():
            info["duration"] -= 1
            if info["duration"] <= 0:
                expired.append(name)
        for name in expired:
            # k は "player"/"enemy"（表示用に対象名を出したいなら map してもOK）
            who = self.player.name if k == "player" else self.enemy.name
            self.logger(f"⚪️ {who} の {name} が切れた")
            del buffs[name]


    # ========= ユーティリティ =========

    def _draw_player_to(self, n: int):
        need = max(0, n - len(self.pdeck.hand))
        if need > 0:
            self._draw(self.pdeck, need)

    def _draw_enemy_to(self, n: int):
        need = max(0, n - len(self.edeck.hand))
        if need > 0:
            self._draw(self.edeck, need)

    def _draw(self, deck, n: int):
        if hasattr(deck, "draw"):
            deck.draw(n)
        elif hasattr(deck, "draw_cards"):
            deck.draw_cards(n)
        else:
            for _ in range(n):
                if getattr(deck, "draw_pile", []):
                    deck.hand.append(deck.draw_pile.pop(0))

    def _discard(self, deck, card):
        if hasattr(deck, "discard"):
            deck.discard(card)
        elif hasattr(deck, "discard_pile"):
            deck.discard_pile.append(card)

    def _effective_cost(self, actor, card) -> int:
        base = getattr(card, "cost", 0)
        # 例：将来、足軽カードのコスト-1等をここで適用
        return base

    @staticmethod
    def _find_first_by_type(hand: list, ctype: str) -> Optional[int]:
        for i, c in enumerate(hand):
            if getattr(c, "card_type", None) == ctype:
                return i
        return None
