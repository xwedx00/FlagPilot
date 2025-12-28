"""
Communication Tools
====================
Tools for professional messaging, email drafting, and sentiment analysis.
"""

from typing import Optional, List
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger
import re

from .base import track_tool


# =============================================================================
# Input Schemas
# =============================================================================

class EmailDraftInput(BaseModel):
    """Input for professional email drafting."""
    purpose: str = Field(..., description="Purpose of email: proposal, follow_up, negotiation, thank_you, decline")
    recipient_name: str = Field(..., description="Recipient's name")
    context: str = Field(..., description="Context and key points to include")
    tone: str = Field(default="professional", description="Tone: professional, friendly, firm, apologetic")


class SentimentInput(BaseModel):
    """Input for sentiment analysis."""
    text: str = Field(..., description="Text to analyze for sentiment and tone")


class TranslateInput(BaseModel):
    """Input for translation."""
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(default="spanish", description="Target language")
    formality: str = Field(default="formal", description="Formality level: formal, informal")


# =============================================================================
# Email Templates
# =============================================================================

EMAIL_TEMPLATES = {
    "proposal": """Subject: Proposal: {subject}

Hi {name},

Thank you for considering me for this project. Based on our conversation, I'm excited to submit my proposal.

## Project Understanding
{context}

## Proposed Approach
I would approach this by [approach details]. This ensures quality results while meeting your timeline.

## Investment
[Rate/package details]

## Timeline
[Estimated timeline]

## Next Steps
If this aligns with your needs, I'm available for a quick call to discuss details. Just reply to this email or book a time at [calendar link].

Looking forward to potentially working together!

Best regards,
[Your Name]""",
    
    "follow_up": """Subject: Following Up: {subject}

Hi {name},

I hope you're doing well. I wanted to follow up on our previous conversation about {context}.

I'm still very interested in this opportunity and would love to move forward when you're ready. Is there any additional information I can provide?

Let me know if now isn't a good time — I'm happy to check back in a few weeks instead.

Best,
[Your Name]""",
    
    "negotiation": """Subject: Re: Project Discussion

Hi {name},

Thank you for sharing the project details. I've reviewed everything and I'm excited about the opportunity.

Regarding the proposed rate, I wanted to share some context on my pricing:

{context}

Based on this, I'd like to propose [your counter-offer]. This reflects both the value I'll bring and ensures I can dedicate the attention this project deserves.

I'm confident we can find an arrangement that works for both of us. What are your thoughts?

Best regards,
[Your Name]""",
    
    "thank_you": """Subject: Thank You!

Hi {name},

I just wanted to take a moment to thank you for {context}.

Working with you has been a great experience, and I truly appreciate the opportunity.

If there's anything else I can help with in the future, please don't hesitate to reach out. I'd be happy to collaborate again.

Best wishes,
[Your Name]""",
    
    "decline": """Subject: Re: {subject}

Hi {name},

Thank you so much for thinking of me for this opportunity. After careful consideration, I've decided this isn't the right fit for me at this time.

{context}

I wish you all the best with the project, and I hope we can work together on something in the future.

Best regards,
[Your Name]""",
}


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=EmailDraftInput)
@track_tool
async def draft_professional_email(
    purpose: str,
    recipient_name: str,
    context: str,
    tone: str = "professional"
) -> str:
    """
    Generate a professional email draft for various business purposes.
    Provides multiple versions and tips for effective communication.
    """
    purpose_key = purpose.lower().replace(" ", "_")
    
    # Get base template
    if purpose_key not in EMAIL_TEMPLATES:
        purpose_key = "follow_up"  # Default
    
    template = EMAIL_TEMPLATES[purpose_key]
    
    # Generate subject
    subjects = {
        "proposal": f"Proposal for Your Project",
        "follow_up": f"Following Up on Our Discussion",
        "negotiation": f"Thoughts on Project Terms",
        "thank_you": f"Thank You",
        "decline": f"Regarding Your Opportunity",
    }
    subject = subjects.get(purpose_key, "Following Up")
    
    # Apply template
    email = template.format(
        name=recipient_name,
        subject=subject,
        context=context
    )
    
    # Adjust tone
    if tone == "friendly":
        email = email.replace("Best regards,", "Cheers,")
        email = email.replace("I hope you're doing well.", "Hope you're having a great week!")
    elif tone == "firm":
        email = email.replace("I wanted to", "I need to")
        email = email.replace("would love to", "would like to")
    elif tone == "apologetic":
        email = "I hope this finds you well. I wanted to reach out regarding... " + email
    
    # Add tips
    tips = {
        "proposal": """
### Proposal Tips
1. **Lead with their needs**, not your services
2. **Include social proof** if available
3. **Make next steps clear** and easy
4. **Follow up in 3-5 days** if no response
""",
        "follow_up": """
### Follow-up Tips
1. **Be brief** — respect their time
2. **Provide value** — share a resource or insight
3. **Don't be needy** — give them an easy out
4. **2-3 follow-ups max** before moving on
""",
        "negotiation": """
### Negotiation Tips
1. **Stay collaborative** — you're on the same team
2. **Justify your position** with data/value
3. **Offer alternatives** — maybe payment terms or scope
4. **Know your minimum** before you start
""",
        "decline": """
### Declining Tips
1. **Be gracious** — leave the door open
2. **Be brief** — no explanation needed
3. **Suggest alternatives** if possible
4. **Don't apologize excessively**
""",
    }
    
    return f"""## Email Draft: {purpose.title()}

### Version 1 ({tone.title()} Tone)

```
{email}
```

{tips.get(purpose_key, '')}

---

### Customization Points

- Replace `[Your Name]` with your actual name
- Add specific project details in `[brackets]`
- Personalize with any shared connections or context
- Add a PS for important last thoughts

### Alternative Subject Lines

1. "{subject}"
2. "Quick question about [project]"
3. "Following up + [value add]"
"""


