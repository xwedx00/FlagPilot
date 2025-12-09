#!/usr/bin/env python3
"""
FlagPilot Entry Point
======================
Sets MetaGPT environment variables BEFORE any imports.
"""

import os
import sys

# =============================================================================
# CRITICAL: Set MetaGPT environment variables BEFORE importing anything else
# =============================================================================


try:
    from config import settings
except ImportError:
    # If run as script, add current dir to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import settings

# Use settings from config.py which handles .env loading
_api_key = settings.OPENROUTER_API_KEY
_base_url = settings.OPENROUTER_BASE_URL
_model = settings.OPENROUTER_MODEL

# Set all the environment variables MetaGPT might read
settings.configure_metagpt_env()


# --- FIX: Generate config2.yaml to satisfy MetaGPT Config validation ---
# MetaGPT requires 'llm' field to exist in config file to initialize structure
try:
    metagpt_dir = os.path.expanduser("~/.metagpt")
    os.makedirs(metagpt_dir, exist_ok=True)
    config_path = os.path.join(metagpt_dir, "config2.yaml")
    
    with open(config_path, "w") as f:
        f.write("llm:\n")
        f.write('  api_type: "openai"\n')
        f.write(f'  model: "{_model}"\n')
        f.write(f'  base_url: "{_base_url}"\n')
        f.write(f'  api_key: "{_api_key}"\n')
    print(f"[Bootstrap] generated {config_path}")
except Exception as e:
    print(f"[Bootstrap] Failed to generate config2.yaml: {e}")
# -----------------------------------------------------------------------

print(f"[Bootstrap] API Key set: {bool(_api_key)} (length: {len(_api_key)})")
print(f"[Bootstrap] Model: {_model}")
print(f"[Bootstrap] OPENAI_API_KEY in env: {bool(os.environ.get('OPENAI_API_KEY'))}")

# =============================================================================
# Run uvicorn WITHOUT reload to avoid subprocess env issues
# In development, use docker-compose restart for code changes
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    # Disable reload - child process doesn't inherit env vars properly
    # For development: docker-compose restart backend
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
