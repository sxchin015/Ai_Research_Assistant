import os
import logging
from groq import Groq
from config.config import GROQ_MODEL, MODE_CONCISE, SYSTEM_PROMPT_CONCISE, SYSTEM_PROMPT_DETAILED

logger = logging.getLogger(__name__)


def _client():
    # Read key fresh every time — picks up keys pasted in the UI
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY is not set. Paste your key in the sidebar.")
    return Groq(api_key=key)


def _messages(query, context, system_prompt):
    user_content = query
    if context.strip():
        user_content = f"Context:\n---\n{context}\n---\n\nQuestion: {query}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_content},
    ]


def get_llm_response(query, context="", mode=MODE_CONCISE):
    try:
        system_prompt = SYSTEM_PROMPT_CONCISE if mode == MODE_CONCISE else SYSTEM_PROMPT_DETAILED
        response = _client().chat.completions.create(
            model=GROQ_MODEL,
            messages=_messages(query, context, system_prompt),
            temperature=0.3,
            max_tokens=300 if mode == MODE_CONCISE else 1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("Groq error: %s", exc)
        raise RuntimeError(f"LLM error: {exc}") from exc


def stream_llm_response(query, context="", mode=MODE_CONCISE):
    try:
        system_prompt = SYSTEM_PROMPT_CONCISE if mode == MODE_CONCISE else SYSTEM_PROMPT_DETAILED
        stream = _client().chat.completions.create(
            model=GROQ_MODEL,
            messages=_messages(query, context, system_prompt),
            temperature=0.3,
            max_tokens=300 if mode == MODE_CONCISE else 1200,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        logger.error("Groq streaming error: %s", exc)
        raise RuntimeError(f"LLM streaming error: {exc}") from exc
