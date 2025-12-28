"""
Financial Tools
================
Tools for payment tracking, invoice generation, and collection strategies.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime, timedelta
import calendar

from .base import track_tool


# =============================================================================
# Input Schemas
# =============================================================================

class OverdueCalculationInput(BaseModel):
    """Input for overdue amount calculation."""
    principal_amount: float = Field(..., description="Original invoice amount")
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format")
    late_fee_rate: float = Field(default=1.5, description="Monthly late fee percentage")


class InvoiceInput(BaseModel):
    """Input for invoice generation."""
    client_name: str = Field(..., description="Client company or individual name")
    client_email: str = Field(..., description="Client email address")
    line_items: List[Dict[str, Any]] = Field(..., description="List of items with description, hours, rate")
    payment_terms: int = Field(default=14, description="Payment due in days")
    notes: Optional[str] = Field(None, description="Additional notes for invoice")


class CollectionLetterInput(BaseModel):
    """Input for collection letter drafting."""
    client_name: str = Field(..., description="Client name")
    amount_owed: float = Field(..., description="Total amount owed including fees")
    days_overdue: int = Field(..., description="Number of days past due")
    previous_attempts: int = Field(default=0, description="Number of previous collection attempts")
    project_description: str = Field(..., description="Brief description of work completed")


class ScopeCreepInput(BaseModel):
    """Input for scope creep value estimation."""
    original_scope: str = Field(..., description="Original project scope/requirements")
    additional_requests: List[str] = Field(..., description="List of additional requests received")
    hourly_rate: float = Field(..., description="Your hourly rate")
    original_estimate_hours: float = Field(..., description="Original hours estimated")


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=OverdueCalculationInput)
@track_tool
async def calculate_overdue_amount(
    principal_amount: float,
    due_date: str,
    late_fee_rate: float = 1.5
) -> str:
    """
    Calculate the total amount owed including late fees.
    Computes days overdue, accrued interest, and total due.
    """
    try:
        due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
        today = datetime.now()
        days_overdue = (today - due_datetime).days
        
        if days_overdue <= 0:
            return f"""## Payment Status

**Invoice Amount:** ${principal_amount:,.2f}
**Due Date:** {due_date}
**Status:** ✅ NOT YET DUE

Payment is due in {-days_overdue} days.
"""
        
        # Calculate late fees (monthly rate, compounded)
        months_overdue = days_overdue / 30
        late_fee_amount = principal_amount * (late_fee_rate / 100) * months_overdue
        total_due = principal_amount + late_fee_amount
        
        # Determine urgency level
        if days_overdue > 90:
            urgency = "🔴 CRITICAL"
            action = "Consider legal action or collection agency"
        elif days_overdue > 60:
            urgency = "🟠 SEVERE"
            action = "Send final demand letter"
        elif days_overdue > 30:
            urgency = "🟡 HIGH"
            action = "Escalate with formal letter"
        else:
            urgency = "🟡 MODERATE"
            action = "Send friendly reminder"
        
        return f"""## Overdue Payment Calculation

### Summary
| Item | Amount |
|------|--------|
| **Principal** | ${principal_amount:,.2f} |
| **Due Date** | {due_date} |
| **Days Overdue** | {days_overdue} days |
| **Late Fee Rate** | {late_fee_rate}% per month |
| **Late Fees Accrued** | ${late_fee_amount:,.2f} |
| **TOTAL DUE** | **${total_due:,.2f}** |

### Urgency Level: {urgency}
**Recommended Action:** {action}

### Late Fee Breakdown
- Monthly rate: {late_fee_rate}%
- Months overdue: {months_overdue:.1f}
- Compounded fees: ${late_fee_amount:,.2f}

### Next Steps
1. Document all communication attempts
2. Send formal payment demand
3. Set deadline for response (7 days)
4. Prepare for escalation if no response
"""
    except ValueError as e:
        return f"Error parsing date: {e}. Use YYYY-MM-DD format."


@tool(args_schema=InvoiceInput)
@track_tool
async def generate_invoice(
    client_name: str,
    client_email: str,
    line_items: List[Dict[str, Any]],
    payment_terms: int = 14,
    notes: Optional[str] = None
) -> str:
    """
    Generate a professional invoice with itemized charges.
    Returns formatted invoice ready to send to client.
    """
    # Generate invoice number
    invoice_date = datetime.now()
    invoice_num = f"INV-{invoice_date.strftime('%Y%m%d')}-{hash(client_name) % 1000:03d}"
    due_date = invoice_date + timedelta(days=payment_terms)
    
    # Calculate totals
    subtotal = 0
    items_formatted = []
    
    for i, item in enumerate(line_items, 1):
        description = item.get("description", "Service")
        hours = float(item.get("hours", 1))
        rate = float(item.get("rate", 0))
        amount = hours * rate
        subtotal += amount
        
        items_formatted.append(f"| {i} | {description} | {hours:.1f} | ${rate:,.2f} | ${amount:,.2f} |")
    
    items_table = "\n".join(items_formatted)
    
    invoice = f"""# INVOICE

