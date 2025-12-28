"""
Scam Detection Tools
====================
Tools for detecting scams, verifying companies, and analyzing suspicious communications.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger
import re
import hashlib

from .base import track_tool, ToolResult


# =============================================================================
# Input Schemas
# =============================================================================

class CompanyVerificationInput(BaseModel):
    """Input for company verification."""
    company_name: str = Field(..., description="Name of the company to verify")
    website: Optional[str] = Field(None, description="Company website URL")
    email_domain: Optional[str] = Field(None, description="Email domain used in communication")


class EmailAnalysisInput(BaseModel):
    """Input for email header analysis."""
    email_content: str = Field(..., description="Full email content or headers")
    sender_email: str = Field(..., description="Sender's email address")


class ScamCheckInput(BaseModel):
    """Input for scam database check."""
    text: str = Field(..., description="Job posting or message to analyze")
    contact_method: Optional[str] = Field(None, description="Contact method mentioned (telegram, whatsapp, etc)")


class ScamReportInput(BaseModel):
    """Input for generating scam report."""
    scam_type: str = Field(..., description="Type of scam (job, payment, romance, etc)")
    description: str = Field(..., description="Description of the scam")
    amount_lost: Optional[float] = Field(None, description="Amount of money lost, if any")
    contact_info: Optional[str] = Field(None, description="Scammer's contact information")


# =============================================================================
# Scam Pattern Database
# =============================================================================

SCAM_PATTERNS = {
    "telegram_job": {
        "keywords": ["telegram", "whatsapp", "signal"],
        "context": ["job", "work", "position", "hiring"],
        "risk_score": 90,
        "description": "Jobs requiring off-platform communication are almost always scams"
    },
    "check_scam": {
        "keywords": ["check", "e-check", "cashier's check", "money order"],
        "context": ["send", "deposit", "equipment", "supplies"],
        "risk_score": 95,
        "description": "Fake check scam - check will bounce after you send money"
    },
    "overpayment": {
        "keywords": ["overpay", "extra", "refund", "send back"],
        "context": ["payment", "check", "wire"],
        "risk_score": 98,
        "description": "Overpayment scam - they 'accidentally' pay too much"
    },
    "upfront_fee": {
        "keywords": ["fee", "deposit", "security", "equipment cost"],
        "context": ["start", "before", "required", "pay"],
        "risk_score": 85,
        "description": "Upfront fee scam - legitimate jobs never require payment"
    },
    "too_good": {
        "keywords": ["$50/hr", "$45/hr", "easy money", "work from home", "no experience"],
        "context": ["data entry", "simple", "easy", "immediate"],
        "risk_score": 80,
        "description": "Too-good-to-be-true offer - unrealistic compensation"
    },
    "urgency": {
        "keywords": ["urgent", "immediately", "today only", "act now", "limited spots"],
        "context": ["apply", "respond", "decision"],
        "risk_score": 70,
        "description": "False urgency - pressure tactics to prevent research"
    },
    "personal_info": {
        "keywords": ["ssn", "social security", "bank account", "id photo", "passport"],
        "context": ["send", "provide", "need", "verify"],
        "risk_score": 95,
        "description": "Identity theft attempt - never send personal docs before hiring"
    }
}


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=CompanyVerificationInput)
@track_tool
async def verify_company_existence(
    company_name: str,
    website: Optional[str] = None,
    email_domain: Optional[str] = None
) -> str:
    """
    Verify if a company exists and appears legitimate.
    Checks for red flags in company information and provides a legitimacy assessment.
    """
    results = []
    risk_flags = []
    trust_signals = []
    
    # Analyze company name
    name_lower = company_name.lower()
    
    # Red flags in company names
    suspicious_patterns = [
        (r'[0-9]{4,}', "Contains long number sequences"),
        (r'official|real|legit|certified', "Uses trust-seeking words"),
        (r'inc\s*$|llc\s*$|ltd\s*$', None),  # Normal - not a flag
    ]
    
    for pattern, flag in suspicious_patterns:
        if flag and re.search(pattern, name_lower):
            risk_flags.append(flag)
    
    # Analyze website if provided
    if website:
        website_lower = website.lower()
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq']
        if any(website_lower.endswith(tld) for tld in suspicious_tlds):
            risk_flags.append(f"Website uses suspicious TLD")
        
        # Check for misspellings of known brands
        brand_typos = ['googel', 'faceboook', 'linkdin', 'upwrok', 'fiverr']
        if any(typo in website_lower for typo in brand_typos):
            risk_flags.append("Website appears to be typosquatting a known brand")
        
        # Positive signals
        if website_lower.endswith('.com') or website_lower.endswith('.org'):
            trust_signals.append("Standard TLD (.com/.org)")
    
    # Analyze email domain if provided
    if email_domain:
        domain_lower = email_domain.lower()
        
        # Free email providers are suspicious for businesses
        free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        if domain_lower in free_providers:
            risk_flags.append("Using free email provider instead of company domain")
        
        # Check if email matches website
        if website:
            website_domain = website.replace('https://', '').replace('http://', '').split('/')[0]
            if website_domain.replace('www.', '') == domain_lower:
                trust_signals.append("Email domain matches website")
            else:
                risk_flags.append("Email domain doesn't match claimed website")
    
    # Calculate risk score
    risk_score = min(len(risk_flags) * 25, 100)
    trust_score = min(len(trust_signals) * 20, 50)
    final_score = max(0, 100 - risk_score + trust_score)
    
    # Build result
    result = f"""## Company Verification: {company_name}

