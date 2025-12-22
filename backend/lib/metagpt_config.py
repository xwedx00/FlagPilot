"""
MetaGPT Configuration Helper
=============================
Generates proper config2.yaml for MetaGPT with OpenRouter integration.
"""

import os
from pathlib import Path
from typing import Optional


METAGPT_CONFIG_TEMPLATE = """# MetaGPT Configuration - Auto-generated
# ========================================
# Using OpenRouter API for LLM calls

llm:
  api_type: "openai"
  base_url: "{base_url}"
  api_key: "{api_key}"
  model: "{model}"
  timeout: 300
  max_token: 4096
  temperature: 0.3
  stream: false

# Repair malformed LLM output
repair_llm_output: true

# Disable search
search:
  api_type: "google"
  api_key: "placeholder"
  cse_id: "placeholder"
"""


def create_metagpt_config(
    api_key: str,
    model: str,
    base_url: str = "https://openrouter.ai/api/v1"
) -> str:
    """Generate MetaGPT config2.yaml content with actual values"""
    return METAGPT_CONFIG_TEMPLATE.format(
        api_key=api_key,
        model=model,
        base_url=base_url
    )


def ensure_metagpt_config(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> Path:
    """
    Ensure MetaGPT config2.yaml exists with current settings.
    Creates/updates ~/.metagpt/config2.yaml with OpenRouter credentials.
    
    Returns: Path to the config file
    """
    from config import settings
    
    api_key = api_key or settings.OPENROUTER_API_KEY
    model = model or settings.OPENROUTER_MODEL
    base_url = base_url or settings.OPENROUTER_BASE_URL
    
    # MetaGPT looks for config in ~/.metagpt/
    config_dir = Path.home() / ".metagpt"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = config_dir / "config2.yaml"
    
    # Generate and write config
    config_content = create_metagpt_config(api_key, model, base_url)
    config_path.write_text(config_content)
    
    return config_path


def configure_metagpt_environment():
    """
    Set environment variables for MetaGPT.
    Call this before importing metagpt modules.
    """
    from config import settings
    
    # Set project root so MetaGPT looks for config in right place
    os.environ["METAGPT_PROJECT_ROOT"] = "/app"
    
    # Also set OpenAI-compatible env vars as fallback
    os.environ["OPENAI_API_KEY"] = settings.OPENROUTER_API_KEY
    os.environ["OPENAI_API_BASE"] = settings.OPENROUTER_BASE_URL
    
    # Ensure config file exists
    return ensure_metagpt_config()
