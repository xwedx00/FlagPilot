"""
Contract Analysis Tools
=======================
Tools for analyzing legal contracts, extracting clauses, and assessing risks.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger
import re

from .base import track_tool


# =============================================================================
# Input Schemas
# =============================================================================

class ClauseAnalysisInput(BaseModel):
    """Input for contract clause analysis."""
    contract_text: str = Field(..., description="Full contract text to analyze")
    clause_types: List[str] = Field(
        default=["payment", "ip", "termination", "liability", "non_compete"],
        description="Types of clauses to extract and analyze"
    )


class JurisdictionCheckInput(BaseModel):
    """Input for jurisdiction law check."""
    clause_text: str = Field(..., description="Contract clause to check")
    jurisdiction: str = Field(default="US", description="Jurisdiction (US, UK, EU, etc)")
    clause_type: str = Field(..., description="Type of clause (non_compete, liability, etc)")


class RedlineInput(BaseModel):
    """Input for generating contract redlines."""
    original_text: str = Field(..., description="Original contract text")
    issues: List[str] = Field(..., description="List of issues to address")


class LiabilityInput(BaseModel):
    """Input for liability exposure calculation."""
    contract_text: str = Field(..., description="Contract text")
    project_value: float = Field(..., description="Total project value")
    payment_terms: Optional[str] = Field(None, description="Payment terms from contract")


# =============================================================================
# Clause Patterns
# =============================================================================

CLAUSE_PATTERNS = {
    "payment": {
        "patterns": [
            r"payment\s+(?:terms?|schedule|within|due)",
            r"(?:net|net-)\d+",
            r"\$[\d,]+(?:\.\d{2})?",
            r"(\d+)\s*%\s*(?:upfront|deposit|upon)",
            r"milestone",
            r"invoice",
        ],
        "risk_keywords": {
            "high": ["net 90", "net 120", "upon completion only", "no deposit"],
            "medium": ["net 60", "net 45"],
            "low": ["net 30", "50% upfront", "deposit", "milestone"]
        }
    },
    "ip": {
        "patterns": [
            r"intellectual\s+property",
            r"work(?:s)?\s+(?:for\s+)?hire",
            r"copyright",
            r"ownership",
            r"moral\s+rights",
            r"perpetual\s+license",
        ],
        "risk_keywords": {
            "high": ["all rights", "perpetual", "irrevocable", "worldwide", "moral rights waived"],
            "medium": ["exclusive license", "first right"],
            "low": ["non-exclusive", "limited license", "credit required"]
        }
    },
    "termination": {
        "patterns": [
            r"terminat(?:e|ion)",
            r"cancel(?:lation)?",
            r"notice\s+period",
            r"at\s+will",
            r"for\s+cause",
            r"without\s+cause",
        ],
        "risk_keywords": {
            "high": ["immediate termination", "without notice", "no payment for work done"],
            "medium": ["7 days notice", "partial payment"],
            "low": ["30 days notice", "payment for work completed", "mutual agreement"]
        }
    },
    "liability": {
        "patterns": [
            r"liability",
            r"indemnif(?:y|ication)",
            r"damages",
            r"limitation\s+of\s+liability",
            r"hold\s+harmless",
            r"consequential",
        ],
        "risk_keywords": {
            "high": ["unlimited liability", "indemnify against all", "consequential damages"],
            "medium": ["3x contract value", "cap at fees paid"],
            "low": ["limited to direct damages", "mutual indemnification", "reasonable cap"]
        }
    },
    "non_compete": {
        "patterns": [
            r"non[\s-]?compete",
            r"non[\s-]?solicitation",
            r"restraint\s+of\s+trade",
            r"exclusive(?:ity)?",
            r"compete\s+with",
        ],
        "risk_keywords": {
            "high": ["worldwide", "5 years", "any competitor", "all clients"],
            "medium": ["2 years", "direct competitors", "same industry"],
            "low": ["6 months", "1 year", "specific competitors only", "reasonable geographic"]
        }
    }
}


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=ClauseAnalysisInput)
@track_tool
async def analyze_contract_clauses(
    contract_text: str,
    clause_types: List[str] = None
) -> str:
    """
    Extract and analyze specific clauses from a contract.
    Identifies key terms, risk levels, and provides recommendations.
    """
    if clause_types is None:
        clause_types = ["payment", "ip", "termination", "liability", "non_compete"]
    
    text_lower = contract_text.lower()
    results = []
    overall_risk = 0
    clause_count = 0
    
    for clause_type in clause_types:
        if clause_type not in CLAUSE_PATTERNS:
            continue
            
        pattern_data = CLAUSE_PATTERNS[clause_type]
        
        # Find matching sentences
        found_content = []
        for pattern in pattern_data["patterns"]:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # Extract surrounding context (sentence)
                start = max(0, match.start() - 100)
                end = min(len(text_lower), match.end() + 100)
                context = contract_text[start:end].strip()
                if context not in found_content:
                    found_content.append(context)
        
        if not found_content:
            results.append(f"### {clause_type.upper().replace('_', ' ')} Clause\n❌ Not found in contract\n")
            continue
        
        # Assess risk level
        risk_level = "low"
        risk_reasons = []
        
        for level in ["high", "medium", "low"]:
            for keyword in pattern_data["risk_keywords"].get(level, []):
                if keyword.lower() in text_lower:
                    if level in ["high", "medium"]:
                        risk_level = level
                        risk_reasons.append(keyword)
        
        clause_count += 1
        if risk_level == "high":
            overall_risk += 3
            risk_emoji = "🔴"
        elif risk_level == "medium":
            overall_risk += 2
            risk_emoji = "🟡"
        else:
            overall_risk += 1
            risk_emoji = "🟢"
        
        clause_result = f"""### {clause_type.upper().replace('_', ' ')} Clause

