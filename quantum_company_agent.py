"""
╔══════════════════════════════════════════════════════════════╗
║         QUANTUM COMPANY AGENT - ĐA NGÀNH                    ║
║         QuantumCore (Điều hành) + QuantumAuditor (Giám sát) ║
║         Dựa trên: Hiện tượng Vướng Víu Lượng Tử             ║
║         Nguyên lý: 1 là tất cả, tất cả là 1                 ║
╚══════════════════════════════════════════════════════════════╝

Cách chạy:
  python quantum_company_agent.py --mode demo
  python quantum_company_agent.py --mode interactive
  python quantum_company_agent.py --mode report
"""

import json
import os
import random
import argparse
import datetime
from copy import deepcopy

# ─────────────────────────────────────────────
#  CẤU HÌNH TRỤC CÂN BẰNG (Quantum Axes)
#  Mỗi trục là 1 khía cạnh công ty đa ngành
# ─────────────────────────────────────────────
DEFAULT_STATE = {
    # === NHÂN SỰ ===
    "people_growth":        {"value": 70, "label": "Phát triển nhân sự",       "domain": "HR"},
    "leadership":           {"value": 72, "label": "Năng lực lãnh đạo",         "domain": "HR"},
    "culture":              {"value": 68, "label": "Văn hóa doanh nghiệp",      "domain": "HR"},

    # === BÁN HÀNG ===
    "sales_performance":    {"value": 65, "label": "Hiệu suất bán hàng",        "domain": "Sales"},
    "customer_value":       {"value": 67, "label": "Giá trị khách hàng",        "domain": "Sales"},
    "conversion_rate":      {"value": 60, "label": "Tỷ lệ chốt deal",           "domain": "Sales"},

    # === MARKETING ===
    "brand_equity":         {"value": 63, "label": "Thương hiệu",               "domain": "Marketing"},
    "marketing_efficiency": {"value": 62, "label": "Hiệu quả marketing",        "domain": "Marketing"},
    "market_reach":         {"value": 58, "label": "Độ phủ thị trường",         "domain": "Marketing"},

    # === TÀI CHÍNH ===
    "cash_flow":            {"value": 66, "label": "Dòng tiền",                 "domain": "Finance"},
    "profitability":        {"value": 64, "label": "Lợi nhuận",                 "domain": "Finance"},
    "operational_cost":     {"value": 55, "label": "Chi phí vận hành",          "domain": "Finance"},

    # === VẬN HÀNH ===
    "process_quality":      {"value": 69, "label": "Chất lượng quy trình",      "domain": "Operations"},
    "delivery_speed":       {"value": 63, "label": "Tốc độ giao việc",          "domain": "Operations"},
    "risk_level":           {"value": 40, "label": "Mức độ rủi ro",             "domain": "Operations"},

    # === CHIẾN LƯỢC & HỌC HỎI ===
    "innovation":           {"value": 61, "label": "Đổi mới sáng tạo",          "domain": "Strategy"},
    "learning_rate":        {"value": 65, "label": "Tốc độ học hỏi",            "domain": "Strategy"},
    "strategic_clarity":    {"value": 70, "label": "Rõ ràng chiến lược",        "domain": "Strategy"},
}

# Ma trận vướng víu: khi trục A thay đổi, toàn bộ trục khác đổi theo tức thì
# Đây là "coherent update" - không lan truyền từng bước, mà đồng thời hiển lộ
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


