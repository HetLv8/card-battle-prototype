# main.py
import random
from model import Player, Enemy
from battle import BattleManager
from battle_deck import BattleDeck
from master_deck import MasterDeck
from starter_decks import make_starter_deck

def show_state(bm: BattleManager):
    p, e = bm.player, bm.enemy
    print(f"\n=== 🧭 ターン {bm.turn} ===")
    print(f"👤 {p.name} HP {p.hp}/{p.max_hp} | Block {p.block} | Energy {p.energy}")
    print(f"💀 {e.name} HP {e.hp}/{e.max_hp} | Block {e.block}")

def show_hand(deck: BattleDeck):
    for i, c in enumerate(deck.hand):
        name = getattr(c, "spec_id", getattr(c, "name", "?"))
        print(f"[{i}] {name} (type:{c.card_type}, cost:{c.cost}, val:{c.power})")

def main():
    random.seed(42)

    # === ゲーム開始：MasterDeck を作成 ===
    starter_cards = make_starter_deck("HIDEYOSHI")
    starter_ids = [c.spec_id for c in starter_cards]
    master = MasterDeck(starter_ids)

    # === 戦闘開始：MasterDeck → BattleDeck 実体化 ===
    player = Player("羽柴隊", max_hp=40)
    enemy = Enemy("明智兵", max_hp=35)
    pdeck = BattleDeck(master.instantiate())
    edeck = BattleDeck([])  # v1.10は敵は簡易AIで山札未使用でもOK

    bm = BattleManager(player, enemy, pdeck, edeck, max_energy=3, hand_size=5)
    bm.start_battle()
    show_state(bm)

    while True:
        bm.start_turn()
        show_state(bm)

        # === プレイヤーターン ===
        while True:
            show_hand(pdeck)
            cmd = input("番号（endで終了）：").strip().lower()
            if cmd in ("end", "e"):
                break
            try:
                idx = int(cmd)
                log = bm.play_player_card(idx)
                print(log)
                show_state(bm)
                over,msg = bm.is_battle_over()
                if over:
                    print(msg)
                    break
            except ValueError:
                print("⚠ 入力エラー（番号 or end）")
        bm.end_turn()

        # === 敵ターン ===
        print(bm.enemy_act())
        show_state(bm)
        over, msg = bm.is_battle_over()
        if over:
            print(msg)
            break

if __name__ == "__main__":
    main()