@tool(args_schema=SentimentInput)
@track_tool
async def analyze_sentiment(
    text: str
) -> str:
    """
    Analyze the sentiment and tone of a message.
    Detects emotional cues, urgency, and potential red flags in communication.
    """
    text_lower = text.lower()
    
    # Sentiment indicators
    positive_words = [
        "thank", "great", "excellent", "appreciate", "wonderful", "excited",
        "love", "happy", "pleased", "perfect", "awesome", "fantastic",
        "amazing", "helpful", "impressed"
    ]
    
    negative_words = [
        "disappointed", "frustrated", "upset", "angry", "unacceptable",
        "terrible", "awful", "worst", "hate", "never", "problem",
        "complaint", "refund", "cancel", "sue", "lawyer"
    ]
    
    urgent_words = [
        "urgent", "asap", "immediately", "now", "deadline", "critical",
        "emergency", "right away", "today", "hurry"
    ]
    
    passive_aggressive = [
        "per my last email", "as i mentioned", "going forward",
        "i would have thought", "i'm confused why", "with all due respect",
        "as per your request", "just to be clear"
    ]
    
    # Count matches
    positive_count = sum(1 for w in positive_words if w in text_lower)
    negative_count = sum(1 for w in negative_words if w in text_lower)
    urgent_count = sum(1 for w in urgent_words if w in text_lower)
    pa_count = sum(1 for phrase in passive_aggressive if phrase in text_lower)
    
    # Analyze punctuation
    exclamation_count = text.count('!')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    question_count = text.count('?')
    
    # Calculate overall sentiment
    sentiment_score = positive_count - (negative_count * 2)
    
    if sentiment_score > 2:
        sentiment = "POSITIVE"
        emoji = "😊"
    elif sentiment_score < -2:
        sentiment = "NEGATIVE"
        emoji = "😤"
    else:
        sentiment = "NEUTRAL"
        emoji = "😐"
    
    # Detect tone issues
    tone_flags = []
    if urgent_count > 0:
        tone_flags.append("⏰ Urgency detected")
    if pa_count > 0:
        tone_flags.append("⚠️ Passive-aggressive language detected")
    if caps_ratio > 0.3:
        tone_flags.append("📢 Excessive capitals (may seem like shouting)")
    if exclamation_count > 3:
        tone_flags.append("❗ Many exclamation marks (over-enthusiastic or frustrated)")
    if negative_count > 3:
        tone_flags.append("🔴 Multiple negative words (client may be upset)")
    
    # Recommendations
    if sentiment == "NEGATIVE":
        recommendation = """
### Recommended Response Approach
1. **Acknowledge their frustration** first
2. **Don't be defensive** — listen actively
3. **Propose a solution** before explaining
4. **Follow up proactively** after resolution
5. **Consider a call** instead of more emails
"""
    elif pa_count > 0:
        recommendation = """
### Recommended Response Approach
1. **Read carefully** for underlying issues
2. **Address concerns directly** but diplomatically
3. **Avoid matching their tone** — stay professional
4. **Clarify expectations** going forward
"""
    else:
        recommendation = """
### Recommended Response Approach
1. **Match their energy** appropriately
2. **Respond promptly** if urgent signals present
3. **Keep it concise** and professional
"""
    
    return f"""## Sentiment Analysis

### Overall Sentiment: {emoji} {sentiment}

| Indicator | Count | Impact |
|-----------|-------|--------|
| Positive words | {positive_count} | +{positive_count} |
| Negative words | {negative_count} | -{negative_count * 2} |
| Urgency signals | {urgent_count} | ⏰ |
| Passive-aggressive | {pa_count} | ⚠️ |

### Tone Flags
{chr(10).join(tone_flags) if tone_flags else "✅ No concerning tone patterns detected"}

### Message Statistics
- Length: {len(text)} characters
- Questions asked: {question_count}
- Exclamation marks: {exclamation_count}
- Caps ratio: {caps_ratio*100:.0f}%

{recommendation}
"""