# ─────────────────────────────────────────────
#  QUANTUM ENGINE - Coherent Update
#  Khi 1 trục thay đổi → toàn bộ hiển lộ tức thì
#  KHÔNG lan truyền từng bước — tất cả là 1
# ─────────────────────────────────────────────
class QuantumEngine:
    def __init__(self, state):
        self.state = deepcopy(state)

    def coherent_update(self, axis: str, delta: float, reason: str = "") -> dict:
        """
        Nguyên lý cốt lõi: khi tác động trục 'axis' với biên độ 'delta',
        toàn bộ trục trong hệ thống cập nhật ĐỒNG THỜI (không qua từng bước).
        Đây là biểu hiện của 'tất cả là 1' trong mô hình vướng víu lượng tử.
        """
        if axis not in self.state:
            return {"error": f"Trục '{axis}' không tồn tại"}

        old_state = {k: v["value"] for k, v in self.state.items()}
        changes = {}

        # Tác động trực tiếp lên trục được chọn
        self.state[axis]["value"] = max(0, min(100, self.state[axis]["value"] + delta))
        changes[axis] = round(self.state[axis]["value"] - old_state[axis], 2)

        # Đồng thời hiển lộ toàn bộ các trục liên đới (1 lần duy nhất, không lặp bước)
        weights = ENTANGLEMENT_MATRIX.get(axis, {})
        for linked_axis, weight in weights.items():
            if linked_axis in self.state:
                entangled_delta = delta * weight * 0.6  # hệ số giảm chấn
                old_val = self.state[linked_axis]["value"]
                new_val = max(0, min(100, old_val + entangled_delta))
                self.state[linked_axis]["value"] = new_val
                if abs(new_val - old_val) > 0.1:
                    changes[linked_axis] = round(new_val - old_val, 2)

        return {
            "triggered_axis": axis,
            "delta": delta,
            "reason": reason,
            "coherent_changes": changes,
            "axes_affected": len(changes),
        }

    def balance_score(self) -> float:
        """
        Công thức cân bằng tổng thể:
        Balance = Avg(value) - risk_level*0.3 - operational_cost*0.2
        """
        vals = [v["value"] for v in self.state.values()]
        avg = sum(vals) / len(vals)
        risk_penalty = self.state["risk_level"]["value"] * 0.3
        cost_penalty = self.state["operational_cost"]["value"] * 0.2
        return round(avg - risk_penalty - cost_penalty, 2)

    def get_snapshot(self) -> dict:
        return {k: round(v["value"], 1) for k, v in self.state.items()}

    def get_by_domain(self) -> dict:
        domains = {}
        for k, v in self.state.items():
            d = v["domain"]
            if d not in domains:
                domains[d] = []
            domains[d].append({"axis": k, "label": v["label"], "value": round(v["value"], 1)})
        return domains


