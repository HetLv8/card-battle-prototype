#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal CLI Card Battle Prototype for VSCode
-------------------------------------------------
🧩 Version: 0.1
🎯 Goal: 基本的なターン制カード戦闘の実装
💻 Run in Terminal:  main.py
"""

from dataclasses import dataclass
from typing import List, Optional
import random
import sys

# ----------------------
# Card Class
# ----------------------
@dataclass
class Card:
    name: str
    cost: int
    power: int
    card_type: str  # 'attack' or 'block'

    def play(self, caster: "Actor", target: "Actor", battle: "BattleManager") -> str:
        """カードの効果を適用"""
        if caster.energy < self.cost:
            return f"⚠ エナジー不足: {self.name} は使用できません (必要{self.cost}, 残り{caster.energy})"

        caster.energy -= self.cost
        log = f"▶ {caster.name} が {self.name} を使用 (コスト:{self.cost})"

        if self.card_type == "attack":
            dmg = self.power
            dealt = target.take_damage(dmg)
            log += f" → {target.name} に {dealt} ダメージ"
        elif self.card_type == "block":
            caster.block += self.power
            log += f" → {caster.name} は {self.power} ブロックを獲得 (合計 {caster.block})"
        else:
            log += " → (効果未定義)"
        return log


# ----------------------
# Actor Base Class
# ----------------------
class Actor:
    def __init__(self, name: str, max_hp: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.energy = 0

    def reset_turn(self, energy: int):
        self.block = 0
        self.energy = energy

    def take_damage(self, amount: int) -> int:
        """ブロック考慮付きのダメージ計算"""
        blocked = min(self.block, amount)
        self.block -= blocked
        actual = max(0, amount - blocked)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_dead(self) -> bool:
        return self.hp <= 0


# ----------------------
# Player / Enemy
# ----------------------
class Player(Actor):
    def __init__(self, name: str, max_hp: int, deck: List[Card]):
        super().__init__(name, max_hp)
        self.draw_pile = deck[:]
        self.discard_pile: List[Card] = []
        self.hand: List[Card] = []
        random.shuffle(self.draw_pile)

    def draw(self, n: int):
        for _ in range(n):
            if not self.draw_pile:
                self.draw_pile = self.discard_pile[:]
                self.discard_pile.clear()
                random.shuffle(self.draw_pile)
            if self.draw_pile:
                self.hand.append(self.draw_pile.pop())

    def discard_all(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()


class Enemy(Actor):
    def __init__(self, name: str, max_hp: int):
        super().__init__(name, max_hp)
        self.turn_index = 0

    def intent(self) -> str:
        return "攻撃 8" if self.turn_index % 2 == 0 else "防御 6"

    def act(self, target: Actor) -> str:
        self.reset_turn(0)
        if self.turn_index % 2 == 0:
            dmg = 8
            dealt = target.take_damage(dmg)
            log = f"▶ {self.name} の攻撃 → {target.name} に {dealt} ダメージ"
        else:
            self.block += 6
            log = f"▶ {self.name} は防御 6 を獲得 (合計 {self.block})"
        self.turn_index += 1
        return log


# ----------------------
# Battle Manager
# ----------------------
class BattleManager:
    def __init__(self, player: Player, enemy: Enemy, draw_per_turn: int = 5, energy_per_turn: int = 3):
        self.player = player
        self.enemy = enemy
        self.turn = 1
        self.draw_per_turn = draw_per_turn
        self.energy_per_turn = energy_per_turn

    def log_state(self):
        print("\n" + "="*45)
        print(f"🧭 ターン {self.turn}")
        print(f"👤 {self.player.name}: HP {self.player.hp}/{self.player.max_hp} | Block {self.player.block} | Energy {self.player.energy}")
        print(f"💀 {self.enemy.name}: HP {self.enemy.hp}/{self.enemy.max_hp} | Block {self.enemy.block} | Intent [{self.enemy.intent()}]")
        print("-"*45)
        for i, c in enumerate(self.player.hand):
            print(f"[{i}] {c.name} (タイプ:{c.card_type}, コスト:{c.cost}, 値:{c.power})")
        print("-"*45)

    def start_player_turn(self):
        self.player.reset_turn(self.energy_per_turn)
        self.player.draw(self.draw_per_turn)

    def end_player_turn(self):
        self.player.discard_all()

    def check_end(self) -> Optional[str]:
        if self.enemy.is_dead():
            return "win"
        if self.player.is_dead():
            return "lose"
        return None

    def play_card(self, idx: int):
        if idx < 0 or idx >= len(self.player.hand):
            print("⚠ 無効な番号です。")
            return
        card = self.player.hand.pop(idx)
        print(card.play(self.player, self.enemy, self))
        self.player.discard_pile.append(card)

    def run(self):
        print("=== カードバトル・プロトタイプ ===")
        while True:
            self.start_player_turn()
            while True:
                self.log_state()
                cmd = input("コマンド (番号=カード使用, e=エンド, q=終了): ").strip().lower()
                if cmd == "q":
                    print("終了します。")
                    sys.exit(0)
                if cmd == "e":
                    break
                if cmd.isdigit():
                    self.play_card(int(cmd))
                    if self.check_end():
                        break
                else:
                    print("⚠ 入力を認識できません。")
                if self.check_end():
                    break

            result = self.check_end()
            if result == "win":
                print("\n🎉 勝利！")
                return
            if result == "lose":
                print("\n💥 敗北…")
                return

            print("\n--- 敵ターン ---")
            print(self.enemy.act(self.player))

            result = self.check_end()
            if result == "win":
                print("\n🎉 勝利！")
                return
            if result == "lose":
                print("\n💥 敗北…")
                return
            self.turn += 1


# ----------------------
# Deck Factory
# ----------------------
def starter_deck() -> List[Card]:
    deck = []
    for _ in range(5):
        deck.append(Card("ストライク", 1, 6, "attack"))
    for _ in range(5):
        deck.append(Card("ディフェンド", 1, 5, "block"))
    return deck


# ----------------------
# Main
# ----------------------
def main():
    player = Player("プレイヤー", 50, starter_deck())
    enemy = Enemy("スライム", 40)
    battle = BattleManager(player, enemy)
    battle.run()


if __name__ == "__main__":
    main()
