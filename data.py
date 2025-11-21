CARD_SPECS = {
    # --- 基本防御 ---
    "S1": {
        "name": "基礎防御",
        "card_type": "defense",
        "cost": 1,
        "power": 6,
        "rarity": "C",
        "tags": ["defense"],
        "desc": "Block6",
        "ops": [
            {"op": "gain_block", "value": 6}
        ],
    },

    # --- 反撃突き（いまはとりあえず「攻撃だけ」入れておく。反撃バフは後で）---
    "S2": {"name": "反撃突き", "card_type": "attack",  "cost": 1, "power": 5, "rarity": "C", "tags": ["counter"], "desc": "5ダメ＋Block20%追加"},

    # --- 防御姿勢 ---
    "S3": {"name": "防御姿勢", "card_type": "defense", "cost": 1, "power": 8, "rarity": "C", "tags": ["retain"], "desc": "Block8。次ターン半分保持（最大6）"},

    # --- 打ち払い：4ダメ＋弱体1 ---
    "S4": {
        "name": "打ち払い",
        "card_type": "attack",
        "cost": 1,
        "power": 4,
        "rarity": "C",
        "tags": ["debuff", "weaken"],
        "desc": "4ダメ＋弱体1",
        "ops": [
            {"op": "attack", "value": 4},
            {"op": "add_weak", "value": 1}  # 基本：弱体1（2T）付与
        ],
    },

    "S5": {"name": "防御号令", "card_type": "skill",   "cost": 1, "power": 2, "rarity": "U", "tags": ["buff"], "desc": "このターン防御効果+2。次の防御2倍"},
    "S6": {"name": "逆襲指示", "card_type": "attack",  "cost": 1, "power": 5, "rarity": "R", "tags": ["counter"], "desc": "Block40%消費→その値を追加ダメ"},
    "S7": {"name": "堅実防御", "card_type": "defense", "cost": 1, "power": 8, "rarity": "U", "tags": ["defense"], "desc": "Block8。次ターン最初の被ダメ-20%"},
    "S8": {"name": "コスト軽減策", "card_type": "skill", "cost": 1, "power": 0, "rarity": "R", "tags": ["support"], "desc": "次の2枚の防御カードのコスト-1"},

    # --- 牽制突き：6ダメ＋弱体1 ---
    "S9": {
        "name": "牽制突き",
        "card_type": "attack",
        "cost": 1,
        "power": 6,
        "rarity": "C",
        "tags": ["weaken"],
        "desc": "6ダメ＋弱体1",
        "ops": [
            {"op": "attack", "value": 6},
            {"op": "add_weak", "value": 1},
        ],
    },

    "S10": {"name": "散兵射撃", "card_type": "attack", "cost": 1, "power": 4, "rarity": "C", "tags": ["weaken"], "desc": "4ダメ＋弱体2。このターン弱体×1追加ダメ"},
    "S11": {"name": "弱点看破", "card_type": "skill",  "cost": 1, "power": 0, "rarity": "U", "tags": ["weaken","buff"], "desc": "弱体10で+30%。20で+60% このターン"},
    "S12": {"name": "崩落の槍", "card_type": "attack", "cost": 2, "power": 10, "rarity": "R", "tags": ["weaken","finisher"], "desc": "10ダメ＋弱体×2。弱体半減"},
    "S13": {"name": "槍隊集中射", "card_type": "attack", "cost": 1, "power": 5, "rarity": "U", "tags": ["weaken","buff"], "desc": "5ダメ。このターン弱体×1.5追加。弱体-1"},
    "S14": {"name": "包囲網の完成", "card_type": "skill", "cost": 2, "power": 0, "rarity": "R", "tags": ["weaken","finisher"], "desc": "弱体15以上：弱体×3追加ダメ（1回）。弱体3に"},
    "S15": {"name": "戦意崩壊", "card_type": "attack", "cost": 2, "power": 12, "rarity": "R", "tags": ["weaken","finisher"], "desc": "12ダメ。弱体25以上で2倍。弱体-5"},

    # --- 槍衾の備え：Block6＋反撃1 ---
    "S16": {"name": "槍衾の備え","card_type": "defense","cost": 1,"power": 6,"rarity": "C","tags": ["counter"],"desc": "Block6＋反撃1",
        "ops": [{"op": "gain_block", "value": 6},
            {"op": "add_counter", "value": 1},],},
    "S17": {"name": "防御反撃", "card_type": "defense", "cost": 1, "power": 5, "rarity": "C", "tags": ["counter"], "desc": "Block5。次に攻撃された時反撃2倍"},
    "S18": {"name": "三段突き返し", "card_type": "attack", "cost": 1, "power": 4, "rarity": "C", "tags": ["counter"], "desc": "4ダメ＋反撃2。Block>0なら反撃+1"},
    "S19": {"name": "背水の構え", "card_type": "skill",   "cost": 1, "power": 0, "rarity": "R", "tags": ["counter","finisher"], "desc": "反撃×2即時ダメ。反撃0に"},
    "S20": {"name": "反撃維持", "card_type": "skill",      "cost": 1, "power": 0, "rarity": "U", "tags": ["counter","stance"], "desc": "このターン反撃が減少しない"},
    "S21": {"name": "大逆襲", "card_type": "attack",       "cost": 2, "power": 0, "rarity": "R", "tags": ["counter","finisher"], "desc": "反撃100%即時ダメ。反撃0に。Block+5"},
    "S22": {"name": "鉄壁迎撃", "card_type": "defense",    "cost": 2, "power": 12, "rarity": "U", "tags": ["counter","defense"], "desc": "Block12＋反撃2。このターン反撃減少20%"},

    "S23": {"name": "陣形：堅壁", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["formation"], "desc": "3T毎ターンBlock+3"},
    "S24": {"name": "陣形：防御効率化", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["formation"], "desc": "2T防御カードBlock+3"},
    "S25": {"name": "陣形：弱体蓄積", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["formation","weaken"], "desc": "3T毎ターン弱体+1"},
    "S26": {"name": "陣形：散兵隊", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["formation"], "desc": "2T毎ターンドロー+1"},
    "S27": {"name": "陣形：反撃陣", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["formation","counter"], "desc": "3T毎ターン反撃+1"},

    "S28": {"name": "反撃姿勢", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["trigger","counter"], "desc": "このターン攻撃使用時反撃+1"},
    "S29": {"name": "攻防一体", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["trigger","counter"], "desc": "このターン防御使用時反撃+1"},
    "S30": {"name": "一斉号令", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["trigger","support"], "desc": "このターンスキル使用時ドロー+1"},
    "S31": {"name": "士気高揚", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["trigger","counter"], "desc": "このターンカード使用時反撃+1"},
    "S32": {"name": "節度ある陣形操作", "card_type": "skill", "cost": 1, "power": 0, "rarity": "U", "tags": ["trigger","formation"], "desc": "このターンBlock消費毎にBlock+1"},
}
