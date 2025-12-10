"""
Risk Advisor Agent
Specialized agent that steps in when a CRITICAL RISK is detected to provide emergency guidance.
"""

from typing import ClassVar
from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm

class ProvideEmergencyAdvice(FlagPilotAction):
    """Provide immediate, actionable steps for a critical risk"""
    
    name: str = "ProvideEmergencyAdvice"
    desc: str = "Synthesize emergency advice based on a critical risk interrupt."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are FlagPilot Risk Advisor, an emergency response expert.
    
    A CRITICAL RISK has been detected in the user's workflow, triggering an immediate abort.
    
    Risk Source Context:
    {context}
    
    Task:
    Provide a concise, high-priority "Emergency Response Plan".
    
    Format Requirements:
    1. Start with a bold warning header.
    2. State the detected risk clearly within 1-2 sentences.
    3. Provide 3-5 numbered, IMMEDIATE actionable steps (e.g., "Do not sign", "Block contact", "File report").
    4. Keep it authoritative and protective.
    
    Response:
    """

    async def run(self, instruction: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(context=context + "\n\nInstruction: " + instruction)
        llm = get_configured_llm()
        return await llm.aask(prompt)

class RiskAdvisor(FlagPilotRole):
    """
    Risk Advisor / Emergency Responder
    Activates only when a high-risk condition triggers a workflow abort.
    """
    
    name: str = "RiskAdvisor"
    profile: str = "Emergency Risk Advisor"
    goal: str = "Protect the user from immediate harm via actionable crisis advice"
    constraints: str = "Be concise, urgent, and protective."
    
    def __init__(self, **kwargs):
        super().__init__(actions=[ProvideEmergencyAdvice], **kwargs)
