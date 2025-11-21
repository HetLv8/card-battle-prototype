# card_effects.py

"""
カード効果とバフ（Buff）処理 + mini ops エンジン
"""

from __future__ import annotations
from typing import Any, Dict, List
from data import CARD_SPECS
from model import CardInstance

# =========================
# バフ関連ユーティリティ
# =========================

BuffDict = Dict[str, Any]  # {"kind": str, "power": int, "turns": int, "trigger": str}


def _ensure_buffs_attr(actor: Any) -> None:
    """Actor に buffs リストがなければ生やす。"""
    if not hasattr(actor, "buffs") or actor.buffs is None:
        actor.buffs: List[BuffDict] = []  # type: ignore[attr-defined]


def add_buff(actor: Any, kind: str, power: int, turns: int, trigger: str) -> None:
    """
    バフ1つを追加する。
    - 重ねがけは「インスタンスが増える」だけ。
    """
    _ensure_buffs_attr(actor)
    actor.buffs.append(
        {"kind": kind, "power": int(power), "turns": int(turns), "trigger": trigger}
    )


def tick_buffs(actor: Any) -> None:
    """
    ターン終了などで呼び出して、すべてのバフの残ターンを1減らす。
    0以下になったものは削除。
    """
    _ensure_buffs_attr(actor)
    alive: List[BuffDict] = []
    for b in actor.buffs:
        b["turns"] -= 1
        if b["turns"] > 0:
            alive.append(b)
    actor.buffs = alive  # type: ignore[attr-defined]


# --- イベントごとにバフを適用するための補助 ---

def apply_buffs_on_turn_start(bm: Any, actor: Any, enemy: Any) -> None:
    """
    ターン開始時に呼び出してほしいフック。
    """
    _ensure_buffs_attr(actor)
    logs: List[str] = []

    for b in actor.buffs:
        if b["trigger"] != "turn_start":
            continue
        kind = b["kind"]
        power = b["power"]

        if kind == "FORM_WALL":  # S23: 陣形：堅壁（3T毎ターンBlock+3）
            actor.block += power
            logs.append(f"{actor.name} の堅壁 → Block+{power}（合計 {actor.block}）")

        elif kind == "FORM_WEAK_STACK":  # S25: 陣形：弱体蓄積
            add_buff(enemy, kind="WEAK", power=1, turns=1, trigger="on_attack_calc")
            logs.append(f"{actor.name} の弱体蓄積 → {enemy.name} に弱体+1")

        elif kind == "FORM_DRAW":  # S26: 陣形：散兵隊（2T毎ターンドロー+1）
            if hasattr(bm, "draw_cards"):
                bm.draw_cards(actor, power)
                logs.append(f"{actor.name} の散兵隊 → カード+{power}枚")

        elif kind == "FORM_COUNTER_STACK":  # S27: 陣形：反撃陣（3T毎ターン反撃+1）
            add_buff(actor, kind="COUNTER", power=power, turns=1, trigger="on_hit")
            logs.append(f"{actor.name} の反撃陣 → 反撃+{power}")

    for line in logs:
        bm.logger(line)


def apply_buffs_on_card_play(bm: Any, card: CardInstance, user: Any, target: Any) -> None:
    """
    カード使用時に呼び出してほしいフック。
    """
    _ensure_buffs_attr(user)
    logs: List[str] = []
    ctype = getattr(card, "card_type", None) or getattr(card, "type", None)

    for b in user.buffs:
        if b["trigger"] != "on_card_play":
            continue
        kind = b["kind"]
        power = b["power"]

        if kind == "TRIG_ATTACK_COUNTER":  # S28: 反撃姿勢
            if ctype == "attack":
                add_buff(user, kind="COUNTER", power=power, turns=1, trigger="on_hit")
                logs.append(f"{user.name} の反撃姿勢 → 反撃+{power}")

        elif kind == "TRIG_DEF_COUNTER":  # S29: 攻防一体
            if ctype == "defense":
                add_buff(user, kind="COUNTER", power=power, turns=1, trigger="on_hit")
                logs.append(f"{user.name} の攻防一体 → 反撃+{power}")

        elif kind == "TRIG_SKILL_DRAW":  # S30: 一斉号令
            if ctype == "skill" and hasattr(bm, "draw_cards"):
                bm.draw_cards(user, power)
                logs.append(f"{user.name} の一斉号令 → カード+{power}枚")

        elif kind == "TRIG_ANY_COUNTER":  # S31: 士気高揚
            add_buff(user, kind="COUNTER", power=power, turns=1, trigger="on_hit")
            logs.append(f"{user.name} の士気高揚 → 反撃+{power}")

        elif kind == "TRIG_BLOCK_RECOVER":  # S32: 節度ある陣形操作
            # 実際の Block 消費検知は take_damage 側で対応予定（ここでは何もしない）
            pass

    for line in logs:
        bm.logger(line)


