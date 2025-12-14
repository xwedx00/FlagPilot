
"""
Contract Guardian - Legal Analysis Agent
"""

from typing import ClassVar
from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole, FlagPilotAction, AgentEvent
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class AnalyzeContract(FlagPilotAction):
    """Analyze legal contracts for risks and clauses"""
    
    name: str = "AnalyzeContract"
    desc: str = "Analyze legal documents for risks, non-competes, and IP rights."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Contract Guardian, a legal AI expert.
    
    Context from Knowledge Base (HIGHEST PRIORITY):
    {rag_context}
    
    Task:
    Analyze the contract-related query below. You MUST base your analysis heavily on the "Context from Knowledge Base" provided above.
    
    Query:
    {content}
    
    Instructions:
    1. EXTRACT EXACT NUMBERS: Look for specific values like "50% upfront", "$15,000", "30 days" in the Context. Quote them exactly.
    2. SCAM DETECTION: If the context identifies "Scam" or "Risk", echo that warning.
    3. If the "Context" contains specific payment terms (e.g. $15,000 project value), USE THEM. Do not hallucinate generic terms like "$120,000/year" unless explicitly in the context.
    
    Structure your answer as:
    1. Red Flags & Risks
    2. Payment Terms (Quote exact numbers from Context)
    3. Late Fees/Penalties (Based on Context)
    4. Recommendations
    
    Output strictly in VALID JSON format:
    {{
        "is_critical_risk": boolean,
        "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
        "risk_summary": "One sentence summary of the highest risk.",
        "override_instruction": "Actionable emergency instruction if risk is CRITICAL else empty string.",
        "analysis": "# Markdown Analysis Here..."
    }}
    """

    async def run(self, instruction: str, context: str = "", runtime_context: dict = None) -> str:
        # 1. Native Tool Use: Search RAG for relevant legal context
        rag_context = "No internal context found."
        try:
            # We search for keywords in the instruction to ground the analysis
            # Extract user_id from runtime_context if available
            user_id = runtime_context.get("id") or runtime_context.get("user_id") if runtime_context else None
            
            rag_context = await RAGSearch.search_knowledge_base(
                query=instruction[:100], 
                user_id=user_id,
                top_k=3
            )
        except Exception:
            pass # Fallback if RAG fails

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=rag_context
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)

class ContractGuardian(FlagPilotRole):
    """
    Contract Guardian Agent
    
    Watches for: User requests about contracts
    Actions: AnalyzeContract
    """
    
    name: str = "ContractGuardian"
    profile: str = "Senior Legal AI Analyst"
    goal: str = "Protect freelancers from unfair contracts"
    constraints: str = "Cite specific clauses. Be conservative in risk assessment."
    
    def __init__(self, **kwargs):
        # Initialize with specific action
        super().__init__(actions=[AnalyzeContract], **kwargs)
        
        # In a team environment, we might watch for specific triggers
        # For now, default watch is empty, set by Orchestrator or Team
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = AnalyzeContract()
        # Direct run
        return await action.run(instruction=text, context=str(context), runtime_context=context)