---

**Invoice Number:** {invoice_num}
**Invoice Date:** {invoice_date.strftime('%B %d, %Y')}
**Due Date:** {due_date.strftime('%B %d, %Y')}

---

## Bill To

**{client_name}**
{client_email}

---

## Services

| # | Description | Hours | Rate | Amount |
|---|-------------|-------|------|--------|
{items_table}

---

| | | | **Subtotal:** | **${subtotal:,.2f}** |
| | | | **Tax:** | $0.00 |
| | | | **TOTAL DUE:** | **${subtotal:,.2f}** |

---

## Payment Terms

- Payment due within **{payment_terms} days** of invoice date
- Late payments subject to **1.5% monthly** late fee
- Accepted methods: Bank transfer, PayPal, Wise

"""
    
    if notes:
        invoice += f"""## Notes

{notes}

"""
    
    invoice += """## Payment Instructions

**Bank Transfer:**
- Bank: [Your Bank Name]
- Account Name: [Your Name]
- Routing: [Routing Number]
- Account: [Account Number]

**PayPal:** [your@email.com]

---

Thank you for your business!
"""
    
    return invoice


@tool(args_schema=CollectionLetterInput)
@track_tool
async def draft_collection_letter(
    client_name: str,
    amount_owed: float,
    days_overdue: int,
    previous_attempts: int = 0,
    project_description: str = ""
) -> str:
    """
    Generate professional collection letters with escalating tone.
    Provides multiple versions: friendly, firm, and final demand.
    """
    today = datetime.now().strftime("%B %d, %Y")
    
    # Determine letter type based on history
    if previous_attempts == 0 or days_overdue < 30:
        letter_type = "friendly"
    elif previous_attempts < 2 or days_overdue < 60:
        letter_type = "firm"
    else:
        letter_type = "final"
    
    letters = {
        "friendly": f"""## Friendly Reminder (First Contact)

**Subject:** Friendly Reminder: Invoice Payment Due

---

Dear {client_name},

I hope this message finds you well! I wanted to follow up regarding the outstanding balance of **${amount_owed:,.2f}** for {project_description}.

The payment is now **{days_overdue} days** past the due date. I understand that things can get busy, so I wanted to send a quick reminder.

Could you please let me know when I might expect payment? If there are any issues or if you'd like to discuss payment options, I'm happy to work something out.

Thank you for your attention to this matter!

Best regards,
[Your Name]

---

**Next Step:** Wait 7 days, then send Firm Reminder
""",
        "firm": f"""## Firm Reminder (Second Attempt)

**Subject:** URGENT: Payment Required - {days_overdue} Days Overdue

---

Dear {client_name},

This is a follow-up regarding your outstanding balance of **${amount_owed:,.2f}** for {project_description}, which is now **{days_overdue} days overdue**.

Despite my previous reminder, I have not received payment or any communication regarding this invoice.

**Please arrange payment within 7 days** to avoid:
- Additional late fees
- Suspension of any ongoing work
- Potential escalation to collections

If you're experiencing financial difficulties, please contact me immediately to discuss a payment plan.

I look forward to your prompt response.

Regards,
[Your Name]

---

**Next Step:** Wait 7 days, then send Final Demand
""",
        "final": f"""## Final Demand (Before Legal Action)

**Subject:** FINAL NOTICE: Payment Required Within 10 Days

---

Dear {client_name},

**THIS IS A FINAL DEMAND FOR PAYMENT.**

You have an outstanding balance of **${amount_owed:,.2f}** for {project_description}, which is now **{days_overdue} days overdue**.

This is my final attempt to resolve this matter directly before pursuing other options.

**If full payment is not received within 10 days**, I will have no choice but to:
1. Report this debt to credit agencies
2. Engage a collection agency
3. Pursue legal action in small claims court

All associated legal fees and collection costs will be added to your balance.