# =========================
# ダメージ計算
# =========================

def calc_attack_damage(attacker: Any, defender: Any, base_damage: int) -> int:
    """
    現時点では「弱体などはまだ未反映のプレーン計算」。
    後で WEAK / VULN などのバフをここに反映させる。
    """
    dmg = base_damage
    # TODO: attacker/defender.buffs から WEAK / VULN などを見て倍率をかける
    return max(int(dmg), 0)


# =========================
# mini ops エンジン
# =========================

def _log_name(card: CardInstance) -> str:
    spec_id = getattr(card, "spec_id", "")
    spec = CARD_SPECS.get(spec_id, {})
    return spec.get("name", spec_id)


def _op_attack(bm: Any, card: CardInstance, user: Any, target: Any, value: int, logs: List[str]) -> None:
    dmg = calc_attack_damage(user, target, value)
    dealt = target.take_damage(dmg)
    name = _log_name(card)
    logs.append(f"{user.name} の{name} → {target.name} に {dealt} ダメージ")


def _op_gain_block(bm: Any, card: CardInstance, user: Any, target: Any, value: int, logs: List[str]) -> None:
    user.block += value
    name = _log_name(card)
    logs.append(f"{user.name} の{name} → Block+{value}（合計 {user.block}）")


def _op_add_weak(bm: Any, card: CardInstance, user: Any, target: Any, value: int, logs: List[str]) -> None:
    """弱体を付与するシンプル版（value 段・2T 固定）。"""
    add_buff(target, kind="WEAK", power=value, turns=2, trigger="on_attack_calc")
    logs.append(f"{target.name} に弱体{value}（2T）")


def _op_add_counter(bm: Any, card: CardInstance, user: Any, target: Any, value: int, logs: List[str]) -> None:
    """反撃カウンタを付与するシンプル版（value・1T・on_hit 固定）。"""
    add_buff(user, kind="COUNTER", power=value, turns=1, trigger="on_hit")
    logs.append(f"{user.name} は反撃+{value}（1T）")


OPS_TABLE = {
    "attack": _op_attack,
    "gain_block": _op_gain_block,
    "add_weak": _op_add_weak,
    "add_counter": _op_add_counter,
}


def _run_ops(
    bm: Any,
    card: CardInstance,
    user: Any,
    target: Any,
    ops: List[Dict[str, Any]],
) -> List[str]:
    """
    data.py の "ops" 配列を順に解決するミニエンジン。
    STEP1 では timing は無視して「on_play 時に全部実行」で OK。
    """
    logs: List[str] = []
    for op_spec in ops:
        op_name = op_spec.get("op")
        if not op_name:
            continue
        handler = OPS_TABLE.get(op_name)
        if not handler:
            logs.append(f"[DEBUG] 未実装の op: {op_name}")
            continue
        value = int(op_spec.get("value", 0))
        handler(bm, card, user, target, value, logs)
    return logs


# =========================
# カードごとの基本解決
# =========================

