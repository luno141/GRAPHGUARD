"""
AI Risk Scoring Engine for GraphGuard AI.

Takes graph signals and produces a weighted fraud risk score (0-100)
with human-readable explanations.
"""

from models import RiskSignals


# Weight configuration for risk factors
WEIGHTS = {
    "shared_device": 20,        # Per shared device user
    "shared_phone": 25,         # Per shared phone user  
    "money_loop": 30,           # If in a circular money transfer
    "flagged_connection": 15,   # Per connected flagged user
    "high_send_volume": 10,     # If sends to many users
    "already_flagged": 25,      # If user is already flagged
    "send_receive_ratio": 10,   # If suspicious ratio
}

MAX_SCORE = 100


def calculate_risk_score(signals: RiskSignals) -> tuple[int, str, list[str]]:
    """
    Calculate fraud risk score from graph signals.
    
    Returns:
        (score, risk_level, explanations)
    """
    score = 0
    explanations = []

    # Factor 1: Shared devices
    if signals.shared_device_count > 0:
        factor = min(signals.shared_device_count * WEIGHTS["shared_device"], 40)
        score += factor
        explanations.append(
            f"⚠️ Shares device(s) with {signals.shared_device_count} other user(s) — "
            f"common in coordinated fraud rings (+{factor} risk)"
        )

    # Factor 2: Shared phones
    if signals.shared_phone_count > 0:
        factor = min(signals.shared_phone_count * WEIGHTS["shared_phone"], 50)
        score += factor
        explanations.append(
            f"📱 Phone number shared with {signals.shared_phone_count} other account(s) — "
            f"strong indicator of synthetic identity fraud (+{factor} risk)"
        )

    # Factor 3: Money loop membership
    if signals.is_in_money_loop:
        factor = WEIGHTS["money_loop"]
        score += factor
        explanations.append(
            f"🔄 Involved in circular money transfer pattern — "
            f"characteristic of money laundering schemes (+{factor} risk)"
        )

    # Factor 4: Connected to flagged users
    flagged_count = len(signals.connected_flagged_users)
    if flagged_count > 0:
        factor = min(flagged_count * WEIGHTS["flagged_connection"], 30)
        score += factor
        explanations.append(
            f"🚩 Connected to {flagged_count} flagged/suspicious user(s) — "
            f"guilt by association signal (+{factor} risk)"
        )

    # Factor 5: High send volume
    if signals.sent_to_count > 3:
        factor = WEIGHTS["high_send_volume"]
        score += factor
        explanations.append(
            f"📤 Sent money to {signals.sent_to_count} different users — "
            f"unusually high fan-out pattern (+{factor} risk)"
        )

    # Factor 6: Already flagged
    if signals.is_flagged:
        factor = WEIGHTS["already_flagged"]
        score += factor
        explanations.append(
            f"🔴 User is already flagged in the system (+{factor} risk)"
        )

    # Factor 7: Send/receive ratio
    if signals.total_sent > 0 and signals.total_received > 0:
        ratio = signals.total_sent / signals.total_received
        if ratio > 3.0 or ratio < 0.3:
            factor = WEIGHTS["send_receive_ratio"]
            score += factor
            explanations.append(
                f"💰 Suspicious send/receive ratio ({ratio:.1f}x) — "
                f"may indicate pass-through account (+{factor} risk)"
            )

    # Cap at MAX_SCORE
    score = min(score, MAX_SCORE)

    # Determine risk level
    if score >= 75:
        risk_level = "CRITICAL"
    elif score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if not explanations:
        explanations.append("✅ No suspicious signals detected — user appears legitimate")

    return score, risk_level, explanations