**To avoid these actions, please remit payment immediately** via:
- Bank transfer
- PayPal
- Certified check

If you believe there is an error or wish to discuss this matter, you must contact me within 5 business days.

This letter serves as formal notice of my intent to pursue collection.

Regards,
[Your Name]

---

**Next Step:** If no response in 10 days, file small claims court or engage collection agency
"""
    }
    
    result = f"""# Collection Letters for {client_name}

**Amount Owed:** ${amount_owed:,.2f}
**Days Overdue:** {days_overdue}
**Previous Attempts:** {previous_attempts}
**Recommended Letter:** {letter_type.upper()}

---

{letters[letter_type]}

---

## All Letter Versions

{letters['friendly']}

{letters['firm']}

{letters['final']}
"""
    
    return result


@tool(args_schema=ScopeCreepInput)
@track_tool
async def estimate_project_value(
    original_scope: str,
    additional_requests: List[str],
    hourly_rate: float,
    original_estimate_hours: float
) -> str:
    """
    Calculate the value of scope creep and provide change order template.
    Estimates hours for additional requests and total impact.
    """
    # Estimate hours based on request complexity (simplified heuristic)
    complexity_keywords = {
        "high": ["redesign", "rebuild", "new feature", "major change", "complete overhaul", "integration"],
        "medium": ["update", "modify", "add", "change", "adjust", "revise"],
        "low": ["tweak", "fix", "minor", "small", "quick"]
    }
    
    additional_items = []
    total_additional_hours = 0
    
    for request in additional_requests:
        request_lower = request.lower()
        
        # Estimate complexity
        if any(kw in request_lower for kw in complexity_keywords["high"]):
            hours = 8  # 1 day
            complexity = "HIGH"
        elif any(kw in request_lower for kw in complexity_keywords["low"]):
            hours = 1  # 1 hour
            complexity = "LOW"
        else:
            hours = 4  # Half day
            complexity = "MEDIUM"
        
        total_additional_hours += hours
        cost = hours * hourly_rate
        additional_items.append({
            "request": request,
            "complexity": complexity,
            "hours": hours,
            "cost": cost
        })
    
    original_value = original_estimate_hours * hourly_rate
    additional_value = total_additional_hours * hourly_rate
    total_project_value = original_value + additional_value
    scope_increase_pct = (total_additional_hours / original_estimate_hours) * 100 if original_estimate_hours > 0 else 0
    
    items_table = "\n".join([
        f"| {i+1} | {item['request'][:40]}... | {item['complexity']} | {item['hours']}h | ${item['cost']:,.2f} |"
        for i, item in enumerate(additional_items)
    ])
    
    return f"""## Scope Creep Analysis

### Original Project
| Metric | Value |
|--------|-------|
| **Hours Estimated** | {original_estimate_hours:.1f} hours |
| **Hourly Rate** | ${hourly_rate:,.2f} |
| **Original Value** | ${original_value:,.2f} |

### Additional Requests ({len(additional_requests)} items)

| # | Request | Complexity | Hours | Cost |
|---|---------|------------|-------|------|
{items_table}

### Impact Summary

| Metric | Value |
|--------|-------|
| **Additional Hours** | {total_additional_hours:.1f} hours |
| **Additional Cost** | ${additional_value:,.2f} |
| **Scope Increase** | {scope_increase_pct:.1f}% |
| **NEW TOTAL** | **${total_project_value:,.2f}** |

---

## Change Order Template

```
CHANGE ORDER

Project: [Original Project Name]
Date: {datetime.now().strftime("%B %d, %Y")}

The following additional work has been requested:

{chr(10).join([f"- {item['request']}" for item in additional_items])}

Estimated Additional Cost: ${additional_value:,.2f}
Revised Project Total: ${total_project_value:,.2f}

By signing below, Client agrees to the additional scope and fees.

_____________________     _____________________
Client Signature          Date

_____________________     _____________________
Contractor Signature      Date
```

---

## Recommendations

1. **Never do unpaid work** - Always get change orders signed first
2. **Document everything** - Keep written records of all requests
3. **Set boundaries early** - Reference original scope when declining
4. {"⚠️ **WARNING:** Scope has increased by over 30%. Consider renegotiating entire project." if scope_increase_pct > 30 else "Scope increase is manageable with proper change order."}
"""


# =============================================================================
# Tool Registry
# =============================================================================

FINANCIAL_TOOLS = [
    calculate_overdue_amount,
    generate_invoice,
    draft_collection_letter,
    estimate_project_value,
]
