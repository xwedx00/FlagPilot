"""
Market Intelligence Tools
==========================
Tools for rate benchmarking, proposal analysis, and negotiation support.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger

from .base import track_tool


# =============================================================================
# Market Rate Data (Production would use real APIs)
# =============================================================================

MARKET_RATES = {
    "web_developer": {
        "junior": {"us": (25, 50), "uk": (20, 40), "eu": (20, 45), "global": (15, 35)},
        "mid": {"us": (50, 100), "uk": (40, 80), "eu": (40, 75), "global": (30, 60)},
        "senior": {"us": (100, 200), "uk": (80, 150), "eu": (75, 140), "global": (50, 100)},
    },
    "designer": {
        "junior": {"us": (25, 45), "uk": (20, 40), "eu": (20, 40), "global": (15, 30)},
        "mid": {"us": (45, 90), "uk": (35, 75), "eu": (35, 70), "global": (25, 55)},
        "senior": {"us": (90, 175), "uk": (70, 140), "eu": (65, 130), "global": (45, 90)},
    },
    "writer": {
        "junior": {"us": (20, 40), "uk": (18, 35), "eu": (15, 30), "global": (10, 25)},
        "mid": {"us": (40, 80), "uk": (35, 65), "eu": (30, 60), "global": (20, 45)},
        "senior": {"us": (80, 150), "uk": (60, 120), "eu": (55, 110), "global": (40, 80)},
    },
    "developer": {
        "junior": {"us": (30, 60), "uk": (25, 50), "eu": (25, 50), "global": (20, 40)},
        "mid": {"us": (60, 120), "uk": (50, 100), "eu": (45, 95), "global": (35, 70)},
        "senior": {"us": (120, 250), "uk": (100, 200), "eu": (90, 180), "global": (60, 120)},
    },
    "marketing": {
        "junior": {"us": (20, 40), "uk": (18, 35), "eu": (18, 35), "global": (12, 28)},
        "mid": {"us": (40, 85), "uk": (35, 70), "eu": (35, 65), "global": (25, 50)},
        "senior": {"us": (85, 175), "uk": (70, 140), "eu": (65, 130), "global": (45, 95)},
    },
    "consultant": {
        "junior": {"us": (50, 100), "uk": (40, 80), "eu": (40, 80), "global": (30, 60)},
        "mid": {"us": (100, 200), "uk": (80, 160), "eu": (75, 150), "global": (50, 100)},
        "senior": {"us": (200, 400), "uk": (150, 300), "eu": (140, 280), "global": (100, 200)},
    },
    "data_scientist": {
        "junior": {"us": (40, 80), "uk": (35, 70), "eu": (35, 65), "global": (25, 50)},
        "mid": {"us": (80, 150), "uk": (65, 120), "eu": (60, 115), "global": (45, 85)},
        "senior": {"us": (150, 300), "uk": (120, 240), "eu": (110, 220), "global": (80, 160)},
    },
}


# =============================================================================
# Input Schemas
# =============================================================================

class MarketRateInput(BaseModel):
    """Input for market rate lookup."""
    skill: str = Field(..., description="Skill category (developer, designer, writer, etc)")
    level: str = Field(default="mid", description="Experience level (junior, mid, senior)")
    region: str = Field(default="us", description="Region (us, uk, eu, global)")


class ProposalBenchmarkInput(BaseModel):
    """Input for proposal benchmarking."""
    proposed_rate: float = Field(..., description="Your proposed hourly rate")
    skill: str = Field(..., description="Skill category")
    level: str = Field(default="mid", description="Experience level")
    region: str = Field(default="us", description="Client region")
    project_hours: float = Field(default=40, description="Estimated project hours")


class ClientBudgetInput(BaseModel):
    """Input for client budget estimation."""
    job_description: str = Field(..., description="Job posting or project description")
    company_size: str = Field(default="unknown", description="Company size (startup, small, medium, enterprise)")
    project_type: str = Field(default="unknown", description="Project type (website, app, marketing, etc)")


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=MarketRateInput)
@track_tool
async def get_market_rates(
    skill: str,
    level: str = "mid",
    region: str = "us"
) -> str:
    """
    Get market rate data for a specific skill and experience level.
    Returns salary ranges based on recent market data.
    """
    skill_key = skill.lower().replace(" ", "_").replace("-", "_")
    level_key = level.lower()
    region_key = region.lower()
    
    # Find closest matching skill
    skill_matches = [k for k in MARKET_RATES.keys() if skill_key in k or k in skill_key]
    if skill_matches:
        skill_key = skill_matches[0]
    elif skill_key not in MARKET_RATES:
        skill_key = "developer"  # Default
    
    if level_key not in ["junior", "mid", "senior"]:
        level_key = "mid"
    
    if region_key not in ["us", "uk", "eu", "global"]:
        region_key = "us"
    
    rates = MARKET_RATES[skill_key][level_key]
    skill_rates = rates[region_key]
    
    # Calculate derived metrics
    low, high = skill_rates
    median = (low + high) / 2
    monthly_low = low * 160  # 40 hrs/week
    monthly_high = high * 160
    annual_low = monthly_low * 12
    annual_high = monthly_high * 12
    
    # Get comparison regions
    all_regions = []
    for reg, (r_low, r_high) in rates.items():
        all_regions.append(f"| {reg.upper()} | ${r_low} - ${r_high} | ${(r_low+r_high)/2:.0f} |")
    
    return f"""## Market Rates: {skill.title()} ({level.title()})