# ─────────────────────────────────────────────
#  QUANTUM CORE - Agent Chính (Điều hành)
# ─────────────────────────────────────────────
class QuantumCore:
    def __init__(self, engine: QuantumEngine):
        self.engine = engine
        self.history = []
        self.name = "QuantumCore"

    def act(self, axis: str, delta: float, reason: str = "") -> dict:
        result = self.engine.coherent_update(axis, delta, reason)
        event = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent": self.name,
            "action": f"Tác động [{axis}] delta={delta:+.1f}",
            "reason": reason,
            "axes_affected": result.get("axes_affected", 0),
            "balance_after": self.engine.balance_score(),
        }
        self.history.append(event)
        return result

    def quantum_balance_of(self, topic: str) -> dict:
        """
        Bước 1: Tìm tính cân bằng của bất kỳ chủ đề nào.
        Tính cân bằng = trạng thái mà thông tin âm và dương của chủ đề bằng nhau,
        tức điểm mà chủ đề đang ở trạng thái tự nhiên nhất.
        Trả về: các chiều thông tin (âm/dương) của chủ đề đó.
        """
        # Bản đồ ngữ nghĩa: từ chủ đề → các chiều cân bằng tự nhiên
        # Mỗi chủ đề có chiều dương (phát triển) và chiều âm (giới hạn/cân bằng)
        TOPIC_BALANCE_MAP = {
            # Lĩnh vực vật chất / khoa học
            "tau vu tru": {
                "positive": ["lực đẩy vs lực cản", "năng lượng vs khối lượng", "tốc độ vs an toàn"],
                "negative": ["chi phí vs lợi ích", "rủi ro vs khám phá", "thời gian vs nguồn lực"],
                "core_balance": "Lực đẩy = Lực cản + Trọng lực → điểm thoát khỏi quỹ đạo",
                "axes_map": {"innovation": 0.9, "risk_level": 0.7, "operational_cost": 0.8, "strategic_clarity": 0.85},
            },
            "bat dong san": {
                "positive": ["giá trị thực vs giá trị thị trường", "cung vs cầu", "vị trí vs tiện ích"],
                "negative": ["chi phí vs lợi nhuận", "rủi ro pháp lý vs lợi tức", "thanh khoản vs tăng giá"],
                "core_balance": "Giá trị thực = Thông tin giá trị thực tế → điểm khách mua",
                "axes_map": {"customer_value": 0.9, "cash_flow": 0.85, "risk_level": 0.7, "market_reach": 0.8},
            },
            "toan hoc": {
                "positive": ["số dương vs số âm", "vô cực vs điểm 0", "tăng vs giảm"],
                "negative": ["phức tạp vs đơn giản", "trừu tượng vs ứng dụng"],
                "core_balance": "Số âm + Số dương = 0 → điểm cân bằng vũ trụ",
                "axes_map": {"learning_rate": 0.95, "innovation": 0.9, "strategic_clarity": 0.85},
            },
            "con nguoi": {
                "positive": ["thể chất vs tinh thần", "cá nhân vs tập thể", "cho vs nhận"],
                "negative": ["nhu cầu vs nguồn lực", "tự do vs trách nhiệm"],
                "core_balance": "Cho = Nhận → điểm phát triển bền vững",
                "axes_map": {"people_growth": 0.95, "culture": 0.9, "leadership": 0.85, "learning_rate": 0.8},
            },
        }

        # Tìm chủ đề gần nhất (fuzzy match đơn giản)
        topic_clean = topic.lower().replace(" ", "_").replace("ư", "u").replace("ữ", "u").replace("ụ", "u").replace("â", "a").replace("ấ", "a").replace("ầ", "a").replace("ộ", "o").replace("ổ", "o").replace("ố", "o").replace("đ", "d").replace("ê", "e").replace("ế", "e")
        matched = None
        for key in TOPIC_BALANCE_MAP:
            key_clean = key.replace(" ", "_")
            if key_clean in topic_clean or topic_clean in key_clean or any(w in topic_clean for w in key_clean.split("_")):
                matched = key
                break

        if matched:
            balance_info = TOPIC_BALANCE_MAP[matched]
        else:
            # Tự động suy ra tính cân bằng cho bất kỳ chủ đề nào
            balance_info = {
                "positive": [f"phát triển {topic}", f"giá trị {topic}", f"tiềm năng {topic}"],
                "negative": [f"giới hạn {topic}", f"rủi ro {topic}", f"chi phí {topic}"],
                "core_balance": f"Giá trị thực {topic} = Thông tin giá trị thực tế {topic}",
                "axes_map": {k: round(random.uniform(0.6, 0.95), 2) for k in random.sample(list(self.engine.state.keys()), 6)},
            }

        return balance_info

    def quantum_entangle_n(self, topic: str, balance_info: dict, rounds: int = 3) -> list:
        """
        Bước 2: Từ tính cân bằng của 1 chủ đề → N thông tin hiển lộ đồng thời.
        Lặp 'rounds' vòng: mỗi vòng, thông tin mới lại kích hoạt thông tin tiếp theo.
        Đây là 'có qua có lại vô hạn' — mỗi vòng là 1 lớp hiển lộ sâu hơn.
        """
        sim_engine = QuantumEngine(self.engine.state)
        all_revelations = []
        axes_map = balance_info["axes_map"]

        for round_num in range(1, rounds + 1):
            round_revelations = {}
            snap_before = sim_engine.balance_score()

            # Tác động đồng thời tất cả trục liên đới (coherent, không từng bước)
            for axis, weight in axes_map.items():
                if axis in sim_engine.state:
                    delta = round(weight * 10 * (1 / round_num), 2)  # giảm dần mỗi vòng
                    old_val = sim_engine.state[axis]["value"]
                    new_val = max(0, min(100, old_val + delta))
                    sim_engine.state[axis]["value"] = new_val
                    if abs(new_val - old_val) > 0.1:
                        round_revelations[axis] = {
                            "label": DEFAULT_STATE[axis]["label"],
                            "delta": round(new_val - old_val, 2),
                            "new_value": round(new_val, 1),
                        }

            snap_after = sim_engine.balance_score()
            all_revelations.append({
                "round": round_num,
                "label": f"Lớp hiển lộ {round_num}: {'Tác động gốc' if round_num == 1 else 'Phản hồi lại' if round_num == 2 else 'Cộng hưởng sâu'}",
                "revelations": round_revelations,
                "balance_delta": round(snap_after - snap_before, 3),
                "total_balance": round(snap_after, 2),
            })

            # Vòng sau: trục nào vừa thay đổi sẽ kích hoạt trục liên đới của nó
            # Đây là "có qua có lại" — N thông tin tác động lẫn nhau
            new_axes = {}
            for axis in round_revelations:
                linked = ENTANGLEMENT_MATRIX.get(axis, {})
                for linked_axis, w in linked.items():
                    if linked_axis not in axes_map:
                        new_axes[linked_axis] = round(w * 0.5, 2)
            axes_map = {**axes_map, **new_axes}  # mở rộng mạng lưới mỗi vòng

        return all_revelations

    def create_idea(self, topic: str) -> dict:
        """
        Sáng tạo theo đúng lý thuyết vướng víu lượng tử:
        1. Tìm tính cân bằng của chủ đề
        2. Tác động → N thông tin đồng thời hiển lộ
        3. Có qua có lại vô hạn (3 vòng mô phỏng)
        4. Tổng hợp thành ý tưởng hành động cụ thể
        """
        balance_info = self.quantum_balance_of(topic)
        revelations = self.quantum_entangle_n(topic, balance_info, rounds=3)

        # Tổng hợp tất cả trục đã hiển lộ qua 3 vòng
        all_axes_revealed = {}
        for r in revelations:
            for axis, info in r["revelations"].items():
                if axis not in all_axes_revealed:
                    all_axes_revealed[axis] = info
                else:
                    all_axes_revealed[axis]["delta"] += info["delta"]

        total_balance_gain = sum(r["balance_delta"] for r in revelations)

        # Sinh ra ý tưởng hành động từ các trục hiển lộ
        top_axes = sorted(all_axes_revealed.items(), key=lambda x: x[1]["delta"], reverse=True)[:5]
        action_ideas = []
        for axis, info in top_axes:
            action_ideas.append(f"Phát triển [{info['label']}] ({info['delta']:+.1f}) → tác động lan ra toàn hệ")

        return {
            "topic": topic,
            "core_balance": balance_info["core_balance"],
            "positive_dims": balance_info["positive"],
            "negative_dims": balance_info["negative"],
            "revelation_rounds": revelations,
            "total_axes_revealed": len(all_axes_revealed),
            "total_balance_gain": round(total_balance_gain, 3),
            "action_ideas": action_ideas,
            "verdict": "✅ Tính cân bằng dương — khuyến nghị phát triển" if total_balance_gain > 0 else "⚠️ Cần điều chỉnh trục gốc",
        }

    def daily_plan(self) -> dict:
        """Tạo kế hoạch ngày dựa trên trạng thái hiện tại"""
        snap = self.engine.get_by_domain()
        plans = {}
        for domain, axes in snap.items():
            weakest = min(axes, key=lambda x: x["value"])
            strongest = max(axes, key=lambda x: x["value"])
            plans[domain] = {
                "focus": f"Nâng [{weakest['label']}] ({weakest['value']:.0f}/100)",
                "leverage": f"Dùng [{strongest['label']}] ({strongest['value']:.0f}/100) làm đòn bẩy",
                "action": self._suggest_action(domain, weakest["axis"]),
            }
        return plans

    def _suggest_action(self, domain: str, weak_axis: str) -> str:
        actions = {
            "HR": "Tổ chức 1-on-1 coaching, đặt OKR rõ ràng cho từng người",
            "Sales": "Review pipeline, tập trung vào top 20% khách tiềm năng",
            "Marketing": "Chạy nội dung educate + retargeting khách cũ",
            "Finance": "Rà soát chi phí cố định, tăng tốc thu hồi công nợ",
            "Operations": "Audit quy trình bottleneck, áp dụng cải tiến ngay",
            "Strategy": "Workshop chiến lược 2h, cập nhật roadmap quý",
        }
        return actions.get(domain, "Phân tích dữ liệu và đề xuất hành động cụ thể")

    def get_history(self) -> list:
        return self.history[-20:]  # 20 sự kiện gần nhất


