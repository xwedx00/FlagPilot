"""
Payment Enforcer - Payment Collection Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class EnforcePayment(FlagPilotAction):
    """Create payment collection strategies"""
    
    name: str = "EnforcePayment"
    desc: str = "Analyze payment situations and provide collection strategies."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Payment Enforcer, an expert at helping freelancers collect overdue payments.
    
    Context from Knowledge Base (Templates/Legal):
    {rag_context}
    
    Analyze this payment situation:
    {content}
    
    Provide:
    1. SITUATION ASSESSMENT (Severity, leverage)
    2. RECOMMENDED APPROACH (Friendly reminder vs Formal demand)
    3. EMAIL TEMPLATES (Use RAG context if applicable)
    4. ESCALATION STEPS
    
    Maintain professionalism to preserve relationships unless the situation demands legal escalation.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for payment templates or legal demand letter examples
        rag_context = "No templates found."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"payment collection templates overdue invoice {instruction[:50]}", 
                top_k=2
            )
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


class PaymentEnforcer(FlagPilotRole):
    """
    Payment Enforcer Agent
    Watches for: Overdue invoice alerts or user requests about payment
    """
    
    name: str = "PaymentEnforcer"
    profile: str = "Payment Collection Specialist"
    goal: str = "Help freelancers collect overdue payments professionally"
    constraints: str = "Maintain professionalism, preserve relationships, escalate appropriately"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[EnforcePayment], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = EnforcePayment()
        return await action.run(instruction=text, context=str(context))
