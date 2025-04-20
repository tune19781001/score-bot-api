def score_evaluation(inputs):
    total = 0
    comments = []

    if inputs["spy"] > 0 and inputs["qqq"] > 0:
        total += 2
        comments.append("SPY/QQQが上昇 → 地合い良好")
    if inputs["vix"] < 20:
        total += 1
        comments.append("VIX低下 → リスク低め")
    if 145 <= inputs["usd_jpy"] <= 155:
        total += 1
        comments.append("為替安定ゾーン")

    if inputs["rsi"] < 30:
        total += 2
        comments.append("RSI30以下 → 売られすぎで反発期待")
    if inputs["volume_ratio"] > 1.5:
        total += 1
        comments.append("出来高急増 → 注目度高")
    if inputs["ma_break"]:
        total += 1
        comments.append("移動平均線上抜け")

    if inputs["roe"] > 10:
        total += 1
        comments.append("ROE > 10% → 経営効率◎")
    if inputs["profit_margin"] > 15:
        total += 1
        comments.append("利益率高い → 収益性あり")

    return total, comments

# 実行
if __name__ == "__main__":
    print("📊 スコア評価Bot（簡易版）")

    spy = float(input("SPYの前日比（%）: "))
    qqq = float(input("QQQの前日比（%）: "))
    vix = float(input("VIXの値: "))
    usd_jpy = float(input("USD/JPYの為替レート: "))
    rsi = float(input("RSIの値: "))
    volume_ratio = float(input("出来高倍率: "))
    ma_break = input("移動平均線を上抜け？ (yes/no): ").lower() == "yes"
    roe = float(input("ROE（%）: "))
    profit_margin = float(input("営業利益率（%）: "))

    inputs = {
        "spy": spy,
        "qqq": qqq,
        "vix": vix,
        "usd_jpy": usd_jpy,
        "rsi": rsi,
        "volume_ratio": volume_ratio,
        "ma_break": ma_break,
        "roe": roe,
        "profit_margin": profit_margin
    }

    score, comments = score_evaluation(inputs)

    print(f"\n✅ 総合スコア：{score} / 20 点")
    print("📌 コメント:")
    for c in comments:
        print(" - " + c)

    if score >= 15:
        print("🟢 強気判断（条件が整っている）")
    elif score >= 12:
        print("🟡 条件付きGO（不安要素あり）")
    elif score >= 10:
        print("🟠 様子見（保留）")
    else:
        print("🔴 弱気（見送り推奨）")
