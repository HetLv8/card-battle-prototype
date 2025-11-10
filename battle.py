# battle.py
from typing import Tuple
from model import Player, Enemy, CardInstance
from deck import DeckState
from data import CARD_SPECS

def make_card(spec_id: str) -> CardInstance:
    spec = CARD_SPECS[spec_id]
    return CardInstance(
        spec_id=spec_id,
        cost=spec["cost"],
        power=spec["power"],
        card_type=spec["card_type"],
        tags=spec.get("tags", []),
    )

def start_battle(player: Player, enemy: Enemy, pdeck: DeckState, edeck: DeckState):
    # 開幕ドロー等
    pdeck.draw(5)
    edeck.draw(1)  # 敵も“行動候補”を手札に1枚だけ（v1.10は簡略）
    turn = 1
    return turn

def start_turn(player: Player, enemy: Enemy, pdeck: DeckState):
    player.reset_turn(3)
    # 必要なら開始時ドロー
    if len(pdeck.hand) < 5:
        pdeck.draw(5 - len(pdeck.hand))

def play_card(idx: int, player: Player, enemy: Enemy, pdeck: DeckState) -> str:
    if idx < 0 or idx >= len(pdeck.hand):
        return "⚠ 無効な番号。"
    card = pdeck.hand.pop(idx)
    # コストチェック
    if card.cost > player.energy:
        # 使えなかったら手札に戻す
        pdeck.hand.insert(idx, card)
        return "⚠ エナジー不足。"
    # 効果解決（v1.10は攻撃/防御のみ）
    if card.card_type == "attack":
        dealt = enemy.take_damage(card.power)
        log = f"▶ {player.name} の攻撃 {card.power} → {enemy.name} に {dealt}"
    elif card.card_type == "block":
        player.block += card.power
        log = f"▶ {player.name} は防御 {card.power} を得た (合計 {player.block})"
    else:
        log = "…何も起きない"
    player.energy -= card.cost
    # 捨て札へ
    pdeck.discard_card(card)
    return log

def enemy_act(enemy: Enemy, player: Player, edeck: DeckState) -> str:
    # v1.10：攻撃優先→なければ防御（手札1枚だけ前提）
    if not edeck.hand:
        edeck.draw(1)
        if not edeck.hand:
            return f"▶ {enemy.name} は様子を見ている…"
    card = edeck.hand.pop(0)
    if card.card_type == "attack":
        dealt = player.take_damage(card.power)
        log = f"▶ {enemy.name} の攻撃 {card.power} → {player.name} に {dealt}"
    else:
        enemy.block += card.power
        log = f"▶ {enemy.name} は防御 {card.power} (合計 {enemy.block})"
    edeck.discard_card(card)
    
    enemy.turn_index += 1
    return log

def is_battle_over(player: Player, enemy: Enemy) -> Tuple[bool, str]:
    if enemy.hp <= 0:
        return True, "🎉 勝利！"
    if player.hp <= 0:
        return True, "💀 敗北…"
    return False, ""