### Rate Summary for {region.upper()}

| Metric | Amount |
|--------|--------|
| **Hourly Low** | ${low}/hr |
| **Hourly High** | ${high}/hr |
| **Recommended Rate** | ${median:.0f}/hr |
| **Monthly (Full-time)** | ${monthly_low:,.0f} - ${monthly_high:,.0f} |
| **Annual Equivalent** | ${annual_low:,.0f} - ${annual_high:,.0f} |

### Regional Comparison

| Region | Hourly Range | Median |
|--------|--------------|--------|
{chr(10).join(all_regions)}

### Rate Setting Tips

1. **Price based on value, not just time** - What is the outcome worth to the client?
2. **Factor in overhead** - Taxes, insurance, software, downtime (~30%)
3. **Consider project complexity** - Complex work commands premium rates
4. **Don't race to the bottom** - Competing on price attracts bad clients

### Adjustments

- **Specialized niche:** Add 20-50%
- **Urgent timeline:** Add 25-50%
- **Enterprise client:** Add 30-100%
- **Non-profit/startup:** May need to discount 10-20%
"""


@tool(args_schema=ProposalBenchmarkInput)
@track_tool
async def benchmark_proposal(
    proposed_rate: float,
    skill: str,
    level: str = "mid",
    region: str = "us",
    project_hours: float = 40
) -> str:
    """
    Benchmark your proposed rate against market data.
    Provides positioning analysis and negotiation recommendations.
    """
    skill_key = skill.lower().replace(" ", "_").replace("-", "_")
    level_key = level.lower()
    region_key = region.lower()
    
    # Get matching rates
    skill_matches = [k for k in MARKET_RATES.keys() if skill_key in k or k in skill_key]
    skill_key = skill_matches[0] if skill_matches else "developer"
    level_key = level_key if level_key in ["junior", "mid", "senior"] else "mid"
    region_key = region_key if region_key in ["us", "uk", "eu", "global"] else "us"
    
    low, high = MARKET_RATES[skill_key][level_key][region_key]
    median = (low + high) / 2
    
    # Calculate positioning
    if proposed_rate < low:
        positioning = "BELOW MARKET"
        position_emoji = "🔴"
        percentile = 10
    elif proposed_rate < median:
        positioning = "BELOW AVERAGE"
        position_emoji = "🟡"
        percentile = 35
    elif proposed_rate <= high:
        positioning = "COMPETITIVE"
        position_emoji = "🟢"
        percentile = 60
    else:
        positioning = "PREMIUM"
        position_emoji = "🔵"
        percentile = 85
    
    project_value = proposed_rate * project_hours
    market_project_low = low * project_hours
    market_project_high = high * project_hours
    
    # Recommendations
    if proposed_rate < low:
        recommendation = f"""### ⚠️ Recommendation: RAISE YOUR RATE

