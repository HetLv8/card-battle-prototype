# battle.py
from typing import Optional
from battle_deck import BattleDeck
from model import CardInstance

class BattleManager:
    """
    戦闘進行管理（v1.10最小版）
    - BattleDeckと連動（draw/discardを直接使用）
    - 特殊効果は S1 / S2 / H2 のみ内蔵
    - それ以外は card_type によるデフォルト挙動
    """

    def __init__(self, player, enemy, pdeck: BattleDeck, edeck: BattleDeck,
                 *, max_energy: int = 3, hand_size: int = 5):
        self.player = player
        self.enemy = enemy
        self.pdeck = pdeck
        self.edeck = edeck
        self.turn = 1
        self.max_energy = max_energy
        self.hand_size = hand_size
        self.temp_buffs = {"player": {}, "enemy": {}}  # { name: {value, duration} }
        self.logger = print
        setattr(self.player, "battle", self)
        setattr(self.enemy, "battle", self)

    # ---- internal helpers ----
    def _akey(self, actor): return "player" if actor is self.player else "enemy"
    def _peer(self, actor): return self.enemy if actor is self.player else self.player

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
        # v1.10：ブロック持ち越しなし・エナジー補充
        self.player.block = 0
        self.enemy.block = 0
        self.player.energy = self.max_energy
        # バフ減衰
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
        # 支払い＆取り出し
        self.player.energy -= cost
        card = self.pdeck.hand.pop(idx)
        # 効果解決
        log = self._resolve_card_effect(card, user=self.player, target=self.enemy)
        # 捨て札へ
        self._discard(self.pdeck, card)
        return log

    # ========= 敵行動（簡易AI：攻撃優先→防御） =========
    def enemy_act(self) -> str:
        self._draw_enemy_to(self.hand_size)
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
        if self.player.hp <= 0 and self.enemy.hp <= 0: return True, "相打ちだ…"
        if self.player.hp <= 0: return True, "敗北…"
        if self.enemy.hp <= 0: return True, "勝利！"
        return False, ""

    # ========= 効果解決（S1/S2/H2のみ内蔵） =========
    def _resolve_card_effect(self, card: CardInstance, *, user, target) -> str:
        """
        v1.10：card_effects なし。
        - S1: 基本防御（バフ考慮）
        - S2: 反撃突き（Blockの20%を追加・消費なし）
        - H2: 逆襲の構え（Blockの半分を消費して追加）
        - それ以外：card_type によるデフォルト挙動
        """
        cid   = getattr(card, "spec_id", "?")
        ctype = getattr(card, "card_type", "")
        power = getattr(card, "power", 0)

        # --- 特殊効果 ---
        if cid == "S1":
            gain = power + self.get_temp_buff_value(user, "defense_plus_this_turn")
            user.block += gain
            return f"{user.name} は防御（Block +{gain}）"

        if cid == "S2":
            extra = int(user.block * 0.20)
            dmg = power + extra
            dealt = target.take_damage(dmg)
            return f"{user.name} の反撃突き → {target.name} に {dealt} ダメージ（+{extra}）"

        if cid == "H2":
            extra = user.block // 2
            if extra > 0:
                user.block -= extra
            dmg = power + extra
            dealt = target.take_damage(dmg)
            return f"{user.name} の逆襲の構え → {target.name} に {dealt} ダメージ（消費:{extra}）"

        # --- デフォルト挙動 ---
        if ctype == "attack":
            dealt = target.take_damage(power)
            return f"{user.name} の攻撃 → {target.name} に {dealt} ダメージ"

        if ctype == "defense":
            gain = power + self.get_temp_buff_value(user, "defense_plus_this_turn")
            user.block += gain
            return f"{user.name} は防御（Block +{gain}）"

        if ctype == "skill":
            return f"{user.name} はスキルを使用した。"

        return f"{user.name} はカードを使用した。"

    # ========= 一時バフ =========
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

    def _effective_cost(self, actor, card: CardInstance) -> int:
        base = getattr(card, "cost", 0)
        # v1.10：コスト補正なし（H4などは未実装）
        return max(0, base)

    @staticmethod
    def _find_first_by_type(hand: list, ctype: str) -> Optional[int]:
        for i, c in enumerate(hand):
            if getattr(c, "card_type", None) == ctype:
                return i
        return None
