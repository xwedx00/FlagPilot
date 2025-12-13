
from contextvars import ContextVar
from typing import Optional

# Context variable to store the current user ID
# This allows deep functions (like patched LLMs) to know which user triggered the request
# without passing user_id through every single function signature.
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
