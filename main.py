# main.py
import random
from model import Player, Enemy
from deck import DeckState
from battle import (
    start_battle, start_turn, play_card, enemy_act, is_battle_over, make_card
)

def make_starter_deck():
    # 最小スターター
    return [make_card("ASHIGARU_STRIKE") for _ in range(5)] + \
           [make_card("SAMURAI_SHIELD") for _ in range(5)]

def make_enemy_deck():
    # v1.10：攻撃/防御を適当に
    return [make_card("ASHIGARU_STRIKE") for _ in range(6)] + \
           [make_card("SAMURAI_SHIELD") for _ in range(4)]

def main():
    random.seed(42)  # 再現性
    player = Player("織田隊", max_hp=40)
    enemy = Enemy("明智兵", max_hp=35)
    pdeck = DeckState(make_starter_deck())
    edeck = DeckState(make_enemy_deck())

    turn = start_battle(player, enemy, pdeck, edeck)

    while True:
        print(f"\n=== 🧭 ターン {turn} ===")
        print(f"👤 {player.name} HP {player.hp}/{player.max_hp} | Block {player.block} | Energy {player.energy}")
        print(f"💀 {enemy.name} HP {enemy.hp}/{enemy.max_hp} | Block {enemy.block}")

        start_turn(player, enemy, pdeck)
        # 手札表示
        for i, c in enumerate(pdeck.hand):
            print(f"[{i}] {c.spec_id} (type:{c.card_type}, cost:{c.cost}, val:{c.power})")

        # 入力（簡易CLI）
        cmd = input("番号 or end: ").strip()
        if cmd == "end" or player.energy <= 0:
            pass
        else:
            try:
                idx = int(cmd)
                print(play_card(idx, player, enemy, pdeck))
            except Exception:
                print("⚠ 入力エラー")

        # ターン終了処理（ブロック持ち越し無しにするならここで0化も可）
        # player.block = 0

        # 敵行動
        print(enemy_act(enemy, player, edeck))

        over, msg = is_battle_over(player, enemy)
        if over:
            print(msg)
            break

        turn += 1

if __name__ == "__main__":
    main()