@tool(args_schema=TranslateInput)
@track_tool
async def translate_message(
    text: str,
    target_language: str = "spanish",
    formality: str = "formal"
) -> str:
    """
    Provide translation guidance and key phrases for professional communication.
    Note: For production, integrate with DeepL or Google Translate API.
    """
    # Common business phrases (expanded in production)
    phrase_translations = {
        "spanish": {
            "formal": {
                "Hello": "Estimado/a",
                "Thank you": "Muchas gracias",
                "Looking forward to hearing from you": "Quedo a la espera de su respuesta",
                "Best regards": "Atentamente",
                "Please let me know": "Por favor, hágamelo saber",
                "I appreciate your time": "Agradezco su tiempo",
            },
            "informal": {
                "Hello": "Hola",
                "Thank you": "Gracias",
                "Looking forward to hearing from you": "Espero tu respuesta",
                "Best regards": "Saludos",
                "Please let me know": "Avísame",
                "I appreciate your time": "Gracias por tu tiempo",
            }
        },
        "french": {
            "formal": {
                "Hello": "Madame, Monsieur",
                "Thank you": "Je vous remercie",
                "Looking forward to hearing from you": "Dans l'attente de votre réponse",
                "Best regards": "Cordialement",
                "Please let me know": "Veuillez me faire savoir",
                "I appreciate your time": "Je vous remercie pour votre temps",
            },
            "informal": {
                "Hello": "Bonjour",
                "Thank you": "Merci",
                "Best regards": "Bien à toi",
            }
        },
        "german": {
            "formal": {
                "Hello": "Sehr geehrte Damen und Herren",
                "Thank you": "Vielen Dank",
                "Looking forward to hearing from you": "Ich freue mich auf Ihre Antwort",
                "Best regards": "Mit freundlichen Grüßen",
            }
        },
    }
    
    lang_key = target_language.lower()
    form_key = formality.lower()
    
    if lang_key not in phrase_translations:
        return f"""## Translation Assistance

**Target Language:** {target_language.title()}

⚠️ Detailed phrase library for {target_language} is not available.

### Recommended Actions:
1. Use **DeepL** (deepl.com) for high-quality professional translations
2. For legal/contract documents, hire a professional translator
3. Use **Google Translate** for initial drafts, then have a native speaker review

### Key Tips for Professional Translation:
- Keep sentences short and clear
- Avoid idioms and slang
- Use formal pronouns when in doubt
- Have a native speaker review important communications
"""
    
    phrases = phrase_translations[lang_key].get(form_key, phrase_translations[lang_key].get("formal", {}))
    
    result = f"""## Translation Assistance: {target_language.title()} ({formality.title()})

### Common Business Phrases

| English | {target_language.title()} |
|---------|{'-' * len(target_language)}|
"""
    
    for eng, trans in phrases.items():
        result += f"| {eng} | {trans} |\n"
    
    result += f"""

### Original Text
```
{text}
```

### Translation Notes

⚠️ **Important:** This provides phrase guidance only. For accurate full translation:
1. Use **DeepL** (deepl.com) - best quality
2. Use **Google Translate** - widely available
3. For contracts/legal: Use certified translator

### Cultural Tips for {target_language.title()}
"""
    
    cultural_tips = {
        "spanish": """- Use formal "usted" for business (not "tú")
- Greetings are important — don't skip them
- Last names are double (maternal + paternal)
- Be aware of regional variations (Spain vs Latin America)""",
        "french": """- Use "vous" (formal you) in business
- Titles are important (Monsieur, Madame)
- Keep a formal tone until invited otherwise
- Written French tends to be more formal than spoken""",
        "german": """- German business communication is very formal
- Use full titles (Herr Doktor, etc.)
- Punctuality and directness are valued
- Keep small talk minimal"""
    }
    
    result += cultural_tips.get(lang_key, "Research cultural norms for your specific audience.")
    
    return result


# =============================================================================
# Tool Registry
# =============================================================================

COMMUNICATION_TOOLS = [
    draft_professional_email,
    analyze_sentiment,
    translate_message,
]
