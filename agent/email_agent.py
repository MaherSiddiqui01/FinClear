from agent.llm import ask_llm

def generate_email(name, amount, days, stage):
    
    prompt = f"""
    Write a professional payment reminder email.

    Client: {name}
    Amount: ₹{amount}
    Overdue Days: {days}
    Escalation Stage: {stage}

    Tone:
    1 = polite
    2 = firm
    3 = urgent
    4 = final warning

    Keep concise.
    """

    return ask_llm(prompt)