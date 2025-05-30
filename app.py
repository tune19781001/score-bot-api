from flask import Flask, request, jsonify, send_from_directory
import os
from memory_bot import (
    save_judgment,
    search_similar,
    update_conversation,
    get_conversation_history,
    get_response
)
from functions import evaluate_market_conditions  # ✅ 関数呼び出し追加！
from upload_to_drive import upload_file_to_drive  # ✅ Drive連携を追加

app = Flask(__name__)

# ✅ UptimeRobot用 pingエンドポイント
@app.route("/ping")
def ping():
    return "pong", 200

# API起動確認用
@app.route("/")
def index():
    return "Score Evaluation API is running!"

# スコア計算ロジック
def score_evaluation(inputs):
    total = 0
    comments = []

    if inputs["spy"] > 0 and inputs["qqq"] > 0:
        total += 2
        comments.append("SPY/QQQ rising - strong market")
    if inputs["vix"] < 20:
        total += 1
        comments.append("Low VIX - low risk")
    if 145 <= inputs["usd_jpy"] <= 155:
        total += 1
        comments.append("Stable exchange rate")
    if inputs["rsi"] < 30:
        total += 2
        comments.append("RSI below 30 - oversold, rebound expected")
    if inputs["volume_ratio"] > 1.5:
        total += 1
        comments.append("High volume - high attention")
    if inputs["ma_break"]:
        total += 1
        comments.append("Price broke above MA")
    if inputs["roe"] > 10:
        total += 1
        comments.append("ROE > 10% - good efficiency")
    if inputs["profit_margin"] > 15:
        total += 1
        comments.append("High profit margin - profitable")

    return total, comments

# 最終判断ロジック
def judge(score):
    if score >= 15:
        return "Strong Buy"
    elif score >= 12:
        return "Buy with Caution"
    elif score >= 10:
        return "Hold"
    else:
        return "Sell"

# スコア取得API
@app.route("/score", methods=["POST"])
def score():
    data = request.json
    score_val, comments = score_evaluation(data)
    judgment = judge(score_val)

    result = {
        "score": score_val,
        "comments": comments,
        "judgment": judgment,
        "saved": True
    }

    update_conversation(str(data), str(result))
    save_judgment(str(data), judgment)

    return jsonify(result)

# Function Calling API
@app.route("/function_call", methods=["POST"])
def function_call():
    data = request.json
    function_name = data.get("function")
    args = data.get("args", {})

    if function_name == "evaluate_market_conditions":
        result = evaluate_market_conditions(args)
        return jsonify(result)

    return jsonify({"error": "Function not found"}), 400

# 判断結果の保存
@app.route("/save_judgment", methods=["POST"])
def save():
    data = request.json
    input_text = data.get("input")
    result = data.get("result")

    if not input_text or not result:
        return jsonify({"error": "input and result are required"}), 400

    save_judgment(input_text, result)

    # ✅ Google Driveにアップロードする（必要ならファイルパス調整）
    upload_file_to_drive("judgments.pkl")
    upload_file_to_drive("faiss.index")

    return jsonify({"status": "Saved!"})

# 類似履歴検索
@app.route("/search_similar", methods=["POST"])
def search():
    data = request.json
    input_text = data.get("input")

    if not input_text:
        return jsonify({"error": "input is required"}), 400

    raw = search_similar(input_text)
    history_text = raw.get("history", "")
    lines = history_text.strip().split("\n")
    pairs = [{"input": lines[i][7:], "output": lines[i + 1][8:]} for i in range(0, len(lines)-1, 2)]
    return jsonify({"results": pairs})

# 会話履歴取得
@app.route("/conversation_history", methods=["GET"])
def history():
    history_text = get_conversation_history(limit=3)
    return jsonify({"history": history_text})

# メモリBotテスト用
@app.route("/memory", methods=["GET", "POST"])
def memory_check():
    if request.method == "GET":
        return "Memory bot is alive!"
    try:
        input_text = request.json.get("input", "")
        response = get_response(input_text)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GPTs用 OpenAPI 配信
@app.route('/.well-known/<path:filename>')
def well_known_static(filename):
    return send_from_directory('.well-known', filename)

@app.route('/.well-known/openapi.yaml')
def serve_openapi_yaml():
    return send_from_directory('.well-known', 'openapi.yaml', mimetype='application/x-yaml')

# Flask起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
