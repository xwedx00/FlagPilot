"""
FlagPilot Orchestrator - LangGraph Multi-Agent Supervisor
=========================================================
Implements team orchestration using LangGraph with:
- Dynamic agent routing based on task analysis
- Fast-fail risk detection (programmatic + LLM)
- RAG context injection
- State persistence and memory
- Parallel agent execution
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger
import asyncio

from config import settings
from lib.persistence import get_checkpointer


class OrchestratorState(TypedDict):
    """State for the multi-agent workflow"""
    messages: Annotated[list, add_messages]
    task: str
    context: Dict[str, Any]
    selected_agents: List[str]
    agent_outputs: Dict[str, str]
    current_agent: str
    risk_level: str
    is_critical_risk: bool
    final_synthesis: str
    status: str
    error: Optional[str]


# Agent capabilities for routing
AGENT_CAPABILITIES = {
    "risk-advisor": "CRITICAL RISK ANALYSIS. Use for ANY suspicious request involving Telegram, checks, 'no experience required' job offers. Detects scams.",
    "contract-guardian": "Contract Analysis, Legal Risk Assessment, Clause Review, IP Rights, Payment Terms",
    "job-authenticator": "Company Legitimacy Check, Job Posting Verification, Scam Detection",
    "profile-analyzer": "Client Research, Company Profiling, Reputation Analysis",
    "communication-coach": "Email Drafting, Professional Communication, Client Messages",
    "negotiation-assistant": "Rate Negotiation, Deal Strategy, Compensation Benchmarks",
    "talent-vet": "Resume Review, Portfolio Analysis, Skill Assessment",
    "dispute-mediator": "Conflict Resolution, Evidence Analysis, Mediation Strategies",
    "payment-enforcer": "Invoice Collection, Payment Tracking, Financial Protection",
    "scope-sentinel": "Scope Creep Detection, Feature Requests Analysis, Boundary Protection",
    "ghosting-shield": "Re-engagement Strategies, Follow-up Planning, Client Recovery",
    "application-filter": "Applicant Screening, Resume Filtering, Candidate Ranking",
    "feedback-loop": "Feedback Analysis, Outcome Learning, Continuous Improvement",
    "planner-role": "Task Planning, Workflow Organization, Priority Setting",
}

# Scam detection keywords (fast-fail before LLM)
SCAM_KEYWORDS = [
    "telegram", "whatsapp", "send you a check", "send check",
    "e-check", "equipment check", "no experience required", "no experience needed",
    "data entry", "$50/hr", "$45/hr", "hiring immediately", "urgent hiring",
    "not a scam", "trust me", "work from home", "easy money", "zelle", "venmo",
    "bank details", "direct deposit setup", "security deposit"
]


def detect_scam_signals(text: str) -> List[str]:
    """
    Programmatic scam detection - runs BEFORE LLM.
    Returns list of detected red flags.
    """
    text_lower = text.lower()
    detected = []
    
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            detected.append(keyword)
    
    # Compound checks
    has_contact_method = any(k in text_lower for k in ["telegram", "whatsapp", "@"])
    has_money_signal = any(k in text_lower for k in ["check", "payment", "$", "pay", "money", "deposit"])
    has_job_signal = any(k in text_lower for k in ["hiring", "job", "work", "data entry", "position"])
    
    if has_contact_method and has_job_signal:
        detected.append("suspicious_contact_in_job_offer")
    
    if has_money_signal and has_job_signal and "no experience" in text_lower:
        detected.append("too_good_to_be_true")
    
    return detected


def identify_relevant_agents(task: str) -> List[str]:
    """Identify which agents should work on this task"""
    task_lower = task.lower()
    relevant = []
    
    # Contract-related
    if any(w in task_lower for w in ["contract", "agreement", "terms", "clause", "sign", "legal"]):
        relevant.append("contract-guardian")
    
    # Job-related
    if any(w in task_lower for w in ["job", "posting", "scam", "fake", "opportunity", "position", "hiring", "offer"]):
        relevant.append("job-authenticator")
    
    # Payment-related
    if any(w in task_lower for w in ["payment", "invoice", "overdue", "collect", "owe", "pay", "money", "late"]):
        relevant.append("payment-enforcer")
    
    # Scope-related
    if any(w in task_lower for w in ["scope", "creep", "additional", "extra", "change request", "more work", "revision"]):
        relevant.append("scope-sentinel")
    
    # Dispute-related
    if any(w in task_lower for w in ["dispute", "conflict", "disagree", "problem", "issue", "complaint"]):
        relevant.append("dispute-mediator")
    
    # Communication-related
    if any(w in task_lower for w in ["message", "email", "write", "draft", "communicate", "proposal", "reply"]):
        relevant.append("communication-coach")
    
    # Negotiation-related
    if any(w in task_lower for w in ["rate", "salary", "negotiate", "price", "cost", "budget", "worth", "charge"]):
        relevant.append("negotiation-assistant")
    
    # Ghosting-related
    if any(w in task_lower for w in ["ghost", "silent", "respond", "follow up", "no response"]): 
        relevant.append("ghosting-shield")
    
    # Profile-related
    if any(w in task_lower for w in ["client", "profile", "company", "background", "review"]):
        relevant.append("profile-analyzer")
    
    # Default: use common agents
    if not relevant:
        relevant = ["profile-analyzer", "communication-coach"]
    
    return relevant[:4]  # Max 4 agents per task


def is_simple_greeting(task: str) -> bool:
    """Check if task is a simple greeting"""
    greetings = ["hi", "hello", "hey", "good morning", "help", "?"]
    task_lower = task.lower().strip()
    return any(task_lower == g or task_lower.startswith(g + " ") for g in greetings) and len(task_lower) < 50


async def plan_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Planning node - analyzes task, detects risks, selects agents.
    """
    task = state["task"]
    context = state.get("context", {}) or {}
    
    logger.info(f"🎯 Planning for: {task[:80]}...")
    
    # Fast-fail: Scam detection
    scam_signals = detect_scam_signals(task)
    if scam_signals:
        logger.warning(f"🚨 SCAM SIGNALS: {scam_signals}")
        return {
            "selected_agents": ["risk-advisor"],
            "status": "risk_check",
            "context": {**context, "scam_signals": scam_signals},
            "is_critical_risk": True,
            "risk_level": "CRITICAL"
        }
    
    # Simple greeting: bypass agents
    if is_simple_greeting(task):
        return {
            "selected_agents": [],
            "status": "direct_response",
            "final_synthesis": """# 👋 Welcome to FlagPilot!

I'm your AI-powered freelancer protection team. I can help you with:

| Service | What I Do |
|---------|-----------|
| 📋 **Contract Review** | Analyze contracts for risks and unfair clauses |
| 🔍 **Scam Detection** | Verify job postings and detect fraud |
| 💰 **Payment Protection** | Track invoices and collection strategies |
| 🎯 **Scope Management** | Identify scope creep and boundary violations |
| ✍️ **Communication** | Draft professional messages and proposals |
| 💵 **Rate Negotiation** | Get benchmark data and counter-offer strategies |

**How can I help protect your freelance business today?**"""
        }
    
    # Inject RAG and memory context
    try:
        from ragflow.client import get_ragflow_client
        from lib.memory.manager import MemoryManager
        
        user_id = context.get("user_id") or context.get("id")
        if user_id:
            client = get_ragflow_client()
            rag_results = await client.search_user_context(user_id, task, limit=3)
            if rag_results:
                context["RAG_CONTEXT"] = "\n".join([r.get("content", "")[:300] for r in rag_results])
            
            memory = MemoryManager()
            if memory.connected:
                profile = await memory.get_user_profile(user_id)
                if profile.get("summary"):
                    context["USER_MEMORY"] = profile["summary"]
    except Exception as e:
        logger.debug(f"Context injection skipped: {e}")
    
    # 🧠 INTELLIGENT ROUTING: Use LLM to select agents (replaces naive keyword matching)
    from agents.router import llm_route_agents
    selected, reasoning, urgency = await llm_route_agents(task, context)
    
    logger.info(f"🧠 LLM Router selected: {selected} (urgency: {urgency})")
    logger.debug(f"Routing reasoning: {reasoning}")
    
    # Elevate risk level based on urgency
    risk_level = "LOW"
    is_critical = False
    if urgency == "critical":
        risk_level = "CRITICAL"
        is_critical = True
    elif urgency == "high":
        risk_level = "HIGH"
    
    return {
        "selected_agents": selected,
        "context": {**context, "routing_reasoning": reasoning, "urgency": urgency},
        "status": "executing",
        "risk_level": risk_level,
        "is_critical_risk": is_critical
    }


