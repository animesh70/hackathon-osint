# preosint.py
from flask import Blueprint, request, jsonify
import re

preosint_bp = Blueprint("preosint", __name__)

@preosint_bp.route("/api/preosint/scan", methods=["POST"])
def scan_preosint():
    data = request.json or {}
    text = data.get("text", "").lower()
    username = data.get("username", "").lower()

    risk_score = 0
    risks = []
    recommendations = []

    # ---------- OSINT RULES ----------

    # Phone number
    if re.search(r"\b\d{10}\b", text):
        risk_score += 30
        risks.append("Phone number exposed")
        recommendations.append("Remove phone numbers before posting")

    # Email
    if re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", text):
        risk_score += 30
        risks.append("Email address exposed")
        recommendations.append("Avoid sharing email publicly")

    # Residence disclosure
    residence_phrases = [
        "i live in", "i stay in", "i am from",
        "based in", "resident of", "my hometown is"
    ]
    locations = [
        "cuttack", "odisha", "bhubaneswar",
        "delhi", "mumbai", "kolkata", "chennai"
    ]

    if any(p in text for p in residence_phrases) and any(l in text for l in locations):
        risk_score += 30
        risks.append("Residential location disclosed")
        recommendations.append("Avoid sharing where you live")

    # Real-time activity
    if any(t in text for t in ["today", "now", "currently", "right now"]):
        risk_score += 15
        risks.append("Real-time activity disclosed")
        recommendations.append("Avoid posting real-time updates")

    # Routine disclosure
    if any(r in text for r in ["every day", "daily", "every morning"]):
        risk_score += 25
        risks.append("Routine pattern disclosed")
        recommendations.append("Avoid sharing daily routines")

    # Username correlation
    if username and username in text:
        risk_score += 20
        risks.append("Username linked to content")
        recommendations.append("Avoid linking usernames with personal info")

    # ---------- FINAL RISK LEVEL ----------
    if risk_score >= 60:
        overall_risk = "HIGH"
    elif risk_score >= 30:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return jsonify({
        "risk_score": risk_score,
        "overall_risk": overall_risk,
        "identified_risks": risks,
        "recommendations": recommendations
    })
