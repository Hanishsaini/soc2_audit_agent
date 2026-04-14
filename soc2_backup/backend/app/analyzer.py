import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from .pdf_parser import get_text_snippet

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SOC2_CONTROL_INFO = {
    "CC1.1": "COSO Principle 1: Integrity and ethical values",
    "CC1.2": "COSO Principle 2: Board independence and oversight",
    "CC6.1": "Logical access security",
    "CC6.2": "User access provisioning",
    "CC6.3": "Security awareness training",
    "CC7.1": "Change management",
    "CC7.2": "Risk assessment",
    "CC8.1": "Vendor risk management",
}

def call_groq(prompt: str) -> dict:
    """Call Groq API with retry on rate limit."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                wait_time = (attempt + 1) * 30  # 30s, 60s, 90s
                print(f"⏳ Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Groq rate limit persisted after retries.")

def analyze_controls(control_ids: list, document_text: str) -> list:
    results = []
    # Reduce context size to save tokens (fewer rate limits)
    text_preview = document_text[:3000]

    for cid in control_ids:
        description = SOC2_CONTROL_INFO.get(cid, "SOC2 control")
        prompt = f"""You are a senior SOC2 auditor. Based on the document excerpt, evaluate control **{cid}** ({description}).

Return JSON with:
- "status": "covered", "partial", or "gap"
- "confidence": 0.0-1.0
- "rationale": one sentence
- "recommendation": one concrete action
- "keyword": a key term from the document

Document excerpt:
{text_preview}
"""
        try:
            data = call_groq(prompt)
            keyword = data.get("keyword", cid)
            snippet = get_text_snippet(document_text, keyword)

            results.append({
                "control_id": cid,
                "status": data.get("status", "error"),
                "confidence": data.get("confidence", 0.0),
                "rationale": data.get("rationale", "No rationale provided."),
                "recommendation": data.get("recommendation", "No recommendation available."),
                "evidence_snippet": snippet
            })
            
            # Small delay between requests to avoid burst rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error analyzing {cid}: {e}")
            results.append({
                "control_id": cid,
                "status": "error",
                "confidence": 0.0,
                "rationale": f"Analysis failed: {str(e)}",
                "recommendation": "Unable to generate recommendation.",
                "evidence_snippet": ""
            })
    return results