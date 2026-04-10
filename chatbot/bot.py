"""
AgroCure - Farmer Chatbot Engine
Rule-based NLP chatbot with optional Gemini/OpenAI LLM upgrade fallback
"""

import json
import random
import os
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# LOAD INTENTS
# ─────────────────────────────────────────────────────────────────────────────

INTENTS_PATH = Path(__file__).parent / "intents.json"

with open(INTENTS_PATH, "r") as f:
    INTENTS_DATA = json.load(f)

INTENTS = INTENTS_DATA["intents"]


# ─────────────────────────────────────────────────────────────────────────────
# RULE-BASED MATCHING
# ─────────────────────────────────────────────────────────────────────────────

def match_intent(query: str) -> Optional[dict]:
    """
    Matches user query to closest intent using keyword matching.
    Returns matched intent dict or None.
    """
    query_lower = query.lower().strip()

    best_match = None
    best_score = 0

    for intent in INTENTS:
        if intent["tag"] == "fallback":
            continue
        for pattern in intent["patterns"]:
            # Score = number of pattern words found in query
            pattern_words = pattern.lower().split()
            matches = sum(1 for word in pattern_words if word in query_lower)
            score = matches / len(pattern_words) if pattern_words else 0

            # Boost for exact substring match
            if pattern.lower() in query_lower:
                score += 0.5

            if score > best_score:
                best_score = score
                best_match = intent

    # Minimum threshold to count as a match
    if best_score >= 0.4:
        return best_match
    return None


def get_rule_based_response(query: str) -> dict:
    """
    Returns a rule-based chatbot response.
    """
    intent = match_intent(query)

    if intent:
        response = random.choice(intent["responses"])
        return {
            "response": response,
            "intent": intent["tag"],
            "source": "rule_based",
            "confidence": "matched",
        }
    else:
        fallback = next(i for i in INTENTS if i["tag"] == "fallback")
        return {
            "response": random.choice(fallback["responses"]),
            "intent": "fallback",
            "source": "rule_based",
            "confidence": "fallback",
        }


# ─────────────────────────────────────────────────────────────────────────────
# LLM UPGRADE (OPTIONAL - plug in your API key to activate)
# ─────────────────────────────────────────────────────────────────────────────

def get_llm_response(
    query: str,
    context: Optional[dict] = None,  # disease context from recent scan
) -> dict:
    """
    LLM-powered response using Google Gemini or OpenAI.

    ╔══════════════════════════════════════════════════════╗
    ║  TODO: Add your Gemini or OpenAI API key here        ║
    ║  Set env var: GEMINI_API_KEY or OPENAI_API_KEY       ║
    ╚══════════════════════════════════════════════════════╝

    Args:
        query: Farmer's question
        context: Optional disease detection result to inject

    Returns:
        dict with response text and source
    """

    # ── Gemini path ──────────────────────────────────────────────────────────
    gemini_key = os.getenv("AIzaSyDRM7bGUi4WT-8whagdfZhilI1jGE5d5oE")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-pro")

            system_context = """You are AgroCure's AI farming assistant for Indian farmers.
You give concise, practical advice about crop diseases, treatments, and farming practices.
Always suggest both chemical and organic options. Use simple language.
Keep answers under 100 words. Do not mention AI or technology."""

            if context:
                system_context += f"""
Current scan context:
- Crop: {context.get('crop', 'Unknown')}
- Disease detected: {context.get('disease', 'None')}
- Severity: {context.get('severity', 'Unknown')}
Answer the farmer's question in context of this diagnosis."""

            full_prompt = f"{system_context}\n\nFarmer asks: {query}"
            response = model.generate_content(full_prompt)
            return {
                "response": response.text,
                "intent": "llm_gemini",
                "source": "gemini",
                "confidence": "llm",
            }
        except Exception as e:
            pass  # Fall through to rule-based

    # ── OpenAI path ──────────────────────────────────────────────────────────
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)

            messages = [
                {
                    "role": "system",
                    "content": "You are AgroCure's AI farming assistant for Indian farmers. Give concise practical advice. Always include both chemical and organic options. Keep responses under 100 words.",
                },
            ]

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context: Crop={context.get('crop')}, Disease={context.get('disease')}, Severity={context.get('severity')}",
                })

            messages.append({"role": "user", "content": query})

            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
            )
            return {
                "response": resp.choices[0].message.content,
                "intent": "llm_openai",
                "source": "openai",
                "confidence": "llm",
            }
        except Exception as e:
            pass  # Fall through to rule-based

    # ── No LLM available → fallback to rule-based ────────────────────────────
    return get_rule_based_response(query)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CHAT FUNCTION (used by API)
# ─────────────────────────────────────────────────────────────────────────────

def chat(query: str, context: Optional[dict] = None, use_llm: bool = True) -> dict:
    """
    Main entry point for chatbot.
    Tries LLM first (if configured), falls back to rule-based.
    """
    if not query or not query.strip():
        return {
            "response": "Please type a question! I'm here to help with your crops. 🌿",
            "intent": "empty",
            "source": "system",
        }

    if use_llm:
        return get_llm_response(query, context)
    else:
        return get_rule_based_response(query)
