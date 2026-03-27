"""
Base utilities shared by all agents: Claude API calls, JSON parsing, and
prompt loading from markdown files.
"""

import json
import re
import time

import anthropic

from config import MODEL, PROMPTS_DIR


def load_prompt(agent_name: str) -> str:
    """Load a system prompt from ``prompts/<agent_name>.md``."""
    path = PROMPTS_DIR / f"{agent_name}.md"
    return path.read_text(encoding="utf-8")


def parse_json_response(text: str) -> dict:
    """Multi-strategy JSON extraction from Claude's response text."""
    text = text.strip()
    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strategy 2: markdown code fences
    fence = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Strategy 3: outermost braces
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        try:
            return json.loads(text[i : j + 1])
        except json.JSONDecodeError:
            pass
    return {"raw_text": text}


def call_agent(agent_name: str, system_prompt: str, user_prompt: str,
               max_retries: int = 3) -> dict:
    """Call Claude API with retry + exponential back-off + JSON extraction."""
    last_error = None
    for attempt in range(max_retries):
        try:
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return parse_json_response(resp.content[0].text)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
    return {"error": f"Agent {agent_name} failed after {max_retries} retries: {last_error}"}