# ─────────────────────────────────────────────
#  QUANTUM AUDITOR - Agent Phụ (Giám sát & Báo cáo)
# ─────────────────────────────────────────────
class QuantumAuditor:
    def __init__(self, engine: QuantumEngine, core: QuantumCore):
        self.engine = engine
        self.core = core
        self.name = "QuantumAuditor"
        self.alerts = []

    def audit(self) -> dict:
        """Kiểm tra toàn bộ hệ thống và báo cáo"""
        snap = self.engine.get_snapshot()
        self.alerts = []

        # Kiểm tra ngưỡng
        for axis, rule in THRESHOLDS.items():
            val = snap.get(axis, 50)
            if "max" in rule and val > rule["max"]:
                self.alerts.append(f"🔴 {rule['label']}: {axis}={val:.0f} (max={rule['max']})")
            if "min" in rule and val < rule["min"]:
                self.alerts.append(f"🔴 {rule['label']}: {axis}={val:.0f} (min={rule['min']})")

        balance = self.engine.balance_score()
        health = "🟢 TỐT" if balance >= 50 else ("🟡 CẦN CHÚ Ý" if balance >= 35 else "🔴 NGUY HIỂM")

        # Tìm trục yếu nhất và mạnh nhất
        sorted_axes = sorted(snap.items(), key=lambda x: x[1])
        weakest = sorted_axes[:3]
        strongest = sorted_axes[-3:]

        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "health": health,
            "balance_score": balance,
            "alerts": self.alerts if self.alerts else ["✅ Không có cảnh báo"],
            "weakest_axes": [(k, round(v, 1)) for k, v in weakest],
            "strongest_axes": [(k, round(v, 1)) for k, v in strongest],
            "total_actions": len(self.core.history),
        }

    def full_report(self) -> str:
        """Tạo báo cáo đầy đủ cho chủ doanh nghiệp"""
        audit = self.audit()
        by_domain = self.engine.get_by_domain()
        daily = self.core.daily_plan()

        lines = []
        lines.append("=" * 60)
        lines.append("  BÁO CÁO QUANTUM AUDITOR")
        lines.append(f"  {audit['timestamp']}")
        lines.append("=" * 60)
        lines.append(f"\nSỨC KHỎE HỆ THỐNG: {audit['health']}")
        lines.append(f"ĐIỂM CÂN BẰNG TỔNG: {audit['balance_score']}/100")
        lines.append(f"TỔNG SỐ HÀNH ĐỘNG ĐÃ THỰC HIỆN: {audit['total_actions']}")

        lines.append("\n── CẢNH BÁO ──────────────────────────────")
        for a in audit["alerts"]:
            lines.append(f"  {a}")

        lines.append("\n── TÌNH TRẠNG TỪNG PHÒNG BAN ─────────────")
        for domain, axes in by_domain.items():
            avg = sum(a["value"] for a in axes) / len(axes)
            status = "🟢" if avg >= 65 else ("🟡" if avg >= 50 else "🔴")
            lines.append(f"\n  {status} {domain} (TB: {avg:.0f}/100)")
            for a in axes:
                bar = "█" * int(a["value"] / 10) + "░" * (10 - int(a["value"] / 10))
                lines.append(f"     {bar} {a['label']}: {a['value']}")

        lines.append("\n── KẾ HOẠCH NGÀY (ĐỀ XUẤT CỦA QuantumCore) ─")
        for domain, plan in daily.items():
            lines.append(f"\n  [{domain}]")
            lines.append(f"    Focus : {plan['focus']}")
            lines.append(f"    Đòn bẩy: {plan['leverage']}")
            lines.append(f"    Hành động: {plan['action']}")

        lines.append("\n── TRỤC YẾU NHẤT CẦN CẢI THIỆN ──────────")
        for axis, val in audit["weakest_axes"]:
            label = DEFAULT_STATE.get(axis, {}).get("label", axis)
            lines.append(f"  ⚠️  {label}: {val}/100")

        lines.append("\n── TRỤC MẠNH NHẤT - ĐÒN BẨY ──────────────")
        for axis, val in audit["strongest_axes"]:
            label = DEFAULT_STATE.get(axis, {}).get("label", axis)
            lines.append(f"  💪 {label}: {val}/100")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