### Legitimacy Score: {final_score}/100

### Trust Signals ✅
{chr(10).join(f'- {s}' for s in trust_signals) if trust_signals else '- None detected'}

### Risk Flags 🚩
{chr(10).join(f'- {f}' for f in risk_flags) if risk_flags else '- None detected'}

### Recommendation
"""
    
    if final_score >= 70:
        result += "Company appears potentially legitimate, but always verify through official channels."
    elif final_score >= 40:
        result += "⚠️ CAUTION: Several risk factors detected. Research thoroughly before proceeding."
    else:
        result += "🚨 HIGH RISK: Multiple red flags detected. This may be a scam operation."
    
    return result


@tool(args_schema=EmailAnalysisInput)
@track_tool
async def analyze_email_headers(
    email_content: str,
    sender_email: str
) -> str:
    """
    Analyze email content for signs of phishing, spoofing, or scam patterns.
    Checks sender legitimacy and content red flags.
    """
    red_flags = []
    
    content_lower = email_content.lower()
    sender_lower = sender_email.lower()
    
    # Check sender email
    free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    sender_domain = sender_email.split('@')[-1].lower() if '@' in sender_email else ''
    
    if sender_domain in free_providers:
        red_flags.append("Sender using free email provider for business communication")
    
    # Check for mismatched brand claims
    brand_keywords = ['amazon', 'paypal', 'bank', 'microsoft', 'apple', 'google', 'upwork', 'fiverr']
    for brand in brand_keywords:
        if brand in content_lower and brand not in sender_domain:
            red_flags.append(f"Claims to be from {brand.title()} but email domain doesn't match")
    
    # Check for urgency language
    urgency_phrases = [
        'act now', 'urgent', 'immediately', 'expires today', 
        'last chance', 'limited time', 'respond within'
    ]
    for phrase in urgency_phrases:
        if phrase in content_lower:
            red_flags.append(f"Uses urgency language: '{phrase}'")
            break
    
    # Check for suspicious links
    if 'bit.ly' in content_lower or 'tinyurl' in content_lower:
        red_flags.append("Contains shortened URLs hiding the real destination")
    
    # Check for personal information requests
    pii_requests = ['ssn', 'social security', 'bank account', 'password', 'credit card', 'routing number']
    for pii in pii_requests:
        if pii in content_lower:
            red_flags.append(f"Requesting sensitive information: {pii}")
    
    # Check for payment requests
    payment_methods = ['zelle', 'venmo', 'cash app', 'western union', 'gift card', 'bitcoin', 'crypto']
    for method in payment_methods:
        if method in content_lower:
            red_flags.append(f"Requests payment via {method} (non-reversible)")
    
    risk_score = min(len(red_flags) * 20, 100)
    
    result = f"""## Email Analysis

### Sender: {sender_email}
### Risk Score: {risk_score}/100

### Red Flags Detected
{chr(10).join(f'- 🚩 {f}' for f in red_flags) if red_flags else '- ✅ No obvious red flags detected'}

### Assessment
"""
    
    if risk_score >= 60:
        result += """🚨 **HIGH RISK**: This email shows multiple signs of being a scam or phishing attempt.
