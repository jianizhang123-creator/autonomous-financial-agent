"""
Server-Sent Events (SSE) helpers for real-time agent progress streaming.
"""

import json


def sse_event(event_type: str, data: dict) -> str:
    """Format a single Server-Sent Event frame."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
