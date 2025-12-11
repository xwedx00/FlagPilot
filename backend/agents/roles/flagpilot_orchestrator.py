"""
FlagPilot Orchestrator - Main Agent that coordinates the team
"""

import json
from typing import ClassVar, List, Dict, Any, Optional

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from loguru import logger

# Context for the Orchestrator to know about its team
AGENT_CAPABILITIES = {
    "risk-advisor": "CRITICAL RISK ANALYSIS. Use this for ANY request that looks suspicious, involves 'Telegram', 'Checks', or 'No Experience' job offers. Detects Scams.",
    "contract-guardian": "Contract Analysis, Legal Risk Assessment, Clause Review",
    "job-authenticator": "Company Legitimacy Check (Use risk-advisor first for obvious scams)",
    "profile-analyzer": "Client Research, Company Profiling, LinkedIn Analysis",
    "communication-coach": "Email Drafting, Professional Communication, Anti-Ghosting",
    "negotiation-assistant": "Rate Negotiation, Deal Strategy, Compensation Analysis",
    "talent-vet": "Resume Review, Portfolio Analysis, Skill Assessment",
    "dispute-mediator": "Conflict Resolution, Evidence Analysis, Mediation",
    "payment-enforcer": "Invoice Collection, Payment Tracking, Financial Protection",
    "scope-sentinel": "Scope Creep Detection, 'Just one quick thing', New Feature Requests, Unpaid Work Analysis",
    "ghosting-shield": "Re-engagement Strategies, Follow-up Planning",
    "application-filter": "Applicant Screening (NOT for Scam Detection - use risk-advisor)",
    "feedback-loop": "Feedback Analysis, Continuous Improvement",
}