Your rate is **${proposed_rate - low:.2f}/hr below** the market minimum.

**Suggested actions:**
1. Raise to at least ${low}/hr (market minimum)
2. Better: Target ${median:.0f}/hr (market median)
3. Highlight your unique value to justify rate
4. Consider this: Underpricing attracts problem clients

**Opportunity cost:** At market median, this project would pay:
${median * project_hours:,.2f} vs your proposal of ${project_value:,.2f}
**You're leaving ${(median * project_hours) - project_value:,.2f} on the table.**
"""
    elif proposed_rate <= high:
        recommendation = f"""### ✅ Recommendation: RATE IS COMPETITIVE

Your rate is within the healthy market range.

**Position strategy:**
- Emphasize your track record and expertise
- Provide case studies or testimonials
- Be confident in your value proposition

**Room to grow:** You could justify up to ${high}/hr with:
- Specialized expertise
- Faster delivery
- Premium service level
"""
    else:
        recommendation = f"""### 🔵 Recommendation: JUSTIFY PREMIUM POSITIONING

Your rate is above typical market rates.

**To maintain premium pricing:**
1. Lead with results and ROI, not hours
2. Offer additional value (consulting, strategy, ongoing support)
3. Target enterprise clients with larger budgets
4. Be prepared to walk away from price-sensitive clients

**Risk:** Some clients may not understand premium value.
"""
    
    return f"""## Proposal Benchmark Analysis

### Your Proposal
| Metric | Value |
|--------|-------|
| **Your Rate** | ${proposed_rate:.2f}/hr |
| **Market Range** | ${low} - ${high}/hr |
| **Market Median** | ${median:.0f}/hr |
| **Project Hours** | {project_hours} hours |
| **Your Project Value** | ${project_value:,.2f} |

### Market Positioning: {position_emoji} {positioning}

**Percentile:** ~{percentile}th (out of 100 freelancers)

```
Market Low    You    Median    Market High
${low}/hr           ${median:.0f}/hr           ${high}/hr
   |------------|---------------|--------------|
   0%          35%             65%          100%
"""
    
    # Add visualization
    total_range = high - low
    position = min(max(proposed_rate - low, 0), total_range)
    bar_width = 40
    marker_pos = int((position / total_range) * bar_width) if total_range > 0 else 0
    bar = "─" * marker_pos + "█" + "─" * (bar_width - marker_pos - 1)
    
    return f"""## Proposal Benchmark Analysis

### Your Proposal
| Metric | Value |
|--------|-------|
| **Your Rate** | ${proposed_rate:.2f}/hr |
| **Market Range** | ${low} - ${high}/hr |
| **Market Median** | ${median:.0f}/hr |
| **Project Hours** | {project_hours} hours |
| **Your Project Value** | ${project_value:,.2f} |

### Market Positioning: {position_emoji} {positioning}

```
${low}  [{bar}]  ${high}
                ↑ You: ${proposed_rate:.0f}