async def execute_node(state: OrchestratorState) -> Dict[str, Any]:
    """Execute selected agents in parallel"""
    from agents.agents import get_agent
    
    selected = state.get("selected_agents", [])
    
    if state.get("status") == "direct_response":
        return {"agent_outputs": {}}
    
    if not selected:
        return {"agent_outputs": {}, "status": "no_agents"}
    
    logger.info(f"🚀 Executing {len(selected)} agents")
    
    agent_outputs = {}
    is_critical = state.get("is_critical_risk", False)
    risk_level = state.get("risk_level", "LOW")
    
    async def run_agent(agent_id: str) -> tuple:
        try:
            agent = get_agent(agent_id)
            if agent:
                result = await agent.analyze(state["task"], state["context"])
                
                # Check for critical risk
                result_lower = result.lower()
                if "critical" in result_lower and ("scam" in result_lower or "fraud" in result_lower):
                    return (agent_id, result, True, "CRITICAL")
                
                return (agent_id, result, False, "LOW")
            return (agent_id, f"Agent {agent_id} not found", False, "LOW")
        except Exception as e:
            logger.error(f"Agent {agent_id} error: {e}")
            return (agent_id, f"Error: {e}", False, "LOW")
    
    # Run all agents concurrently
    results = await asyncio.gather(*[run_agent(a) for a in selected], return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            continue
        agent_id, output, critical, risk = result
        agent_outputs[agent_id] = output
        if critical:
            is_critical = True
            risk_level = "CRITICAL"
    
    logger.info(f"✅ Execution complete. Risk: {risk_level}")
    
    return {
        "agent_outputs": agent_outputs,
        "is_critical_risk": is_critical,
        "risk_level": risk_level,
        "status": "synthesizing"
    }


async def synthesize_node(state: OrchestratorState) -> Dict[str, Any]:
    """Synthesize agent outputs into final response"""
    
    if state.get("status") == "direct_response":
        return {"status": "COMPLETED"}
    
    agent_outputs = state.get("agent_outputs", {})
    
    # Critical risk: abort
    if state.get("is_critical_risk"):
        synthesis = "# 🚨 CRITICAL RISK DETECTED\n\n"
        for agent_id, output in agent_outputs.items():
            synthesis += f"## {agent_id.replace('-', ' ').title()}\n\n{output}\n\n---\n\n"
        synthesis += "⛔ **Please review these warnings carefully before proceeding.**"
        return {"final_synthesis": synthesis, "status": "RISK_DETECTED"}
    
    # No outputs
    if not agent_outputs:
        return {
            "final_synthesis": "I wasn't able to analyze your request. Please provide more details.",
            "status": "COMPLETED"
        }
    
    # Combine outputs with synthesis
    llm = ChatOpenAI(
        model=settings.OPENROUTER_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=0.3
    )
    
    outputs_str = "\n\n---\n\n".join([
        f"### {agent_id.replace('-', ' ').title()}\n\n{output}"
        for agent_id, output in agent_outputs.items()
    ])
    
    prompt = f"""You are FlagPilot, synthesizing analysis from specialist agents.

## Original Request
{state['task']}

## Agent Analyses
{outputs_str}

## Your Task
Create a comprehensive response that:
1. Summarizes key findings
2. Lists recommended actions (numbered)
3. Highlights any warnings
4. Includes any templates or scripts provided by agents

Use clear markdown formatting. Be thorough but concise."""

    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are FlagPilot, synthesizing multi-agent analysis into actionable advice."),
            HumanMessage(content=prompt)
        ])
        return {"final_synthesis": response.content, "status": "COMPLETED"}
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return {"final_synthesis": f"## Agent Analyses\n\n{outputs_str}", "status": "COMPLETED"}


