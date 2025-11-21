# main.py

from model import Player, Enemy
from battle import BattleManager
from battle_deck import BattleDeck
from master_deck import MasterDeck
from starter_decks import make_starter_deck


def show_state(bm: BattleManager) -> None:
    p, e = bm.player, bm.enemy
    print(f"\n=== 🧭 ターン {bm.turn} ===")
    print(f"👤 {p.name} HP {p.hp}/{p.max_hp} | Block {p.block} | Energy {p.energy}")
    print(f"💀 {e.name} HP {e.hp}/{e.max_hp} | Block {e.block}")


def show_hand(deck: BattleDeck) -> None:
    for i, c in enumerate(deck.hand):
        print(f"{i}: {c.spec_id} ({c.card_type}) cost={c.cost} pow={c.power}")


def main() -> None:
    # --- プレイヤー／敵 ---
    player = Player(name="織田信長", max_hp=60)
    enemy = Enemy(name="明智光秀", max_hp=50)

    # --- デッキ準備 ---
    mdeck = MasterDeck()
    # とりあえず HIDEYOSHI スターターを流用（中身は適宜 S1〜S32 に差し替えてOK）
    starter_ids = make_starter_deck("HIDEYOSHI")

    pdeck = BattleDeck(starter_ids)
    edeck = BattleDeck(starter_ids)  # テスト用に同じデッキを敵にも

    bm = BattleManager(player, enemy, pdeck, edeck, max_energy=3, hand_size=5)
    bm.start_battle()

    # --- メインループ ---
    while True:
        # プレイヤーターン
        bm.start_turn()
        show_state(bm)
        show_hand(bm.pdeck)

        while True:
            cmd = input("番号でカードを選択 / end でターン終了 > ").strip()
            if cmd == "end":
                break
            try:
                idx = int(cmd)
                log = bm.play_player_card(idx)
                print(log)
                show_state(bm)
                over, msg = bm.is_battle_over()
                if over:
                    print(msg)
                    return
            except ValueError:
                print("⚠ 入力エラー（番号 or end）")

        bm.end_turn()

        # 敵ターン
        log = bm.enemy_act()
        print(log)
        show_state(bm)
        over, msg = bm.is_battle_over()
        if over:
            print(msg)
            return


if __name__ == "__main__":
    main()
