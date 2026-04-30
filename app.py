"""
Quantum Company Agent — Web API
Chạy trên Railway qua Flask
"""

import os
import json
from flask import Flask, request, jsonify
from quantum_company_agent import (
    QuantumEngine, QuantumCore, QuantumAuditor, DEFAULT_STATE
)

app = Flask(__name__)

# Khởi tạo agent (dùng chung 1 instance)
engine = QuantumEngine(DEFAULT_STATE)
core = QuantumCore(engine)
auditor = QuantumAuditor(engine, core)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "name": "Quantum Company Agent",
        "status": "running",
        "endpoints": [
            "GET  /status       — Sức khỏe hệ thống",
            "GET  /report       — Báo cáo đầy đủ",
            "POST /act          — Tác động trục cân bằng",
            "POST /create       — Sáng tạo ý tưởng",
            "GET  /axes         — Danh sách 18 trục",
            "GET  /plan         — Kế hoạch ngày",
        ]
    })


@app.route("/status", methods=["GET"])
def status():
    audit = auditor.audit()
    return jsonify(audit)


@app.route("/report", methods=["GET"])
def report():
    return jsonify({
        "report": auditor.full_report(),
        "by_domain": engine.get_by_domain(),
        "balance_score": engine.balance_score(),
    })


@app.route("/act", methods=["POST"])
def act():
    """
    Body JSON: {"axis": "people_growth", "delta": 10, "reason": "Tuyển nhân sự mới"}
    """
    data = request.get_json()
    if not data or "axis" not in data or "delta" not in data:
        return jsonify({"error": "Cần có 'axis' và 'delta'"}), 400

    axis = data["axis"]
    delta = float(data["delta"])
    reason = data.get("reason", "")

    if axis not in DEFAULT_STATE:
        return jsonify({"error": f"Trục '{axis}' không tồn tại"}), 400

    result = core.act(axis, delta, reason)
    result["balance_score"] = engine.balance_score()
    return jsonify(result)


@app.route("/create", methods=["POST"])
def create():
    """
    Body JSON: {"topic": "bat dong san"}
    """
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "Cần có 'topic'"}), 400

    topic = data["topic"]
    result = core.create_idea(topic)
    return jsonify(result)


@app.route("/axes", methods=["GET"])
def axes():
    snapshot = engine.get_snapshot()
    result = {}
    for k, v in DEFAULT_STATE.items():
        result[k] = {
            "label": v["label"],
            "domain": v["domain"],
            "value": snapshot[k],
        }
    return jsonify(result)


@app.route("/plan", methods=["GET"])
def plan():
    return jsonify(core.daily_plan())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
