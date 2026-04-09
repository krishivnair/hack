"""
AgroCure - Severity & Health Score Engine
Calculates disease severity from model confidence + health analytics
"""

from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# SEVERITY FROM CONFIDENCE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_severity(confidence: float, urgency_override: Optional[str] = None) -> dict:
    """
    Maps model confidence → severity level + action priority.

    Args:
        confidence: float 0.0–1.0 from ML model
        urgency_override: from disease_mapper urgency field (HIGH/MEDIUM/NONE)

    Returns:
        dict with level, label, color, action
    """
    if urgency_override == "NONE":
        return {
            "level": 0,
            "label": "Healthy",
            "color": "#22c55e",
            "badge": "✅ Healthy",
            "action": "No treatment needed. Continue regular monitoring.",
        }

    if confidence >= 0.90:
        severity = {
            "level": 3,
            "label": "Severe",
            "color": "#ef4444",
            "badge": "🔴 Severe",
            "action": "Immediate treatment required. Risk of total crop loss if untreated.",
        }
    elif confidence >= 0.70:
        severity = {
            "level": 2,
            "label": "Moderate",
            "color": "#f97316",
            "badge": "🟠 Moderate",
            "action": "Apply treatment within 48 hours to prevent spread.",
        }
    elif confidence >= 0.50:
        severity = {
            "level": 1,
            "label": "Mild",
            "color": "#eab308",
            "badge": "🟡 Mild",
            "action": "Monitor closely. Begin preventive treatment.",
        }
    else:
        severity = {
            "level": 0,
            "label": "Low Risk",
            "color": "#84cc16",
            "badge": "🟢 Low Risk",
            "action": "Low confidence detection. Recheck with a clearer image.",
        }

    # Escalate if disease mapper flagged HIGH urgency
    if urgency_override == "HIGH" and severity["level"] < 3:
        severity["level"] = min(severity["level"] + 1, 3)
        severity["action"] = f"[Urgency escalated] {severity['action']}"

    return severity


# ─────────────────────────────────────────────────────────────────────────────
# FARM HEALTH SCORE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_health_score(scan_results: list[dict]) -> dict:
    """
    Calculates overall farm health score from a batch of scan results.

    Args:
        scan_results: list of dicts, each with keys:
            - "disease": str (None if healthy)
            - "confidence": float

    Returns:
        dict with score (0–100), label, color, breakdown
    """
    if not scan_results:
        return {"score": 0, "label": "No Data", "color": "#6b7280", "breakdown": {}}

    total = len(scan_results)
    healthy_count = sum(1 for r in scan_results if r.get("disease") is None)
    infected_count = total - healthy_count

    score = round((healthy_count / total) * 100, 1)

    if score >= 70:
        label, color = "Healthy Farm", "#22c55e"
    elif score >= 40:
        label, color = "Moderate Risk", "#f97316"
    else:
        label, color = "Critical — Action Needed", "#ef4444"

    # Disease breakdown
    disease_counts: dict[str, int] = {}
    for r in scan_results:
        d = r.get("disease")
        if d:
            disease_counts[d] = disease_counts.get(d, 0) + 1

    return {
        "score": score,
        "label": label,
        "color": color,
        "total_scans": total,
        "healthy_count": healthy_count,
        "infected_count": infected_count,
        "breakdown": disease_counts,
    }


# ─────────────────────────────────────────────────────────────────────────────
# OUTBREAK RISK ENGINE
# ─────────────────────────────────────────────────────────────────────────────

OUTBREAK_THRESHOLDS = {
    "default": 0.30,       # 30% infection rate triggers alert
    "Late Blight": 0.15,   # Late blight spreads fast — lower threshold
    "Early Blight": 0.25,
    "Common Rust": 0.30,
}


def assess_outbreak_risk(scan_results: list[dict]) -> dict:
    """
    Assesses outbreak risk from a batch of scan results.

    Args:
        scan_results: list of dicts with 'disease' key

    Returns:
        dict with risk_level, alert, affected_disease, infection_rate
    """
    if not scan_results:
        return {"risk_level": "UNKNOWN", "alert": False, "details": "No data"}

    total = len(scan_results)
    disease_counts: dict[str, int] = {}

    for r in scan_results:
        d = r.get("disease")
        if d:
            disease_counts[d] = disease_counts.get(d, 0) + 1

    alerts = []
    for disease, count in disease_counts.items():
        infection_rate = count / total
        threshold = OUTBREAK_THRESHOLDS.get(disease, OUTBREAK_THRESHOLDS["default"])

        if infection_rate >= threshold:
            alerts.append({
                "disease": disease,
                "infection_rate": round(infection_rate * 100, 1),
                "threshold_pct": round(threshold * 100, 1),
                "count": count,
            })

    if not alerts:
        return {
            "risk_level": "LOW",
            "alert": False,
            "message": "No outbreak risk detected.",
            "alerts": [],
        }

    # Highest infection rate alert = primary
    primary = max(alerts, key=lambda x: x["infection_rate"])
    risk_level = "HIGH" if primary["infection_rate"] >= 50 else "MEDIUM"

    return {
        "risk_level": risk_level,
        "alert": True,
        "message": f"⚠️ Possible {primary['disease']} outbreak — {primary['infection_rate']}% of scanned crops infected.",
        "alerts": alerts,
    }