def apply_card_effect(bm: Any, card: CardInstance, user: Any, target: Any) -> str:
    """
    バトル側から呼び出されるエントリポイント。

    方針：
    - まず data 側に "ops" があれば mini ops エンジンで解決
    - なければ旧来の「card_type と tags / spec_id」で処理する
    """
    spec_id = getattr(card, "spec_id", "")
    spec = CARD_SPECS.get(spec_id, {})
    ctype = spec.get("card_type", getattr(card, "card_type", "skill"))
    tags = spec.get("tags", [])
    name = _log_name(card)

    # ===== 1) ops 優先 =====
    ops = spec.get("ops")
    if ops:
        logs = _run_ops(bm, card, user, target, ops)
        return " / ".join(logs)

    # ===== 2) 互換用：従来ロジック =====
    logs: List[str] = []

    # --- 基本攻撃・防御 ---
    if ctype == "attack":
        base = getattr(card, "power", spec.get("power", 0))
        dmg = calc_attack_damage(user, target, base)
        dealt = target.take_damage(dmg)
        logs.append(f"{user.name} の{name} → {target.name} に {dealt} ダメージ")

    elif ctype == "defense":
        gain = getattr(card, "power", spec.get("power", 0))
        user.block += gain
        logs.append(f"{user.name} の{name} → Block+{gain}（合計 {user.block}）")

    else:  # skill
        logs.append(f"{user.name} は{name}を使用した。")

    # --- 代表的な追加効果（タグ & spec_id ベース） ---

    # 弱体付与（シンプルなものだけ）
    if "weaken" in tags:
        if spec_id in ("S4", "S9"):
            add_buff(target, kind="WEAK", power=1, turns=2, trigger="on_attack_calc")
            logs.append(f"{target.name} に弱体1（2T）")
        elif spec_id == "S10":
            add_buff(target, kind="WEAK", power=2, turns=2, trigger="on_attack_calc")
            logs.append(f"{target.name} に弱体2（2T）")
        elif spec_id == "S12":
            add_buff(target, kind="WEAK", power=2, turns=2, trigger="on_attack_calc")
            logs.append(f"{target.name} に弱体2（2T）（崩落の槍）")

    # シンプルな反撃付与
    if "counter" in tags:
        if spec_id == "S16":  # Block6＋反撃1
            add_buff(user, kind="COUNTER", power=1, turns=1, trigger="on_hit")
            logs.append(f"{user.name} は反撃+1（1T）")
        elif spec_id == "S18":  # 4ダメ＋反撃2。Block>0なら反撃+1
            add_buff(user, kind="COUNTER", power=2, turns=1, trigger="on_hit")
            if user.block > 0:
                add_buff(user, kind="COUNTER", power=1, turns=1, trigger="on_hit")
            logs.append(f"{user.name} は反撃+2(+1) を得た")
        elif spec_id == "S22":  # Block12＋反撃2。このターン反撃減少20%
            add_buff(user, kind="COUNTER", power=2, turns=1, trigger="on_hit")
            logs.append(f"{user.name} は反撃+2 を得た")

    # 陣形（turn_start 系バフ）
    if "formation" in tags:
        if spec_id == "S23":
            add_buff(user, kind="FORM_WALL", power=3, turns=3, trigger="turn_start")
            logs.append(f"{user.name} は陣形『堅壁』を展開（3T）")
        elif spec_id == "S24":
            add_buff(user, kind="FORM_DEF_BOOST", power=3, turns=2, trigger="on_card_play")
            logs.append(f"{user.name} は陣形『防御効率化』を展開（2T）")
        elif spec_id == "S25":
            add_buff(user, kind="FORM_WEAK_STACK", power=1, turns=3, trigger="turn_start")
            logs.append(f"{user.name} は陣形『弱体蓄積』を展開（3T）")
        elif spec_id == "S26":
            add_buff(user, kind="FORM_DRAW", power=1, turns=2, trigger="turn_start")
            logs.append(f"{user.name} は陣形『散兵隊』を展開（2T）")
        elif spec_id == "S27":
            add_buff(user, kind="FORM_COUNTER_STACK", power=1, turns=3, trigger="turn_start")
            logs.append(f"{user.name} は陣形『反撃陣』を展開（3T）")

    # トリガー系
    if "trigger" in tags:
        if spec_id == "S28":
            add_buff(user, kind="TRIG_ATTACK_COUNTER", power=1, turns=1, trigger="on_card_play")
            logs.append(f"{user.name} は反撃姿勢を取った（このターン攻撃で反撃+1）")
        elif spec_id == "S29":
            add_buff(user, kind="TRIG_DEF_COUNTER", power=1, turns=1, trigger="on_card_play")
            logs.append(f"{user.name} は攻防一体を発動（このターン防御で反撃+1）")
        elif spec_id == "S30":
            add_buff(user, kind="TRIG_SKILL_DRAW", power=1, turns=1, trigger="on_card_play")
            logs.append(f"{user.name} は一斉号令を発した（このターンスキルでドロー+1）")
        elif spec_id == "S31":
            add_buff(user, kind="TRIG_ANY_COUNTER", power=1, turns=1, trigger="on_card_play")
            logs.append(f"{user.name} は士気高揚した（このターンカード使用で反撃+1）")
        elif spec_id == "S32":
            add_buff(user, kind="TRIG_BLOCK_RECOVER", power=1, turns=1, trigger="on_card_play")
            logs.append(f"{user.name} は節度ある陣形操作を行った（このターンBlock消費毎にBlock+1）")

    return " / ".join(logs)