**DO NOT** click any links, download attachments, or respond with personal information."""
    elif risk_score >= 30:
        result += "⚠️ **CAUTION**: Some suspicious elements detected. Verify sender through official channels before responding."
    else:
        result += "✅ **LOW RISK**: No obvious red flags, but always verify unexpected requests independently."
    
    return result


@tool(args_schema=ScamCheckInput)
@track_tool
async def check_scam_database(
    text: str,
    contact_method: Optional[str] = None
) -> str:
    """
    Check text against known scam patterns and return risk assessment.
    Uses pattern matching against database of known freelance scam indicators.
    """
    text_lower = text.lower()
    detected_patterns = []
    
    # Check each scam pattern
    for pattern_name, pattern_data in SCAM_PATTERNS.items():
        keyword_matches = sum(1 for k in pattern_data["keywords"] if k in text_lower)
        context_matches = sum(1 for c in pattern_data["context"] if c in text_lower)
        
        if keyword_matches > 0 and context_matches > 0:
            detected_patterns.append({
                "pattern": pattern_name,
                "risk_score": pattern_data["risk_score"],
                "description": pattern_data["description"],
                "keyword_matches": keyword_matches
            })
    
    # Additional check for contact method
    if contact_method:
        contact_lower = contact_method.lower()
        if any(app in contact_lower for app in ["telegram", "whatsapp", "signal"]):
            detected_patterns.append({
                "pattern": "off_platform_contact",
                "risk_score": 85,
                "description": "Requests communication outside platform",
                "keyword_matches": 1
            })
    
    # Sort by risk score
    detected_patterns.sort(key=lambda x: x["risk_score"], reverse=True)
    
    if not detected_patterns:
        return """## Scam Check Results

### Risk Level: LOW ✅

No known scam patterns detected in this message.

**Note:** This doesn't guarantee safety. Always:
- Verify company independently
- Never pay upfront fees
- Keep communication on the platform
- Trust your instincts"""
    
    max_risk = max(p["risk_score"] for p in detected_patterns)
    
    result = f"""## Scam Check Results

### Risk Level: {'🚨 CRITICAL' if max_risk >= 90 else '⚠️ HIGH' if max_risk >= 70 else '⚠️ MEDIUM'} ({max_risk}%)

### Detected Scam Patterns

"""
    
    for p in detected_patterns:
        result += f"""**{p['pattern'].replace('_', ' ').title()}** (Risk: {p['risk_score']}%)
> {p['description']}

"""
    
    result += """### Immediate Actions
1. **DO NOT** send any money or personal information
2. **DO NOT** move conversation to Telegram/WhatsApp
3. **REPORT** this posting to the platform
4. **BLOCK** the sender if possible"""
    
    return result


@tool(args_schema=ScamReportInput)
@track_tool
async def generate_scam_report(
    scam_type: str,
    description: str,
    amount_lost: Optional[float] = None,
    contact_info: Optional[str] = None
) -> str:
    """
    Generate a formatted scam report for submission to FTC, IC3, or platform safety teams.
    Includes all relevant details in the required format.
    """
    # Generate unique report ID
    report_hash = hashlib.md5(f"{scam_type}{description}".encode()).hexdigest()[:8].upper()
    
    result = f"""## Scam Report Template

### Report ID: FP-{report_hash}

---

### For FTC (reportfraud.ftc.gov)

**Scam Type:** {scam_type.replace('_', ' ').title()}

**Description:**
{description}

**Financial Impact:** {"$" + f"{amount_lost:,.2f}" if amount_lost else "No money lost (attempt only)"}

**Scammer Contact Info:**
{contact_info if contact_info else "Not provided"}

---

### For FBI IC3 (ic3.gov)

Use the above information and add:
- Date/time of incident
- How you were contacted
- Any accounts or platforms involved
- Screenshots of conversations (if available)

---

### For Platform Safety Team

```
FRAUD REPORT

Type: {scam_type}
Description: {description[:200]}...

Evidence: [Attach screenshots]
User impact: {"Financial loss reported" if amount_lost else "No financial loss"}
```

---

### Next Steps

1. **File FTC report** at reportfraud.ftc.gov
2. **File IC3 report** at ic3.gov (if over $100 lost)
3. **Report to platform** where you encountered the scam
4. **Contact your bank** if you shared financial information
5. **Monitor credit** at annualcreditreport.com

{"⚠️ **URGENT:** You reported financial loss. Contact your bank IMMEDIATELY to dispute charges or stop transfers." if amount_lost else ""}
"""
    
    return result


# =============================================================================
# Tool Registry
# =============================================================================

SCAM_TOOLS = [
    verify_company_existence,
    analyze_email_headers,
    check_scam_database,
    generate_scam_report,
]