**Risk Level:** {risk_emoji} {risk_level.upper()}

**Found Terms:**
```
{found_content[0][:200]}...
```

"""
        if risk_reasons:
            clause_result += f"**Concerns:** {', '.join(risk_reasons)}\n\n"
        
        results.append(clause_result)
    
    # Calculate overall assessment
    avg_risk = overall_risk / max(clause_count, 1)
    
    header = f"""## Contract Clause Analysis

**Clauses Analyzed:** {clause_count}
**Overall Risk:** {'🔴 HIGH' if avg_risk >= 2.5 else '🟡 MEDIUM' if avg_risk >= 1.5 else '🟢 LOW'}

---

"""
    
    return header + "\n".join(results)


@tool(args_schema=JurisdictionCheckInput)
@track_tool
async def check_jurisdiction_laws(
    clause_text: str,
    jurisdiction: str = "US",
    clause_type: str = "non_compete"
) -> str:
    """
    Check if a contract clause is enforceable in the specified jurisdiction.
    Provides guidance on legal validity and common restrictions.
    """
    # Jurisdiction-specific rules (simplified but real guidance)
    jurisdiction_rules = {
        "US": {
            "non_compete": {
                "enforceable": "Varies by state",
                "details": """
**California:** Non-competes are UNENFORCEABLE (except for sale of business)
**New York:** Enforceable if reasonable in scope, duration, and geography
**Texas:** Enforceable with limitations
**Most states:** 6 months to 2 years typically acceptable

Key factors courts consider:
- Geographic scope (must be reasonable)
- Time period (6-24 months typical)
- Industry/role specificity
- Consideration provided
""",
                "recommendation": "If in CA, this clause is void. In other states, push for narrower scope."
            },
            "liability": {
                "enforceable": "Generally yes, with limits",
                "details": """
**Gross negligence:** Cannot be waived in most states
**Fraud:** Cannot be limited
**Consumer protection:** Various state laws apply

Typical acceptable limits:
- Cap at total contract value
- Exclude consequential damages
- Mutual limitation provisions
""",
                "recommendation": "Ensure liability cap exists and is mutual. Reject unlimited liability."
            },
            "ip": {
                "enforceable": "Generally yes",
                "details": """
**Work for hire:** Valid for employees and specific contractor relationships
**Copyright assignment:** Must be in writing
**Moral rights:** Can be waived in US

Watch for:
- Pre-existing IP clauses (protect your previous work)
- Portfolio rights (ensure you can show work)
- Background IP ownership
""",
                "recommendation": "Always carve out pre-existing IP and portfolio usage rights."
            }
        },
        "UK": {
            "non_compete": {
                "enforceable": "Strict scrutiny",
                "details": """
**Reasonableness test:** Courts will not enforce unreasonable restraints
**Typical limits:** 6-12 months maximum in most cases
**Must protect legitimate business interest**

