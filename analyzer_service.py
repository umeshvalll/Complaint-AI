import google.generativeai as genai

def analyze_complaint(user_message):

    prompt = f"""
Analyze this customer complaint.

Complaint:
{user_message}

Return ONLY in this exact format:

Category: <Technical/Billing/Delivery/General>
Sentiment: <Positive/Neutral/Negative/Very Negative>
Priority: <Low/Medium/High>
"""

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    try:

        response = model.generate_content(
            prompt
        )

        result = response.text

    except Exception:

        result = ""

    category = "General"
    sentiment = "Neutral"
    priority = "Medium"

    lines = result.split("\n")

    for line in lines:

        line = line.strip()

        if "Category" in line:
            category = (
                line.split(":")[-1]
                .strip()
            )

        elif "Sentiment" in line:
            sentiment = (
                line.split(":")[-1]
                .strip()
            )

        elif "Priority" in line:
            priority = (
                line.split(":")[-1]
                .strip()
            )

    title = (
        user_message[:50]
        .strip()
    )

    return {
        "title": title,
        "category": category,
        "sentiment": sentiment,
        "priority": priority
    }