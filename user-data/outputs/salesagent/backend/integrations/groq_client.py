from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


async def call_groq(system: str, user: str, max_tokens: int = 1024) -> str:
    """Call Groq API and return the text response."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )
    return response.choices[0].message.content


async def research_lead_prompt(name: str, phone: str, message: str, source: str) -> str:
    """Ask Groq to research a lead based on available info."""
    system = """You are a sales intelligence assistant for a small business.
Your job is to analyse an incoming lead and write a concise research summary.
Be practical and honest — if there's little info, say so clearly.
Keep your response to 3-4 sentences maximum."""

    user = f"""Incoming lead details:
Name: {name}
Phone: {phone}
Source: {source}
Message: "{message}"

Based on this information, summarise:
1. Who this person likely is
2. What they are looking for
3. How serious they seem as a buyer"""

    return await call_groq(system, user)


async def score_lead_prompt(name: str, message: str, source: str, research_summary: str) -> dict:
    """Ask Groq to score the lead and return structured JSON."""
    system = """You are a lead scoring assistant. You MUST respond with ONLY valid JSON.
No preamble, no explanation, no markdown code blocks. Just raw JSON.

Scoring guide:
9-10: Clear purchase intent, decision maker, strong buying signals
7-8:  Interested, likely buyer, needs some nurturing
5-6:  Curious, unclear intent, worth a follow-up
3-4:  Low intent, possibly shopping around
1-2:  Spam, wrong audience, or very low quality

JSON format:
{
  "score": <integer 1-10>,
  "reason": "<2-3 sentence plain English explanation>",
  "suggested_message": "<personalised first outreach message, 2-3 sentences, friendly tone>"
}"""

    user = f"""Lead info:
Name: {name}
Source: {source}
Message: "{message}"

Research summary: {research_summary}

Score this lead and write a personalised outreach message."""

    raw = await call_groq(system, user)

    try:
        # Strip any accidental markdown fences
        cleaned = raw.strip().strip("```json").strip("```").strip()
        return json.loads(cleaned)
    except Exception:
        # Fallback if JSON parsing fails
        return {
            "score": 5,
            "reason": "Could not parse AI response. Manual review recommended.",
            "suggested_message": f"Hi {name}, thanks for reaching out! We'd love to learn more about what you're looking for. Can we connect for a quick call?"
        }