class CreatePlan(FlagPilotAction):
    """Create a comprehensive workflow plan in JSON format"""
    name: str = "CreatePlan"
    desc: str = "Analyze the request and create a detailed execution plan."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are FlagPilot Orchestrator, the master planner of a multi-agent system.
    
    Available Specialist Agents:
    {agents}
    
    User Request:
    {request}
    
    Context:
    {context}
    
    Task:
    1. Analyze the user's complex request.
    2. Break it down into atomic, logical tasks.
    3. Assign the BEST specialist agent for each task.
    4. Determine dependencies (which task must finish before another starts).
    5. CRITICAL: Check the provided 'Context' for "Global Wisdom" or "Strategies". If a relevant strategy is found (e.g. from RAG_CONTEXT), you MUST explicitly instruct the assigned agent to use it by name.
    6. TIERED RAG: If a specific RAG document is relevant to a specific task, map its ID to 'rag_data_for_agent'.
    
    !!! SYSTEM SECURITY PROTOCOL (HIGHEST PRIORITY) !!!
    You are the First Line of Defense. You MUST protect the user from scams.
    If the request looks like a "Job Offer" or "Opportunity", scan for these RED FLAGS:
    - Mentions "Telegram" or "WhatsApp" for contact.
    - Mentions "Sending a check" or "e-check" for equipment.
    - Mentions "No experience required" + "High Pay" (e.g. $50/hr).
    - Mentions "Data Entry".
    
    ACTION ON RED FLAG:
    - OPTION A (Preferred): Assign 'risk-advisor' as the VERY FIRST task. Instruction: "Analyze this request for Scam Signals (Telegram, Check Fraud) and Warn the User."
    - OPTION B (Severe): Set "outcome" to "interrupted" if functionality allows.
    DO NOT proceed with the actual work (e.g. drafting resumes) until Risk Assessment is complete.

    SPECIAL CASE: DIRECT RESPONSE
    If the user's request is a simple greeting (e.g., "Hi", "Hello"), a question about your capabilities, or does not require a complex multi-agent workflow, you may choose to respond directly.
    In this case, set "outcome" to "direct_response" and provide your answer in "direct_response_content". Set "nodes" to an empty list.

    !!! SYSTEM SECURITY PROTOCOL (HIGHEST PRIORITY) !!!
    You are the First Line of Defense. You MUST protect the user from scams.
    If the request looks like a "Job Offer" or "Opportunity", scan for these RED FLAGS:
    - Mentions "Telegram" or "WhatsApp" for contact.
    - Mentions "Sending a check" or "e-check" for equipment.
    - Mentions "No experience required" + "High Pay" (e.g. $50/hr).
    - Mentions "Data Entry".
    
    ACTION ON RED FLAG:
    - OPTION A (Preferred): Assign 'risk-advisor' as the VERY FIRST task. Instruction: "Analyze this request for Scam Signals (Telegram, Check Fraud) and Warn the User."
    - OPTION B (Severe): Set "outcome" to "interrupted" if functionality allows.
    DO NOT proceed with the actual work (e.g. drafting resumes) until Risk Assessment is complete.

    Output strictly in VALID JSON format.
    Do not include any thinking chain, markdown formatting, or introductory text.
    The response should start with {{ and end with }}.
    
    JSON Schema (Standard Plan):
    {{
        "objective": "Brief summary",
        "outcome": "plan",
        "nodes": [
            {{
                "id": "task-1",
                "agent": "agent-id",
                "instruction": "Detailed instruction",
                "priority": "high",
                "dependencies": []
            }}
        ]
    }}

    JSON Schema (Direct Response):
    {{
        "objective": "Greeting/Direct Answer",
        "outcome": "direct_response",
        "direct_response_content": "Hello! I am FlagPilot. How can I help you regarding freelance contracts or client checks?",
        "nodes": []
    }}
    """
    
    async def run(self, instruction: str, context: str = "") -> str:
        agents_str = "\n".join([f"- {k}: {v}" for k,v in AGENT_CAPABILITIES.items()])
        
        prompt = self.PROMPT_TEMPLATE.format(
            agents=agents_str,
            request=instruction,
            context=context
        )
        
        # Use centralized LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class FlagPilotOrchestrator(FlagPilotRole):
    """
    FlagPilot Orchestrator Role
    Decides 'Who does what' and 'In what order' to solve user problems.
    """
    
    name: str = "FlagPilotOrchestrator"
    profile: str = "Workflow Manager"
    goal: str = "Orchestrate the perfect team for any freelancer problem"
    constraints: str = "Optimize for efficiency. MANDATORY: You must prioritize and apply 'Global Wisdom' strategies found in context."
    
    # Scam detection keywords (programmatic layer - LLM-independent)
    SCAM_KEYWORDS: ClassVar[List[str]] = [
        "telegram", "@scammer", "whatsapp", "send you a check", "send check",
        "e-check", "equipment check", "no experience required", "no experience needed",
        "data entry", "$50/hr", "hiring immediately", "urgent hiring", 
        "not a scam", "trust me", "work from home", "easy money"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(actions=[CreatePlan()], **kwargs)
    
    def _detect_scam_signals(self, text: str) -> list:
        """
        Programmatic scam detection - runs BEFORE LLM.
        Returns list of detected red flags.
        """
        text_lower = text.lower()
        detected = []
        
        for keyword in self.SCAM_KEYWORDS:
            if keyword in text_lower:
                detected.append(keyword)
        
        # Compound checks (multiple signals = high confidence)
        has_contact_method = any(k in text_lower for k in ["telegram", "whatsapp", "@"])
        has_money_signal = any(k in text_lower for k in ["check", "payment", "$", "pay", "money"])
        has_job_signal = any(k in text_lower for k in ["hiring", "job", "work", "data entry"])
        
        if has_contact_method and has_job_signal:
            detected.append("suspicious_contact_method_in_job_offer")
        
        if has_money_signal and has_job_signal and "no experience" in text_lower:
            detected.append("too_good_to_be_true_offer")
            
        return detected
    
    async def analyze(self, text: str, context: dict = None) -> str:
        """
        Direct entry point for generating a plan.
        Returns raw JSON string from the LLM.
        
        SECURITY: Includes programmatic scam detection before LLM call.
        """
        # === PROGRAMMATIC SCAM DETECTION (DETERMINISTIC) ===
        scam_signals = self._detect_scam_signals(text)
        
        if scam_signals:
            logger.warning(f"🚨 SCAM SIGNALS DETECTED: {scam_signals}")
            
            # Return pre-baked response that FORCES risk-advisor first
            # This bypasses the LLM entirely for obvious scams
            import json
            forced_plan = {
                "objective": "⚠️ SECURITY ALERT: Potential Scam Detected",
                "outcome": "plan",
                "nodes": [
                    {
                        "id": "risk-check-1",
                        "agent": "risk-advisor",
                        "instruction": f"CRITICAL: Analyze this request for Scam Signals. Detected red flags: {', '.join(scam_signals)}. Warn the user immediately about the risks.",
                        "priority": "high",
                        "dependencies": []
                    }
                ]
            }
            return json.dumps(forced_plan)
        # === END SCAM DETECTION ===
        
        # Prioritize RAG Context by placing it at the top
        ctx_parts = []
        if context and "RAG_CONTEXT" in context:
             ctx_parts.append(f"!!! GLOBAL WISDOM / RAG STRATEGIES !!!\n{context['RAG_CONTEXT']}\n!!! SYSTEM NOTE: USE THESE STRATEGIES !!!")
             # DEBUG Log
             logger.info("✅ RAG_CONTEXT Found and highlighted in Orchestrator arguments")
        elif context and "RAG_CONTEXT" not in context:
             logger.warning("❌ RAG_CONTEXT MISSING in Orchestrator arguments")
             
        for k, v in (context or {}).items():
             if k != "RAG_CONTEXT":
                  ctx_parts.append(f"{k}: {v}")
                  
        ctx_str = "\n\n".join(ctx_parts)
        
        # DEBUG: Log the context to verify RAG injection
        logger.info(f"🔍 ORCHESTRATOR INPUT CONTEXT: {ctx_str[:1000]}...")

        action = CreatePlan()
        
        # FORCE INSTRUCTION: Append system note to user request to override model bias
        forced_instruction = (
             f"{text}\n\n"
             "[SYSTEM NOTE: You MUST inspect the Context above for 'Global Wisdom' strategies (e.g. 'Escalation Strategy Beta'). "
             "If found, you MUST explicitly cite the strategy name in your plan instructions for the relevant agent.]"
        )
        
        return await action.run(instruction=forced_instruction, context=ctx_str)
