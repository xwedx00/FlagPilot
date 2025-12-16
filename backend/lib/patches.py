"""
MetaGPT Patches - Simplified
============================
Previously contained billing/cost tracking patches.
Now simplified since billing is handled by frontend.
"""

import logging

logger = logging.getLogger("uvicorn")


def apply_metagpt_patches():
    """
    Apply any necessary patches to MetaGPT.
    
    NOTE: Billing patches removed - cost tracking moved to frontend.
    This function is kept for backward compatibility.
    """
    logger.info("🔧 MetaGPT patches applied (cost tracking disabled)")

