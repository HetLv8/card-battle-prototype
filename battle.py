# battle.py
from typing import Optional
import random

from battle_deck import BattleDeck
from model import CardInstance
from card_effects import (
    apply_card_effect,
    apply_buffs_on_turn_start,
    apply_buffs_on_card_play,
    tick_buffs,
)


class BattleManager:
    """
    戦闘進行管理（槍デッキ＋バフ一元管理版）

    ベース:
        - v1.10 の最小 BattleManager
        - BattleDeck と連動（draw/discard を直接使用）

    追加:
        - card_effects.apply_card_effect でカード効果を一元処理
        - card_effects 側のバフエンジンと連携:
            - apply_buffs_on_turn_start(...)
            - apply_buffs_on_card_play(...)
            - tick_buffs(...)
    """

    def __init__(
        self,
        player,
        enemy,
        pdeck: BattleDeck,
        edeck: BattleDeck,
        *,
        max_energy: int = 3,
        hand_size: int = 5,
    ):
        self.player = player
        self.enemy = enemy
        self.pdeck = pdeck
        self.edeck = edeck
        self.turn = 1
        self.max_energy = max_energy
        self.hand_size = hand_size

        # 旧システムの一時バフ（防御+2など）用
        # いまは主に防御号令などの互換性維持のため残している
        self.temp_buffs = {"player": {}, "enemy": {}}  # { name: {value, duration} }

        self.logger = print
        setattr(self.player, "battle", self)
        setattr(self.enemy, "battle", self)

    # ---- internal helpers ----
    def _akey(self, actor):
        return "player" if actor is self.player else "enemy"

    def _peer(self, actor):
        return self.enemy if actor is self.player else self.player

    # ========= 戦闘/ターン進行 =========
    def start_battle(self) -> int:
        self.logger(f"=== ⚔️  戦闘開始: {self.player.name} vs {self.enemy.name} ===")
        self.player.block = 0
        self.enemy.block = 0
        self.player.energy = self.max_energy
        # 初期手札
        self._draw_player_to(self.hand_size)
        self._draw_enemy_to(self.hand_size)
        return self.turn

    def start_turn(self):
        self.logger(f"\n=== 🧭 ターン {self.turn} 開始 ===")
        # v1.10：ブロック持ち越しなし・エナジー補充
        self.player.block = 0
        self.enemy.block = 0
        self.player.energy = self.max_energy

        # --- バフ処理（プレイヤー側のターン開始） ---
        # 陣形などの「turn_start トリガー」を評価し、そのあとプレイヤー側の残ターンを1減らす。
        apply_buffs_on_turn_start(self, self.player, self.enemy)
        tick_buffs(self.player)

        # 旧一時バフ（defense_plus_this_turn など）の減衰
        self._decrement_temp_buffs()

        # 手札補充
        self._draw_player_to(self.hand_size)

    def end_turn(self):
        self.logger(f"=== 🔚 ターン {self.turn} 終了 ===")
        self.turn += 1

    # ========= プレイヤー行動 =========
    def play_player_card(self, idx: int) -> str:
        if idx < 0 or idx >= len(self.pdeck.hand):
            return "⚠ 無効な番号です。"
        card: CardInstance = self.pdeck.hand[idx]
        cost = self._effective_cost(self.player, card)
        if self.player.energy < cost:
            return f"⚠ エナジー不足（必要:{cost}, 残り:{self.player.energy}）"

        # エナジー支払い＆手札から取り出し
        self.player.energy -= cost
        card = self.pdeck.hand.pop(idx)

        # カード使用時トリガーバフの適用
        apply_buffs_on_card_play(self, card, self.player, self.enemy)

        # 効果解決
        log = self._resolve_card_effect(card, user=self.player, target=self.enemy)

        # 捨て札へ
        self._discard(self.pdeck, card)
        return log

     # ========= 敵行動（簡易AI：攻撃優先→防御） =========
    def enemy_act(self) -> str:
        # 敵ターン開始時のバフ処理（敵側の陣形など）
        apply_buffs_on_turn_start(self, self.enemy, self.player)
        tick_buffs(self.enemy)
        e = self.enemy
        p = self.player
        # 3パターンからランダム選択
        action = random.choice(["attack", "multi_attack", "defense"])
        if action == "attack":
            dmg = 8
            dealt = p.take_damage(dmg)
            return f"▶ {e.name} の攻撃 → {p.name} に {dealt} ダメージ"
        elif action == "multi_attack":
            # 例：4ダメ×2回（ブロックに2回別々に当たる）
            dmg_each = 4
            total = 0
            for i in range(2):
                dealt = p.take_damage(dmg_each)
                total += dealt
            return f"▶ {e.name} の連続攻撃 → {p.name} に 合計 {total} ダメージ"
        else:  # "defense"
            gain = 6
            e.block += gain
            return f"▶ {e.name} は防御を固めた → Block+{gain}（合計 {e.block}）"

    # ========= 勝敗判定 =========
    def is_battle_over(self):
        if self.player.hp <= 0 and self.enemy.hp <= 0:
            return True, "相打ちだ…"
        if self.player.hp <= 0:
            return True, "敗北…"
        if self.enemy.hp <= 0:
            return True, "勝利！"
        return False, ""

    # ========= 効果解決 =========
    def _resolve_card_effect(self, card: CardInstance, *, user, target) -> str:
        # すべて card_effects 側に委譲
        return apply_card_effect(self, card, user, target)

    # ========= 一時バフ（旧仕様。防御号令などのため残置） =========
    def add_temp_buff(self, actor, name: str, value: int, duration: int = 1):
        k = self._akey(actor)
        buffs = self.temp_buffs.setdefault(k, {})
        buffs[name] = {"value": value, "duration": duration}
        self.logger(f"🟢 {actor.name} に {name}+{value}（{duration}T）")

    def get_temp_buff_value(self, actor, name: str) -> int:
        k = self._akey(actor)
        return self.temp_buffs.get(k, {}).get(name, {}).get("value", 0)

    def clear_temp_buff(self, actor, name: str):
        k = self._akey(actor)
        self.temp_buffs.get(k, {}).pop(name, None)

    def _decrement_temp_buffs(self):
        for k, buffs in self.temp_buffs.items():
            expired = []
            for name, info in list(buffs.items()):
                info["duration"] -= 1
                if info["duration"] <= 0:
                    expired.append(name)
            for name in expired:
                who = self.player.name if k == "player" else self.enemy.name
                self.logger(f"⚪️ {who} の {name} が切れた")
                del buffs[name]

    # ========= ユーティリティ（BattleDeck前提） =========
    def _draw_player_to(self, n: int):
        need = max(0, n - len(self.pdeck.hand))
        if need > 0:
            self._draw(self.pdeck, need)

    def _draw_enemy_to(self, n: int):
        need = max(0, n - len(self.edeck.hand))
        if need > 0:
            self._draw(self.edeck, need)

    @staticmethod
    def _draw(deck: BattleDeck, n: int):
        deck.draw(n)

    @staticmethod
    def _discard(deck: BattleDeck, card: CardInstance):
        deck.discard(card)

    def draw_cards(self, actor, n: int):
        """card_effects から呼ぶための共通ドロー関数。"""
        if actor is self.player:
            self._draw(self.pdeck, n)
        elif actor is self.enemy:
            self._draw(self.edeck, n)
    
    def _effective_cost(self, actor, card: CardInstance) -> int:
        base = getattr(card, "cost", 0)
        # v1.10：コスト補正なし（コスト軽減策などは今後バフで対応予定）
        return max(0, base)

    @staticmethod
    def _find_first_by_type(hand: list, ctype: str) -> Optional[int]:
        for i, c in enumerate(hand):
            if getattr(c, "card_type", None) == ctype:
                return i
        return None
