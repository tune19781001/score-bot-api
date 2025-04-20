# functions.py

def evaluate_market_conditions(inputs):
    score = 0
    reasons = []

    if inputs["spy"] > 0:
        score += 1
        reasons.append("SPYが上昇")
    if inputs["rsi"] < 30:
        score += 1
        reasons.append("RSIが30未満 → 反発の可能性")
    if inputs["vix"] < 20:
        score += 1
        reasons.append("VIXが低い → 市場安定")

    if score >= 2:
        decision = "買いシグナル"
    else:
        decision = "様子見"

    return {
        "score": score,
        "reasons": reasons,
        "judgment": decision
    }