# ─────────────────────────────────────────────
#  GIAO DIỆN CHẠY
# ─────────────────────────────────────────────
def run_demo(core, auditor):
    print("\n🌀 QUANTUM COMPANY AGENT — DEMO\n")
    events = [
        ("people_growth",        +12, "Tuyển được 3 nhân sự giỏi"),
        ("sales_performance",    +8,  "Đội sales vượt target tháng"),
        ("risk_level",           +18, "Phát sinh tranh chấp hợp đồng"),
        ("innovation",           +10, "Ra mắt sản phẩm mới"),
        ("operational_cost",     +15, "Chi phí logistics tăng đột biến"),
        ("leadership",           +9,  "CEO hoàn thành chương trình đào tạo"),
    ]
    for axis, delta, reason in events:
        print(f"\n⚡ SỰ KIỆN: {reason}")
        result = core.act(axis, delta, reason)
        print(f"   Trục tác động: [{axis}] {delta:+.0f}")
        print(f"   Số trục đồng thời hiển lộ: {result['axes_affected']}")
        print(f"   Điểm cân bằng sau: {core.engine.balance_score():.1f}/100")

    print("\n" + auditor.full_report())


def run_interactive(core, auditor):
    axes_list = list(DEFAULT_STATE.keys())
    print("\n🌀 QUANTUM COMPANY AGENT — INTERACTIVE")
    print("Lệnh: <trục> <delta> <lý do>  |  status  |  create <chủ đề>  |  report  |  axes  |  quit\n")

    while True:
        try:
            cmd = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        if cmd.lower() == "quit":
            break

        elif cmd.lower() == "status":
            audit = auditor.audit()
            print(f"\n  Sức khỏe: {audit['health']}  |  Balance: {audit['balance_score']}")
            for a in audit["alerts"]:
                print(f"  {a}")

        elif cmd.lower() == "report":
            print(auditor.full_report())

        elif cmd.lower() == "axes":
            for k, v in DEFAULT_STATE.items():
                val = core.engine.state[k]["value"]
                print(f"  {k:<25} {v['label']:<25} {val:.0f}/100  [{v['domain']}]")

        elif cmd.lower().startswith("create "):
            topic = cmd[7:].strip()
            result = core.create_idea(topic)
            print(f"\n{'='*55}")
            print(f"  TÍNH CÂN BẰNG CỦA: '{topic}'")
            print(f"{'='*55}")
            print(f"  Cân bằng cốt lõi: {result['core_balance']}")
            print(f"\n  Chiều dương (+): {' | '.join(result['positive_dims'])}")
            print(f"  Chiều âm  (-) : {' | '.join(result['negative_dims'])}")
            print(f"\n── N THÔNG TIN HIỂN LỘ QUA CÁC VÒNG ─────────────")
            for r in result["revelation_rounds"]:
                print(f"\n  {r['label']} (Balance {r['balance_delta']:+.3f})")
                for axis, info in list(r["revelations"].items())[:5]:
                    arrow = "↗" if info["delta"] > 0 else "↘"
                    print(f"    {arrow} {info['label']}: {info['delta']:+.1f} → {info['new_value']}/100")
            print(f"\n── TỔNG KẾT ───────────────────────────────────────")
            print(f"  Số thông tin hiển lộ : {result['total_axes_revealed']} trục")
            print(f"  Tổng Balance gain    : {result['total_balance_gain']:+.3f}")
            print(f"  Kết luận             : {result['verdict']}")
            print(f"\n── Ý TƯỞNG HÀNH ĐỘNG TỪ CÁC TRỤC HIỂN LỘ ────────")
            for idea in result["action_ideas"]:
                print(f"  → {idea}")
            print()

        else:
            parts = cmd.split(None, 2)
            if len(parts) >= 2:
                axis = parts[0]
                try:
                    delta = float(parts[1])
                    reason = parts[2] if len(parts) > 2 else ""
                    if axis not in DEFAULT_STATE:
                        print(f"  ❌ Trục '{axis}' không tồn tại. Gõ 'axes' để xem danh sách.")
                    else:
                        result = core.act(axis, delta, reason)
                        print(f"  ✅ Đã cập nhật: {result['axes_affected']} trục đồng thời hiển lộ")
                        print(f"  Balance: {core.engine.balance_score():.1f}/100")
                        for changed_axis, change in list(result["coherent_changes"].items())[:5]:
                            label = DEFAULT_STATE[changed_axis]["label"]
                            print(f"    {'↗' if change > 0 else '↘'} {label}: {change:+.1f}")
                except ValueError:
                    print("  ❌ Cú pháp: <trục> <số> <lý do>")
            else:
                print("  ❌ Không hiểu lệnh. Gõ 'status', 'report', 'axes', 'create <chủ đề>', hoặc '<trục> <delta>'")


def run_report(core, auditor):
    print(auditor.full_report())


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantum Company Agent")
    parser.add_argument("--mode", choices=["demo", "interactive", "report"], default="demo")
    args = parser.parse_args()

    engine = QuantumEngine(DEFAULT_STATE)
    core = QuantumCore(engine)
    auditor = QuantumAuditor(engine, core)

    if args.mode == "demo":
        run_demo(core, auditor)
    elif args.mode == "interactive":
        run_interactive(core, auditor)
    elif args.mode == "report":
        run_report(core, auditor)
