# main.py
import random
from model import Player, Enemy
from deck import DeckState
from battle import BattleManager
from battle import make_card  # 既存のカード生成ファクトリ想定
from starter_decks import make_starter_deck

def make_starter_deck_local():
    return make_starter_deck("HIDEYOSHI")

def make_enemy_deck():
    # v1.10：攻撃/防御を適当に
    return [make_card("ASHIGARU_STRIKE") for _ in range(6)] + \
           [make_card("SAMURAI_SHIELD") for _ in range(4)]

def show_state(bm: BattleManager):
    p, e = bm.player, bm.enemy
    print(f"\n=== 🧭 ターン {bm.turn} ===")
    print(f"👤 {p.name} HP {p.hp}/{p.max_hp} | Block {p.block} | Energy {p.energy}")
    print(f"💀 {e.name} HP {e.hp}/{e.max_hp} | Block {e.block}")

def show_hand(deck: DeckState):
    for i, c in enumerate(deck.hand):
        name = getattr(c, "spec_id", getattr(c, "name", "?"))
        print(f"[{i}] {name} (type:{c.card_type}, cost:{c.cost}, val:{c.power})")

def main():
    random.seed(42)  # 再現性
    player = Player("織田隊", max_hp=40)
    enemy = Enemy("明智兵", max_hp=35)
    pdeck = DeckState(make_starter_deck())
    edeck = DeckState(make_enemy_deck())

    bm = BattleManager(player, enemy, pdeck, edeck, max_energy=3, hand_size=5)
    bm.start_battle()

    while True:
        show_state(bm)
        bm.start_turn()

        # === プレイヤーターン（手動endのみ） ===
        while True:
            show_hand(pdeck)
            cmd = input("番号を入力（endで終了）：").strip().lower()
            if cmd in ("end", "e"):
                break
            try:
                idx = int(cmd)
                log = bm.play_player_card(idx)  # エナジー不足等はここで判定
                print(log)
            except ValueError:
                print("⚠ 入力エラー（番号 or end）")

        bm.end_turn()

        # === 敵ターン（簡易AI） ===
        print(bm.enemy_act())

        over, msg = bm.is_battle_over()
        if over:
            print(msg)
            break
        
if __name__ == "__main__":
    main()