# Build the graph
workflow = StateGraph(OrchestratorState)
workflow.add_node("plan", plan_node)
workflow.add_node("execute", execute_node)
workflow.add_node("synthesize", synthesize_node)
workflow.set_entry_point("plan")
workflow.add_edge("plan", "execute")
workflow.add_edge("execute", "synthesize")
workflow.add_edge("synthesize", END)

# Compile with persistent checkpointer (PostgreSQL or fallback to memory)
checkpointer = get_checkpointer()
orchestrator_graph = workflow.compile(checkpointer=checkpointer)


async def run_orchestrator(task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run the orchestrator"""
    context = context or {}
    thread_id = context.get("user_id") or context.get("session_id") or "default"
    
    initial_state = {
        "messages": [],
        "task": task,
        "context": context,
        "selected_agents": [],
        "agent_outputs": {},
        "current_agent": "",
        "risk_level": "LOW",
        "is_critical_risk": False,
        "final_synthesis": "",
        "status": "",
        "error": None
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    result = await orchestrator_graph.ainvoke(initial_state, config=config)
    
    return {
        "task": task,
        "final_synthesis": result.get("final_synthesis", ""),
        "status": result.get("status", "COMPLETED"),
        "risk_level": result.get("risk_level", "LOW"),
        "is_critical_risk": result.get("is_critical_risk", False),
        "agent_outputs": result.get("agent_outputs", {}),
    }
