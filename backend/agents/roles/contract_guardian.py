"""
Contract Guardian - Contract Analysis Agent
Uses MetaGPT Role for team orchestration
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class AnalyzeContract(Action):
    """Analyze contracts for risks and unfair terms"""
    
    name: str = "AnalyzeContract"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Contract Guardian, an expert contract analyst protecting freelancers.

Analyze this contract/agreement for:
1. HIGH RISK clauses (payment terms, IP rights, liability)
2. MEDIUM RISK items needing clarification
3. Missing standard protections
4. Unfair or one-sided terms
5. Hidden fees or penalties

Contract/Text to analyze:
{content}

Additional context:
{context}

Provide:
- RISK SCORE (1-10)
- DETAILED ANALYSIS with specific clause references
- NEGOTIATION SUGGESTIONS
- RED FLAGS to address immediately
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ContractGuardian(Role):
    """Contract Guardian Agent - Analyzes contracts for risks"""
    
    name: str = "ContractGuardian"
    profile: str = "Contract Analysis Specialist"
    goal: str = "Identify risky contract terms and protect freelancers from unfair agreements"
    constraints: str = "Be thorough, cite specific clauses, provide actionable negotiation advice"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeContract])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        
        if msg:
            result = await todo.run(content=msg.content, context="")
        else:
            result = "No contract provided for analysis."
        
        return Message(
            content=result,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
        )
    
    async def analyze(self, text: str, context: dict = None) -> str:
        """Direct API method"""
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        action = AnalyzeContract()
        return await action.run(content=text, context=ctx)
