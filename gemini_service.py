import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from config import Config


genai.configure(
    api_key=Config.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def get_support_reply(messages):

    try:

        conversation = ""

        for msg in messages:

            if msg["role"] == "user":
                conversation += (
                    f"Customer: {msg['text']}\n"
                )

            else:
                conversation += (
                    f"Assistant: {msg['text']}\n"
                )

        prompt = f"""
You are Complaint AI, an intelligent customer support assistant.

ROLE:
You are helping customers resolve complaints and create support tickets.

STRICT RULES:

1. Remember the entire conversation.
2. Never repeat questions that were already answered.
3. Ask at most TWO follow-up questions.
4. Give at most THREE troubleshooting steps.
5. Use simple English.
6. Keep responses under 120 words.
7. Use numbered lists.
8. Be empathetic and professional.
9. Do not ask unnecessary questions.
10. If the customer says:
   - Still not working
   - Not resolved
   - Same issue
   - No
   - Didn't work
   - Problem persists

Then STOP troubleshooting and ask:

Would you like me to create a complaint ticket?

11. Never ask more than one round of questions.
12. Never ask for information already available in the conversation.

RESPONSE FORMAT:

😊 I understand your issue.

Questions:

1. Question
2. Question

Things to Try:

1. Step
2. Step
3. Step

If the issue is unresolved:

Would you like me to create a complaint ticket?

Conversation:

{conversation}

Generate ONLY the next assistant response.
"""

        response = model.generate_content(
            prompt
        )

        reply = (
            response.text
            .strip()
        )

        return reply

    except ResourceExhausted:

        return (
            "⚠️ Too many requests were sent to Gemini.\n\n"
            "Please wait about one minute and try again."
        )

    except Exception as e:

        return (
            f"⚠️ AI Service Error:\n{str(e)}"
        )