"""
╔══════════════════════════════════════════════════════════════╗
║     QUANTUM COMPANY AGENT — Flask API  (Fixed v3)           ║
║     Alpha Mind Systems                                      ║
║     - Luôn trả JSON, không bao giờ trả HTML ở /chat        ║
║     - CORS đúng cho mọi origin                              ║
║     - Serve index.html ở route /                            ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, jsonify, send_file
from copy import deepcopy
import datetime, random, os

app = Flask(__name__)

# ── CORS thủ công — không cần flask-cors ──────────────────────────
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.after_request
def after_request(response):
    return add_cors(response)

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        from flask import Response
        return add_cors(Response("", 204))

# ── Bắt mọi lỗi Flask → trả JSON thay vì HTML ────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Không tìm thấy route", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method không được phép", "code": 405}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": f"Lỗi server: {str(e)}", "code": 500}), 500

# ══════════════════════════════════════════════
#  QUANTUM ENGINE
# ══════════════════════════════════════════════
DEFAULT_STATE = {
    "people_growth":        {"value": 70, "label": "Phát triển nhân sự",       "domain": "HR"},
    "leadership":           {"value": 72, "label": "Năng lực lãnh đạo",         "domain": "HR"},
    "culture":              {"value": 68, "label": "Văn hóa doanh nghiệp",      "domain": "HR"},
    "sales_performance":    {"value": 65, "label": "Hiệu suất bán hàng",        "domain": "Sales"},
    "customer_value":       {"value": 67, "label": "Giá trị khách hàng",        "domain": "Sales"},
    "conversion_rate":      {"value": 60, "label": "Tỷ lệ chốt deal",           "domain": "Sales"},
    "brand_equity":         {"value": 63, "label": "Thương hiệu",               "domain": "Marketing"},
    "marketing_efficiency": {"value": 62, "label": "Hiệu quả marketing",        "domain": "Marketing"},
    "market_reach":         {"value": 58, "label": "Độ phủ thị trường",         "domain": "Marketing"},
    "cash_flow":            {"value": 66, "label": "Dòng tiền",                 "domain": "Finance"},
    "profitability":        {"value": 64, "label": "Lợi nhuận",                 "domain": "Finance"},
    "operational_cost":     {"value": 55, "label": "Chi phí vận hành",          "domain": "Finance"},
    "process_quality":      {"value": 69, "label": "Chất lượng quy trình",      "domain": "Operations"},
    "delivery_speed":       {"value": 63, "label": "Tốc độ giao việc",          "domain": "Operations"},
    "risk_level":           {"value": 40, "label": "Mức độ rủi ro",             "domain": "Operations"},
    "innovation":           {"value": 61, "label": "Đổi mới sáng tạo",          "domain": "Strategy"},
    "learning_rate":        {"value": 65, "label": "Tốc độ học hỏi",            "domain": "Strategy"},
    "strategic_clarity":    {"value": 70, "label": "Rõ ràng chiến lược",        "domain": "Strategy"},
}

ENTANGLEMENT_MATRIX = {
    "people_growth":        {"sales_performance": 0.7, "marketing_efficiency": 0.6, "customer_value": 0.65,
                             "leadership": 0.8, "culture": 0.75, "innovation": 0.7, "learning_rate": 0.8,
                             "process_quality": 0.6, "brand_equity": 0.5},
    "leadership":           {"culture": 0.85, "strategic_clarity": 0.8, "people_growth": 0.75,
                             "innovation": 0.7, "sales_performance": 0.6, "cash_flow": 0.55},
    "culture":              {"people_growth": 0.8, "leadership": 0.7, "innovation": 0.75,
                             "customer_value": 0.6, "brand_equity": 0.65, "learning_rate": 0.7},
    "sales_performance":    {"customer_value": 0.85, "cash_flow": 0.8, "profitability": 0.75,
                             "brand_equity": 0.6, "marketing_efficiency": 0.65, "conversion_rate": 0.9},
    "customer_value":       {"sales_performance": 0.85, "brand_equity": 0.8, "market_reach": 0.7,
                             "cash_flow": 0.65, "conversion_rate": 0.75, "profitability": 0.6},
    "conversion_rate":      {"sales_performance": 0.85, "customer_value": 0.7, "cash_flow": 0.75,
                             "marketing_efficiency": 0.6},
    "brand_equity":         {"market_reach": 0.8, "customer_value": 0.75, "sales_performance": 0.65,
                             "marketing_efficiency": 0.7, "conversion_rate": 0.6},
    "marketing_efficiency": {"brand_equity": 0.75, "market_reach": 0.85, "customer_value": 0.65,
                             "sales_performance": 0.6, "conversion_rate": 0.55},
    "market_reach":         {"brand_equity": 0.7, "customer_value": 0.65, "marketing_efficiency": 0.75,
                             "sales_performance": 0.55},
    "cash_flow":            {"profitability": 0.85, "operational_cost": -0.6, "delivery_speed": 0.5,
                             "risk_level": -0.55, "strategic_clarity": 0.5},
    "profitability":        {"cash_flow": 0.8, "operational_cost": -0.65, "innovation": 0.55,
                             "strategic_clarity": 0.6, "risk_level": -0.5},
    "operational_cost":     {"profitability": -0.7, "cash_flow": -0.65, "risk_level": 0.5,
                             "process_quality": -0.4},
    "process_quality":      {"delivery_speed": 0.8, "customer_value": 0.65, "operational_cost": -0.55,
                             "risk_level": -0.6, "profitability": 0.55},
    "delivery_speed":       {"customer_value": 0.7, "process_quality": 0.75, "sales_performance": 0.5,
                             "risk_level": -0.45},
    "risk_level":           {"profitability": -0.6, "cash_flow": -0.55, "process_quality": -0.5,
                             "strategic_clarity": -0.45, "innovation": -0.35},
    "innovation":           {"learning_rate": 0.85, "brand_equity": 0.7, "strategic_clarity": 0.75,
                             "market_reach": 0.6, "people_growth": 0.55},
    "learning_rate":        {"innovation": 0.85, "people_growth": 0.8, "process_quality": 0.65,
                             "strategic_clarity": 0.7, "culture": 0.6},
    "strategic_clarity":    {"leadership": 0.8, "innovation": 0.7, "sales_performance": 0.6,
                             "people_growth": 0.65, "operational_cost": -0.4},
}

THRESHOLDS = {
    "risk_level":       {"max": 70, "label": "Rủi ro quá cao"},
    "operational_cost": {"max": 80, "label": "Chi phí vượt ngưỡng"},
    "cash_flow":        {"min": 40, "label": "Dòng tiền nguy hiểm"},
    "profitability":    {"min": 40, "label": "Lợi nhuận thấp nguy hiểm"},
    "culture":          {"min": 35, "label": "Văn hóa xuống dốc"},
}


class QuantumEngine:
    def __init__(self, state):
        self.state = deepcopy(state)

    def coherent_update(self, axis, delta, reason=""):
        if axis not in self.state:
            return {"error": f"Trục '{axis}' không tồn tại"}
        old = {k: v["value"] for k, v in self.state.items()}
        changes = {}
        self.state[axis]["value"] = max(0, min(100, self.state[axis]["value"] + delta))
        changes[axis] = round(self.state[axis]["value"] - old[axis], 2)
        for linked, weight in ENTANGLEMENT_MATRIX.get(axis, {}).items():
            if linked in self.state:
                ed = delta * weight * 0.6
                ov = self.state[linked]["value"]
                nv = max(0, min(100, ov + ed))
                self.state[linked]["value"] = nv
                if abs(nv - ov) > 0.1:
                    changes[linked] = round(nv - ov, 2)
        return {"triggered_axis": axis, "delta": delta, "reason": reason,
                "coherent_changes": changes, "axes_affected": len(changes)}

    def balance_score(self):
        vals = [v["value"] for v in self.state.values()]
        avg  = sum(vals) / len(vals)
        return round(avg - self.state["risk_level"]["value"] * 0.3
                        - self.state["operational_cost"]["value"] * 0.2, 2)

    def get_snapshot(self):
        return {k: round(v["value"], 1) for k, v in self.state.items()}

    def get_by_domain(self):
        domains = {}
        for k, v in self.state.items():
            d = v["domain"]
            if d not in domains:
                domains[d] = []
            domains[d].append({"axis": k, "label": v["label"], "value": round(v["value"], 1)})
        return domains


class QuantumCore:
    def __init__(self, engine):
        self.engine  = engine
        self.history = []

    def act(self, axis, delta, reason=""):
        result = self.engine.coherent_update(axis, delta, reason)
        self.history.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "action": f"[{axis}] {delta:+.1f}",
            "reason": reason,
            "axes_affected": result.get("axes_affected", 0),
            "balance": self.engine.balance_score(),
        })
        return result

    def create_idea(self, topic):
        keys = list(self.engine.state.keys())
        axes_map = {k: round(random.uniform(0.6, 0.95), 2)
                    for k in random.sample(keys, min(6, len(keys)))}
        sim = QuantumEngine(self.engine.state)
        revelations, all_axes = [], {}
        for rnd in range(1, 4):
            rnd_rev = {}
            for axis, weight in axes_map.items():
                if axis in sim.state:
                    d  = round(weight * 10 * (1 / rnd), 2)
                    ov = sim.state[axis]["value"]
                    nv = max(0, min(100, ov + d))
                    sim.state[axis]["value"] = nv
                    if abs(nv - ov) > 0.1:
                        rnd_rev[axis] = {
                            "label": DEFAULT_STATE[axis]["label"],
                            "delta": round(nv - ov, 2),
                            "new_value": round(nv, 1)
                        }
                        all_axes[axis] = all_axes.get(axis, 0) + round(nv - ov, 2)
            new_axes = {}
            for axis in rnd_rev:
                for la, w in ENTANGLEMENT_MATRIX.get(axis, {}).items():
                    if la not in axes_map:
                        new_axes[la] = round(w * 0.5, 2)
            axes_map = {**axes_map, **new_axes}
            revelations.append({
                "round": rnd,
                "revelations": rnd_rev,
                "balance": round(sim.balance_score(), 2)
            })
        top   = sorted(all_axes.items(), key=lambda x: x[1], reverse=True)[:5]
        ideas = [f"Phát triển [{DEFAULT_STATE[a]['label']}] ({d:+.1f}) → lan ra toàn hệ"
                 for a, d in top]
        gain  = sim.balance_score() - self.engine.balance_score()
        return {
            "topic": topic,
            "revelations": revelations,
            "total_axes": len(all_axes),
            "balance_gain": round(gain, 3),
            "ideas": ideas,
            "verdict": "✅ Tính cân bằng dương — khuyến nghị phát triển" if gain > 0 else "⚠️ Cần điều chỉnh trục gốc"
        }

    def daily_plan(self):
        actions = {
            "HR": "Tổ chức 1-on-1 coaching, đặt OKR rõ ràng",
            "Sales": "Review pipeline, tập trung top 20% khách tiềm năng",
            "Marketing": "Chạy nội dung educate + retargeting khách cũ",
            "Finance": "Rà soát chi phí cố định, tăng tốc thu hồi công nợ",
            "Operations": "Audit quy trình bottleneck, cải tiến ngay",
            "Strategy": "Workshop chiến lược 2h, cập nhật roadmap quý",
        }
        plans = {}
        for domain, axes in self.engine.get_by_domain().items():
            w = min(axes, key=lambda x: x["value"])
            s = max(axes, key=lambda x: x["value"])
            plans[domain] = {
                "focus":    f"Nâng [{w['label']}] ({w['value']:.0f}/100)",
                "leverage": f"Dùng [{s['label']}] ({s['value']:.0f}/100) làm đòn bẩy",
                "action":   actions.get(domain, "Phân tích dữ liệu, đề xuất hành động"),
            }
        return plans


class QuantumAuditor:
    def __init__(self, engine, core):
        self.engine = engine
        self.core   = core

    def audit(self):
        snap   = self.engine.get_snapshot()
        alerts = []
        for axis, rule in THRESHOLDS.items():
            val = snap.get(axis, 50)
            if "max" in rule and val > rule["max"]:
                alerts.append(f"🔴 {rule['label']}: {axis}={val:.0f}")
            if "min" in rule and val < rule["min"]:
                alerts.append(f"🔴 {rule['label']}: {axis}={val:.0f}")
        balance = self.engine.balance_score()
        health  = ("🟢 TỐT" if balance >= 50
                   else "🟡 CẦN CHÚ Ý" if balance >= 35 else "🔴 NGUY HIỂM")
        sorted_axes = sorted(snap.items(), key=lambda x: x[1])
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "health": health,
            "balance_score": balance,
            "alerts": alerts if alerts else ["✅ Không có cảnh báo"],
            "weakest":   [(k, v) for k, v in sorted_axes[:3]],
            "strongest": [(k, v) for k, v in sorted_axes[-3:]],
            "total_actions": len(self.core.history),
        }


# ── Singleton ─────────────────────────────────
engine  = QuantumEngine(DEFAULT_STATE)
core    = QuantumCore(engine)
auditor = QuantumAuditor(engine, core)


# ══════════════════════════════════════════════
#  CHAT PROCESSOR
# ══════════════════════════════════════════════
def process_message(msg: str) -> dict:
    ml = msg.lower().strip()

    # status
    if any(w in ml for w in ["status", "sức khỏe", "tình trạng", "health"]):
        data = auditor.audit()
        snap = engine.get_by_domain()
        domains = {
            d: {"avg": round(sum(a["value"] for a in axes)/len(axes), 1), "axes": axes}
            for d, axes in snap.items()
        }
        return {"type": "status",
                "text": f"Sức khỏe: {data['health']} | Balance: {data['balance_score']}/100",
                "data": {**data, "domains": domains}}

    # report
    if any(w in ml for w in ["report", "báo cáo", "bao cao"]):
        return {"type": "report",
                "text": f"📊 Báo cáo — {datetime.datetime.now().strftime('%H:%M %d/%m/%Y')}",
                "data": {"audit": auditor.audit(), "daily_plan": core.daily_plan(),
                         "history": core.history[-10:]}}

    # axes
    if any(w in ml for w in ["axes", "danh sách", "trục", "list"]):
        snap = engine.get_snapshot()
        axes_info = [{"axis": k, "label": DEFAULT_STATE[k]["label"],
                      "domain": DEFAULT_STATE[k]["domain"], "value": v}
                     for k, v in snap.items()]
        return {"type": "axes", "text": f"📐 {len(axes_info)} trục quantum:", "data": axes_info}

    # create
    if any(w in ml for w in ["create", "tạo", "ý tưởng", "y tuong", "sáng tạo", "san pham", "sản phẩm"]):
        topic = msg
        for kw in ["create ", "tạo ý tưởng về ", "tạo sản phẩm ", "tạo ", "ý tưởng về ", "sáng tạo về "]:
            if kw in ml:
                topic = msg[ml.find(kw) + len(kw):].strip() or msg
                break
        result = core.create_idea(topic)
        ideas  = "\n".join(f"→ {i}" for i in result["ideas"])
        return {"type": "create",
                "text": f"🌀 Phân tích quantum: **{topic}**\n\n{ideas}\n\n{result['verdict']}",
                "data": result}

    # plan
    if any(w in ml for w in ["plan", "kế hoạch", "ke hoach", "hôm nay", "hom nay"]):
        return {"type": "plan", "text": "📋 Kế hoạch hôm nay:", "data": core.daily_plan()}

    # act — tìm pattern <axis> <số>
    parts = ml.split()
    for i, part in enumerate(parts):
        if part in DEFAULT_STATE:
            try:
                delta  = float(parts[i+1]) if i+1 < len(parts) else 10.0
                reason = " ".join(parts[i+2:]) if i+2 < len(parts) else msg
                result = core.act(part, delta, reason)
                changes = [
                    f"{'↗' if v>0 else '↘'} {DEFAULT_STATE[a]['label']}: {v:+.1f}"
                    for a, v in list(result["coherent_changes"].items())[:6]
                ]
                return {"type": "act",
                        "text": f"⚡ [{part}] {delta:+.1f}\n" + "\n".join(changes) +
                                f"\nBalance: {engine.balance_score():.1f}/100",
                        "data": result}
            except (IndexError, ValueError):
                pass

    # help
    if any(w in ml for w in ["help", "giúp", "hướng dẫn", "lệnh", "lenh"]):
        return {"type": "help", "text": "🤖 Hướng dẫn sử dụng Quantum Agent:",
                "data": {"commands": [
                    {"cmd": "status",              "desc": "Xem sức khỏe toàn hệ thống"},
                    {"cmd": "report",              "desc": "Báo cáo đầy đủ theo phòng ban"},
                    {"cmd": "axes",                "desc": "Danh sách 18 trục quantum"},
                    {"cmd": "plan",                "desc": "Kế hoạch hành động hôm nay"},
                    {"cmd": "create <chủ đề>",     "desc": "Tạo ý tưởng / sản phẩm AI"},
                    {"cmd": "<axis> <delta>",       "desc": "Tác động trực tiếp lên trục"},
                ]}}

    return {"type": "hint",
            "text": "Tôi chưa hiểu lệnh này. Thử:\n• `status` — sức khỏe hệ thống\n• `create chatbot AI` — tạo ý tưởng\n• `report` — báo cáo\n• `help` — xem tất cả lệnh",
            "data": {}}


# ══════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════

@app.route("/")
def index():
    # Phục vụ index.html nếu có, không thì trả JSON
    if os.path.exists("index.html"):
        return send_file("index.html")
    return jsonify({"status": "ok", "message": "Quantum Agent API đang chạy", "company": "Alpha Mind Systems"})


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    try:
        body = request.get_json(force=True, silent=True) or {}
        msg  = str(body.get("message", "")).strip()
        if not msg:
            return jsonify({"type": "error", "text": "Thiếu nội dung message", "data": {}}), 400
        result = process_message(msg)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"type": "error", "text": f"Lỗi xử lý: {str(e)}", "data": {}}), 500


@app.route("/status", methods=["GET"])
def get_status():
    try:
        data = auditor.audit()
        snap = engine.get_by_domain()
        domains = {
            d: {"avg": round(sum(a["value"] for a in axes)/len(axes), 1), "axes": axes}
            for d, axes in snap.items()
        }
        return jsonify({**data, "domains": domains}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/snapshot", methods=["GET"])
def get_snapshot():
    return jsonify(engine.get_snapshot()), 200


@app.route("/reset", methods=["POST", "OPTIONS"])
def reset():
    global engine, core, auditor
    engine  = QuantumEngine(DEFAULT_STATE)
    core    = QuantumCore(engine)
    auditor = QuantumAuditor(engine, core)
    return jsonify({"ok": True, "message": "Đã reset về trạng thái ban đầu"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "agent": "Quantum Agent", "company": "Alpha Mind Systems"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
