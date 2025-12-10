
"""
Job Authenticator - Scam Detection Agent
"""

from typing import ClassVar
from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class AuthenticateJob(FlagPilotAction):
    """Detect fake job postings and scams"""
    
    name: str = "AuthenticateJob"
    desc: str = "Detect fake job postings and scams using known patterns and RAG context."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Job Authenticator, a scam detection expert.
    
    Known Scam Patterns (RAG Context):
    {rag_context}
    
    Analyze this job posting:
    {content}
    
    Identify:
    1. Red Flags (Unrealistic pay, telegram contact, generic Gmail)
    2. Yellow Flags (Vague description, urgent hiring)
    3. Payment Scams (Check fraud, equipment purchase)
    
    Provide a LEGITIMACY SCORE (1-10) and specific warnings.
    
    Output strictly in VALID JSON format:
    {{
        "is_critical_risk": boolean,
        "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
        "risk_summary": "One sentence summary of the highest risk.",
        "override_instruction": "Actionable emergency instruction if risk is CRITICAL else empty string.",
        "score": 5,
        "analysis": "# Markdown Analysis Here..."
    }}
    """
    
    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool Use: Search for similar scams or company reputation
        rag_context = "No internal context found."
        try:
            rag_context = RAGSearch.search_knowledge_base(query="common job scams " + instruction[:50], top_k=3)
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=rag_context
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)

class JobAuthenticator(FlagPilotRole):
    """
    Job Authenticator Agent
    Watches for: Job postings
    """
    
    name: str = "JobAuthenticator"
    profile: str = "Scam Detection Specialist"
    goal: str = "Protect freelancers from fake job postings"
    constraints: str = "Be vigilant. Assume potential scam until proven legit."
    
    def __init__(self, **kwargs):
        super().__init__(actions=[AuthenticateJob], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = AuthenticateJob()
        return await action.run(instruction=text, context=str(context))