UK courts are generally hostile to broad non-competes.
""",
                "recommendation": "UK courts favor workers. Push back on anything over 6 months."
            },
            "liability": {
                "enforceable": "With consumer protection limits",
                "details": """
**UCTA 1977:** Unfair Contract Terms Act applies
**Cannot exclude liability for death/injury from negligence**
**Consumer Rights Act 2015:** Additional protections
""",
                "recommendation": "Reasonable limitations are fine. Reject exclusions for gross negligence."
            }
        },
        "EU": {
            "non_compete": {
                "enforceable": "Generally disfavored",
                "details": """
**Germany:** Requires compensation during restriction period
**France:** Strict limits, often unenforceable
**Netherlands:** Very limited enforcement

EU generally protects freedom to work.
""",
                "recommendation": "EU-wide, non-competes face strong limitations. Push back aggressively."
            }
        }
    }
    
    jurisdiction = jurisdiction.upper()
    rules = jurisdiction_rules.get(jurisdiction, jurisdiction_rules["US"])
    clause_rules = rules.get(clause_type, {
        "enforceable": "Unknown",
        "details": "No specific guidance available for this clause type.",
        "recommendation": "Consult with a local attorney for specific advice."
    })
    
    return f"""## Jurisdiction Check: {clause_type.upper().replace('_', ' ')}

**Jurisdiction:** {jurisdiction}
**Enforceability:** {clause_rules['enforceable']}

### Legal Guidance
{clause_rules['details']}

### Recommendation
{clause_rules['recommendation']}

### Clause Under Review
```
{clause_text[:300]}...
```

---
⚠️ **Disclaimer:** This is general guidance only. Consult a licensed attorney for specific legal advice.
"""


@tool(args_schema=RedlineInput)
@track_tool
async def generate_contract_redlines(
    original_text: str,
    issues: List[str]
) -> str:
    """
    Generate suggested contract changes (redlines) to address identified issues.
    Provides alternative language for problematic clauses.
    """
    # Standard protective language templates
    protective_clauses = {
        "payment": {
            "original_indicators": ["net 60", "net 90", "upon completion"],
            "suggested": "50% deposit due upon signing. Remaining 50% due within 14 days of final delivery. Late payments accrue interest at 1.5% per month."
        },
        "ip": {
            "original_indicators": ["all rights", "perpetual", "worldwide rights"],
            "suggested": "Contractor retains ownership of all pre-existing intellectual property. Client receives non-exclusive license to use deliverables. Contractor may display work in portfolio with client attribution."
        },
        "termination": {
            "original_indicators": ["immediate", "without notice", "without payment"],
            "suggested": "Either party may terminate with 14 days written notice. Upon termination, Client pays for all work completed to date at the agreed rate. Contractor delivers all work-in-progress upon receipt of final payment."
        },
        "liability": {
            "original_indicators": ["unlimited", "indemnify against all", "consequential"],
            "suggested": "Neither party shall be liable for indirect, incidental, or consequential damages. Total liability of either party shall not exceed the total fees paid under this Agreement."
        },
        "non_compete": {
            "original_indicators": ["worldwide", "5 year", "any competitor"],
            "suggested": "Contractor agrees not to solicit Client's current employees for 12 months after project completion. No other restrictions on Contractor's ability to work with other clients."
        }
    }
    
    result = """## Contract Redline Suggestions

These are suggested changes to address the identified issues. Copy and propose these modifications to the client.

---

"""
    
    for issue in issues:
        issue_lower = issue.lower()
        
        # Find matching clause type
        matched = None
        for clause_type, data in protective_clauses.items():
            if clause_type in issue_lower or any(ind in issue_lower for ind in data["original_indicators"]):
                matched = (clause_type, data)
                break
        
        if matched:
            clause_type, data = matched
            result += f"""### Issue: {issue}

**❌ Problematic Language:**
> Current clause contains concerning terms: {', '.join(data['original_indicators'][:3])}

**✅ Suggested Replacement:**
```
{data['suggested']}
```

---

"""
        else:
            result += f"""### Issue: {issue}

**Recommendation:** Negotiate removal or modification of this clause. Consult with an attorney for specific alternative language.

---

"""
    
    result += """
### Negotiation Tips

