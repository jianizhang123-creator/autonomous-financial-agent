"""
Shared configuration for the Autonomous Financial Agent.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
MEMORY_FILE = DATA_DIR / "memory.json"
MODEL = "claude-haiku-4-5-20251001"