```

{recommendation}
"""


@tool(args_schema=ClientBudgetInput)
@track_tool
async def analyze_client_budget(
    job_description: str,
    company_size: str = "unknown",
    project_type: str = "unknown"
) -> str:
    """
    Estimate client budget range based on job posting analysis.
    Uses signals in job description to infer budget flexibility.
    """
    desc_lower = job_description.lower()
    
    # Budget signals
    high_budget_signals = [
        ("enterprise", "Enterprise company"), ("fortune 500", "Fortune 500"),
        ("series", "Funded startup"), ("million", "High revenue mentioned"),
        ("long-term", "Long-term engagement"), ("senior", "Seeking senior talent"),
        ("critical", "Business-critical project"), ("urgent", "Urgency premium"),
        ("expert", "Expert-level requirement"), ("lead", "Leadership role"),
    ]
    
    low_budget_signals = [
        ("startup", "Early-stage startup"), ("bootstrap", "Bootstrapped company"),
        ("budget is", "Budget mentioned explicitly"), ("fixed price", "Fixed price project"),
        ("quick", "Quick/simple task"), ("simple", "Simple project"),
        ("part-time", "Part-time work"), ("student", "Student project"),
    ]
    
    # Analyze signals
    high_signals = []
    low_signals = []
    
    for keyword, label in high_budget_signals:
        if keyword in desc_lower:
            high_signals.append(label)
    
    for keyword, label in low_budget_signals:
        if keyword in desc_lower:
            low_signals.append(label)
    
    # Company size multipliers
    size_multipliers = {
        "enterprise": 2.0,
        "large": 1.5,
        "medium": 1.2,
        "small": 1.0,
        "startup": 0.8,
        "unknown": 1.0
    }
    
    multiplier = size_multipliers.get(company_size.lower(), 1.0)
    
    # Calculate score
    budget_score = 50 + (len(high_signals) * 15) - (len(low_signals) * 10)
    budget_score = max(10, min(100, budget_score))  # Clamp 10-100
    
    # Estimate budget range
    base_hourly = 50 * multiplier
    if budget_score >= 80:
        budget_range = (base_hourly * 1.5, base_hourly * 3)
        flexibility = "HIGH"
        emoji = "🔵"
    elif budget_score >= 50:
        budget_range = (base_hourly * 0.8, base_hourly * 1.5)
        flexibility = "MEDIUM"
        emoji = "🟢"
    else:
        budget_range = (base_hourly * 0.5, base_hourly * 0.9)
        flexibility = "LOW"
        emoji = "🟡"
    
    return f"""## Client Budget Analysis

### Estimated Budget: {emoji} {flexibility} Flexibility

**Likely Hourly Range:** ${budget_range[0]:.0f} - ${budget_range[1]:.0f}/hr
**Company Size Factor:** {company_size.title()} ({multiplier}x)

### Budget Signals Detected

**🔵 High Budget Indicators:**
{chr(10).join(f"- ✓ {s}" for s in high_signals) if high_signals else "- None detected"}

**🟡 Budget Constraints:**
{chr(10).join(f"- ⚠ {s}" for s in low_signals) if low_signals else "- None detected"}

### Budget Score: {budget_score}/100

### Negotiation Strategy

"""
    
    if budget_score >= 80:
        strategy = """- **Lead with value**, not price
- Propose at top of your range
- They have budget; prove you're worth it
- Consider value-based pricing"""
    elif budget_score >= 50:
        strategy = """- Standard negotiation approach
- Start 20% above target rate
- Be prepared to justify value
- Look for scope trade-offs"""
    else:
        strategy = """- Consider if this aligns with your minimums
- Be upfront about rate requirements early
- Don't invest time if budget mismatch
- May need to decline or limit scope"""
    
    return f"""## Client Budget Analysis

### Estimated Budget: {emoji} {flexibility} Flexibility

**Likely Hourly Range:** ${budget_range[0]:.0f} - ${budget_range[1]:.0f}/hr
**Company Size Factor:** {company_size.title()} ({multiplier}x)

### Budget Signals Detected

**🔵 High Budget Indicators:**
{chr(10).join(f"- ✓ {s}" for s in high_signals) if high_signals else "- None detected"}

**🟡 Budget Constraints:**
{chr(10).join(f"- ⚠ {s}" for s in low_signals) if low_signals else "- None detected"}

### Budget Score: {budget_score}/100

### Negotiation Strategy

{strategy}
"""


# =============================================================================
# Tool Registry
# =============================================================================

MARKET_TOOLS = [
    get_market_rates,
    benchmark_proposal,
    analyze_client_budget,
]
