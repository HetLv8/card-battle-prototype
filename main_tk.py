# main_tk.py
import tkinter as tk
from tkinter import ttk
import random

from model import Player, Enemy
from battle import BattleManager
from battle_deck import BattleDeck
from master_deck import MasterDeck
from starter_decks import make_starter_deck


class BattleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("プロトタイプUI")
        self.geometry("720x480")

        self.bm: BattleManager | None = None
        self.game_over = False
        self.hand_buttons = []
        self._create_widgets()
        self._setup_game()

    # ===== ウィジェット作成 =====
    def _create_widgets(self):
        # ステータス表示
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        self.turn_label = ttk.Label(status_frame, text="ターン: 1")
        self.turn_label.grid(row=0, column=0, sticky="w")

        self.player_label = ttk.Label(status_frame, text="")
        self.player_label.grid(row=1, column=0, sticky="w")

        self.enemy_label = ttk.Label(status_frame, text="")
        self.enemy_label.grid(row=2, column=0, sticky="w")

        # バトルログ
        log_frame = ttk.LabelFrame(self, text="バトルログ")
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.log_text = tk.Text(log_frame, height=12, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 手札ボタン置き場
        hand_frame = ttk.LabelFrame(self, text="手札")
        hand_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        self.hand_frame = hand_frame

        # 下部操作ボタン
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)

        self.end_turn_btn = ttk.Button(
            ctrl_frame, text="ターン終了", command=self.on_end_turn
        )
        self.end_turn_btn.pack(side=tk.RIGHT)

    # ===== ゲーム初期化 =====
    def _setup_game(self):
        random.seed(42)

        starter_cards = make_starter_deck("HIDEYOSHI")
        starter_ids = [c.spec_id for c in starter_cards]
        master = MasterDeck(starter_ids)

        player = Player("羽柴隊", max_hp=40)
        enemy = Enemy("明智兵", max_hp=35)
        pdeck = BattleDeck(master.instantiate())
        edeck = BattleDeck([])  # v1.10は敵デッキなしAI

        bm = BattleManager(player, enemy, pdeck, edeck, max_energy=3, hand_size=5)
        bm.logger = self.log  # コンソールprintの代わりにUIログへ
        self.bm = bm

        self.log("=== UIバトル開始 ===")
        bm.start_battle()
        bm.start_turn()
        self.refresh_ui()

    # ===== ログ出力 =====
    def log(self, *msgs):
        text = " ".join(str(m) for m in msgs)
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        # print(text)  # デバッグしたければ残してOK

    # ===== 画面更新 =====
    def refresh_ui(self):
        bm = self.bm
        if bm is None:
            return

        p, e = bm.player, bm.enemy

        self.turn_label.config(text=f"ターン: {bm.turn}")
        self.player_label.config(
            text=f"👤 {p.name} HP {p.hp}/{p.max_hp} | Block {p.block} | Energy {p.energy}"
        )
        self.enemy_label.config(
            text=f"💀 {e.name} HP {e.hp}/{e.max_hp} | Block {e.block}"
        )

        # 既存の手札ボタンを削除
        for b in self.hand_buttons:
            b.destroy()
        self.hand_buttons.clear()

        # ゲーム終了ならボタン貼り直さない
        if self.game_over:
            return

        # 手札1枚ごとにボタンを生成
        for i, c in enumerate(bm.pdeck.hand):
            # カード名を取得
            from data import CARD_SPECS
            card_name = CARD_SPECS[c.spec_id]["name"]
            cost_icon = f"🔸{c.cost}"
            label = f"{cost_icon} {card_name} ({c.card_type} {c.power})"

            btn = ttk.Button(
                self.hand_frame,
                text=label,
                command=lambda idx=i: self.on_play_card(idx),
                )
            # 2行×4列にグリッド配置
            row = i // 3  # 0〜3 → 1行目 / 4〜7 → 2行目
            col = i % 3
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            self.hand_buttons.append(btn)
        # 列幅を均等に広げる（見た目整える用）
        for col in range(4):
            self.hand_frame.grid_columnconfigure(col, weight=1)

    # ===== カードプレイ処理 =====
    def on_play_card(self, idx: int):
        if self.game_over or self.bm is None:
            return

        bm = self.bm
        log = bm.play_player_card(idx)
        self.log(log)
        self.refresh_ui()

        over, msg = bm.is_battle_over()
        if over:
            self.game_over = True
            self.log(msg)
            return

    # ===== ターン終了→敵ターン→次ターン開始 =====
    def on_end_turn(self):
        if self.game_over or self.bm is None:
            return

        bm = self.bm

        # プレイヤーターン終了
        bm.end_turn()

        # 敵行動
        enemy_log = bm.enemy_act()
        self.log(enemy_log)
        self.refresh_ui()

        over, msg = bm.is_battle_over()
        if over:
            self.game_over = True
            self.log(msg)
            return

        # 次ターン開始
        bm.start_turn()
        self.refresh_ui()


if __name__ == "__main__":
    app = BattleApp()
    app.mainloop()