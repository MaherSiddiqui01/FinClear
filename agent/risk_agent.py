# agent/risk_agent.py

def risk_score(days, amount):
    score = 0

    # Overdue Days Risk
    if days > 60:
        score += 60
    elif days > 30:
        score += 45
    elif days > 15:
        score += 25
    elif days > 7:
        score += 10

    # Amount Risk
    if amount > 200000:
        score += 40
    elif amount > 100000:
        score += 30
    elif amount > 50000:
        score += 20
    elif amount > 20000:
        score += 10

    return min(score, 100)