1. **Be Professional:** Frame changes as "industry standard" not personal demands
2. **Offer Alternatives:** Don't just reject—propose fair alternatives  
3. **Prioritize:** Focus on the most critical issues first
4. **Document:** Keep all versions and communications in writing
5. **Walk Away Power:** Know your limits before negotiating
"""
    
    return result


@tool(args_schema=LiabilityInput)
@track_tool
async def calculate_liability_exposure(
    contract_text: str,
    project_value: float,
    payment_terms: Optional[str] = None
) -> str:
    """
    Calculate the potential financial exposure and risk from contract terms.
    Analyzes liability caps, indemnification, and payment terms.
    """
    text_lower = contract_text.lower()
    
    # Detect liability cap
    liability_cap = None
    cap_patterns = [
        (r"liability.*(?:not exceed|limited to|capped at).*\$?([\d,]+)", "explicit"),
        (r"(\d+)x.*(?:contract|fees|amount)", "multiplier"),
        (r"unlimited liability", "unlimited"),
    ]
    
    for pattern, cap_type in cap_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if cap_type == "unlimited":
                liability_cap = ("unlimited", float('inf'))
            elif cap_type == "multiplier":
                multiplier = int(match.group(1))
                liability_cap = (f"{multiplier}x contract value", project_value * multiplier)
            else:
                cap_value = float(match.group(1).replace(',', ''))
                liability_cap = (f"${cap_value:,.2f}", cap_value)
            break
    
    if liability_cap is None:
        liability_cap = ("undefined", project_value * 10)  # Assume worst case
    
    # Detect indemnification
    indemnification_risk = "low"
    if "indemnify" in text_lower:
        if "all claims" in text_lower or "any and all" in text_lower:
            indemnification_risk = "high"
        elif "mutual" in text_lower:
            indemnification_risk = "low"
        else:
            indemnification_risk = "medium"
    
    # Calculate exposure
    max_exposure = liability_cap[1] if liability_cap[1] != float('inf') else project_value * 100
    
    result = f"""## Liability Exposure Analysis

### Project Value: ${project_value:,.2f}

---

### Liability Cap Analysis

**Detected Cap:** {liability_cap[0]}
**Maximum Exposure:** ${min(max_exposure, 10000000):,.2f}

### Indemnification Risk: {'🔴 HIGH' if indemnification_risk == 'high' else '🟡 MEDIUM' if indemnification_risk == 'medium' else '🟢 LOW'}

"""
    
    if indemnification_risk == "high":
        result += """
⚠️ **WARNING:** Broad indemnification clause detected. You could be responsible for:
- Client's legal fees
- Third-party claims against client
- Damages beyond project scope

**Recommendation:** Negotiate mutual indemnification or limit to your direct negligence.
"""
    
    # Payment risk analysis
    if payment_terms:
        if "net 90" in payment_terms.lower() or "net 120" in payment_terms.lower():
            payment_risk = "high"
        elif "net 60" in payment_terms.lower():
            payment_risk = "medium"
        else:
            payment_risk = "low"
        
        result += f"""
### Payment Risk: {'🔴' if payment_risk == 'high' else '🟡' if payment_risk == 'medium' else '🟢'} {payment_risk.upper()}

**Terms:** {payment_terms}
"""
    
    result += f"""
---

### Risk Summary

| Factor | Exposure | Risk Level |
|--------|----------|------------|
| Liability Cap | {liability_cap[0]} | {'High' if liability_cap[1] == float('inf') else 'Medium' if liability_cap[1] > project_value * 3 else 'Acceptable'} |
| Indemnification | {indemnification_risk.title()} | {indemnification_risk.title()} |
| Total Maximum Exposure | ${min(max_exposure, 10000000):,.2f} | - |

### Recommendations

1. **Insurance:** Ensure you have professional liability insurance covering at least ${min(max_exposure * 0.5, 500000):,.0f}
2. **Negotiate Cap:** Push for liability limited to fees paid
3. **Mutual Terms:** Ensure indemnification goes both ways
4. **Deposit:** Get 50%+ upfront to reduce payment risk
"""
    
    return result


# =============================================================================
# Tool Registry
# =============================================================================

CONTRACT_TOOLS = [
    analyze_contract_clauses,
    check_jurisdiction_laws,
    generate_contract_redlines,
    calculate_liability_exposure,
]
