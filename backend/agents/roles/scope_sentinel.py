"""
Scope Sentinel - Scope Creep Detection Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class DetectScopeCreep(FlagPilotAction):
    """Detect and prevent scope creep"""
    
    name: str = "DetectScopeCreep"
    desc: str = "Compare new requests against original SOW to identify scope creep."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Scope Sentinel, protecting freelancers from unpaid extra work.
    
    Original Agreement / SOW (RAG Context):
    {rag_context}
    
    New Request / Situation:
    {content}
    
    Analyze:
    1. IS THIS SCOPE CREEP? (Yes/No/Gray Area)
    2. IMPACT ANALYSIS (Cost/Time)
    3. RESPONSE SCRIPT (Diplomatically requesting change order or extra pay)
    
    Be firm but polite. "Freebies" set bad precedents.
    
    Output strictly in VALID JSON format:
    {{
        "is_critical_risk": boolean,
        "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
        "risk_summary": "One sentence summary of the highest risk (e.g. Unpaid features).",
        "override_instruction": "Actionable emergency instruction if risk is CRITICAL else empty string.",
        "analysis": "# Markdown Analysis Here...",
        "detected_scope_creep": boolean
    }}
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for the original SOW or project definition
        rag_context = "Original agreement not found in context."
        try:
            # We search for "SOW", "agreement", or project name references
            rag_context = RAGSearch.search_knowledge_base(
                query=f"project scope agreement SOW {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            # If explicit context (like uploaded SOW text) is passed, it overrides RAG
            rag_context=f"{rag_context}\n\nProvided Context: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ScopeSentinel(FlagPilotRole):
    """
    Scope Sentinel Agent
    Watches for: New task requests, "just one quick thing" messages
    """
    
    name: str = "ScopeSentinel"
    profile: str = "Scope Management Specialist"
    goal: str = "Protect freelancers from scope creep and ensure fair compensation"
    constraints: str = "Be firm but diplomatic, document everything, suggest fair pricing"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[DetectScopeCreep], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = DetectScopeCreep()
        return await action.run(instruction=text, context=str(context))
