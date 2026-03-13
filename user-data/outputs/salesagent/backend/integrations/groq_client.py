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

async def detect_language(message: str) -> str:
    """Detect what language the lead wrote in."""
    system = "You are a language detection expert. Reply with ONLY the language name in English (e.g., 'Hindi', 'Marathi', 'English')."
    user = f"Identify the language of this message: '{message}'"
    
    lang = await call_groq(system, user, max_tokens=10)
    return lang.strip().replace(".", "")

async def research_lead_prompt(name: str, phone: str, message: str, source: str, language: str = "English", company_context: str = "") -> str:
    """Research the lead, responding in their detected language using Groq."""
    system = f"""You are a sales intelligence assistant. 
Company Context: {company_context}
Your job is to analyse an incoming lead and write a concise research summary.
Respond in {language}. Use simple, friendly language appropriate for the detected language.
Be practical and honest. Keep your response to 3-4 sentences maximum."""

    user = f"""Incoming lead details:
Name: {name}
Phone: {phone}
Source: {source}
Message: "{message}"

Based on this information, summarise who this person is and what they want."""

    return await call_groq(system, user)

async def generate_scoring_insights(outcomes_history: list) -> str:
    """Analyse past won/lost leads and write scoring tips."""
    system = """You are a sales strategy consultant. 
Analyse the provided history of 'won' and 'lost' leads.
Identify patterns: What signals indicate a high-quality lead? What signals indicate a waste of time?
Write 3-4 concise, bulleted 'Scoring Tips' for an AI agent to use in future scoring.
Focus on source, message content, and intent."""

    user = f"Lead Outcome History:\n{json.dumps(outcomes_history, indent=2, default=str)}\n\nWrite 3-4 scoring tips based on this data."
    
    return await call_groq(system, user)

async def score_lead_prompt(name: str, message: str, source: str, research_summary: str, language: str = "English", company_context: str = "", scoring_tips: str = "") -> dict:
    """Score the lead and provide reasoning/message in the detected language using Groq."""
    tips_section = f"Past Performance Scoring Tips:\n{scoring_tips}" if scoring_tips else ""
    
    system = f"""You are a lead scoring assistant. Respond in {language}.
Company Context: {company_context}
{tips_section}

You MUST respond with ONLY valid JSON. No markdown.

JSON format:
{{
  "score": <integer 1-10>,
  "reason": "<2-3 sentence explanation in {language}>",
  "suggested_message": "<personalised outreach message in {language}, friendly tone>"
}}"""

    user = f"""Lead info:
Name: {name}
Source: {source}
Message: "{message}"
Research summary: {research_summary}

Score this lead and write a personalised outreach message."""

    raw = await call_groq(system, user)

    try:
        cleaned = raw.strip().strip("```json").strip("```").strip()
        return json.loads(cleaned)
    except Exception:
        return {
            "score": 5,
            "reason": f"AI response parsing failed. Review manually.",
            "suggested_message": f"Hi {name}, thanks for reaching out! We'd love to connect and discuss how we can help."
        }
