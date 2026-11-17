"""
Gemini Service for Medical AI.
Direct integration with Google Gemini 2.5 Flash for:
- Medicine scanning and pharmaceutical enrichment
- Dermatology skin lesion analysis
- Universal symptom triage and clinical assessment
"""
import os
import json
import logging
from google import genai
from google.genai import types
from PIL import Image

logger = logging.getLogger(__name__)

def get_gemini_client():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY is not configured.")
        return None
    return genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

def analyze_medicine_image_with_gemini(image_path: str) -> dict:
    """Analyze a medicine package/strip/bottle image directly with Gemini."""
    client = get_gemini_client()
    if not client:
        return {'error': 'Gemini API key not configured'}

    prompt = """
You are an expert pharmaceutical AI. Analyze this medicine image carefully.
Identify the brand name, active ingredients (salts/composition), dosage strength, category/type, manufacturer if visible, uses, dosage instructions, side effects, warnings, and safe alternatives with the same active salts.

Return ONLY a valid JSON object matching this schema:
{
  "name": "Brand/Trade Name",
  "generic_name": "Generic Name",
  "salt_composition": "Active Salt Composition with strength, e.g., Paracetamol 500mg",
  "dosage_form": "Tablet / Syrup / Cream / Capsule / etc.",
  "strength": "e.g., 500mg",
  "manufacturer": "Manufacturer name or Unknown",
  "category": "Analgesic / Antibiotic / Antihistamine / etc.",
  "usage": "Primary medical usage and conditions treated",
  "dosage": "Standard adult dosage and usage directions",
  "side_effects": ["Side effect 1", "Side effect 2", "Side effect 3"],
  "warnings": ["Warning 1", "Warning 2"],
  "contraindications": ["Contraindication 1", "Contraindication 2"],
  "price_inr": "Estimated price range in INR (e.g. ₹30 - ₹50)",
  "confidence": 0.95,
  "alternatives": [
    {
      "name": "Alternative Brand 1",
      "generic_name": "Generic Name",
      "salt_composition": "Salt",
      "price_inr": "₹30",
      "manufacturer": "Brand Manufacturer"
    }
  ]
}
"""
    try:
        img = Image.open(image_path)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        text = response.text.strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Gemini medicine analysis failed: {e}", exc_info=True)
        return {'error': str(e)}

def analyze_skin_image_with_gemini(image_path: str = None, symptoms: str = "", body_part: str = "unknown") -> dict:
    """Analyze skin condition from image and symptoms using Gemini Vision."""
    client = get_gemini_client()
    if not client:
        return {'error': 'Gemini API key not configured'}

    prompt = f"""
You are an expert dermatological AI clinical assistant.
User details:
- Body part: {body_part}
- Symptoms described: {symptoms or 'No symptoms described'}

Analyze the skin condition based on the image (if provided) and reported symptoms.
Provide a clinical differential diagnosis, severity assessment, causes, home care/treatments, emergency signs, and recommended topical/oral medicines.

Return ONLY a valid JSON object with this exact structure:
{{
  "disease": {{
    "name": "Primary suspected skin disease / condition",
    "scientific_name": "Medical/Latin terminology",
    "category": "Fungal / Bacterial / Viral / Inflammatory / Allergic / Parasitic",
    "severity": "Mild / Moderate / Severe",
    "urgency": "Routine / Consult Doctor Soon / Immediate Emergency",
    "description": "Comprehensive explanation of the condition",
    "causes": ["Cause 1", "Cause 2", "Cause 3"],
    "symptoms": ["Symptom 1", "Symptom 2", "Symptom 3"],
    "risk_factors": ["Risk 1", "Risk 2"],
    "prevention": ["Prevention tip 1", "Prevention tip 2"]
  }},
  "confidence": 0.92,
  "top_alternatives": [
    {{
      "name": "Differential Diagnosis 1",
      "confidence": 0.65,
      "description": "Why this is also possible"
    }},
    {{
      "name": "Differential Diagnosis 2",
      "confidence": 0.45,
      "description": "Why this is also possible"
    }}
  ],
  "recommended_medicines": [
    {{
      "name": "Medicine Name (e.g. Clotrimazole 1% Cream)",
      "generic_name": "Generic Name",
      "salt_composition": "Active Salt",
      "type": "Topical Cream / Oral Tablet / etc.",
      "usage": "How and when to apply/take",
      "dosage": "Application frequency (e.g. Twice daily for 2 weeks)",
      "side_effects": ["Mild stinging", "Redness"],
      "warnings": ["For external use only"],
      "price_inr": "₹80 - ₹150",
      "recommendation_reason": "First-line antifungal/antibacterial treatment"
    }}
  ],
  "alternative_medicines": [
    {{
      "name": "Alternative Medicine Name",
      "generic_name": "Generic Name",
      "salt_composition": "Active Salt",
      "type": "Topical / Oral",
      "usage": "Usage details",
      "dosage": "Dosage details",
      "side_effects": ["Side effect"],
      "warnings": ["Warning"],
      "price_inr": "₹100",
      "recommendation_reason": "Alternative option if primary is unavailable"
    }}
  ],
  "treatments": [
    {{
      "step": 1,
      "title": "Clean and Dry",
      "description": "Wash area gently with mild soap and pat dry"
    }},
    {{
      "step": 2,
      "title": "Medication Application",
      "description": "Apply thin layer of recommended topical medicine"
    }}
  ],
  "lifestyle_tips": [
    "Keep the affected area clean and dry",
    "Avoid scratching to prevent secondary bacterial infection",
    "Wear loose-fitting, breathable cotton clothing"
  ],
  "when_to_see_doctor": [
    "Condition worsens or does not improve after 7 days",
    "Development of fever, chills, or spreading red streaks",
    "Severe pain or pus formation"
  ]
}}
"""
    try:
        contents = []
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            contents.append(img)
        contents.append(prompt)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini dermatology analysis failed: {e}", exc_info=True)
        return {'error': str(e)}

def analyze_symptoms_with_gemini(symptoms: str, body_part: str = "unknown", category: str = None) -> dict:
    """Analyze general medical symptoms directly with Gemini."""
    client = get_gemini_client()
    if not client:
        return {'error': 'Gemini API key not configured'}

    prompt = f"""
You are an expert clinical triage AI.
User reports:
- Symptoms: {symptoms}
- Body part / region: {body_part}
- Category: {category or 'General'}

Analyze these symptoms, assess potential underlying conditions, urgency level, first-aid measures, and safe OTC medications.

Return ONLY a valid JSON object matching this schema:
{{
  "top_match": {{
    "name": "Most likely primary condition",
    "confidence": 0.88,
    "severity": "Mild / Moderate / Severe / Critical",
    "description": "Clinical overview of the suspected condition",
    "common_causes": ["Cause 1", "Cause 2"],
    "typical_duration": "3-7 days"
  }},
  "differential_diagnoses": [
    {{
      "name": "Differential 1",
      "confidence": 0.60,
      "distinguishing_factor": "Key distinguishing symptom"
    }},
    {{
      "name": "Differential 2",
      "confidence": 0.40,
      "distinguishing_factor": "Key distinguishing symptom"
    }}
  ],
  "emergency": false,
  "emergency_warning": null,
  "urgency_level": "Home care / Consult GP / Urgent Care / Emergency Room",
  "first_aid_steps": [
    "Step 1: Immediate self-care instruction",
    "Step 2: Rest and hydration"
  ],
  "recommended_otc_medications": [
    {{
      "name": "Medication Name",
      "salt": "Active ingredient",
      "purpose": "What symptom it relieves",
      "dosage": "Standard OTC dosage",
      "warnings": "Important warning"
    }}
  ],
  "red_flags": [
    "High fever (>103°F) not responding to antipyretics",
    "Difficulty breathing or chest tightness",
    "Sudden confusion or lethargy"
  ],
  "disclaimer": "This AI assessment is for informational and educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment."
}}
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini symptom analysis failed: {e}", exc_info=True)
        return {'error': str(e)}

def search_medicines_with_gemini(query: str) -> list:
    """Search or ask Gemini about any medicine or salt name dynamically."""
    client = get_gemini_client()
    if not client:
        return []

    prompt = f"""
Search or describe medicines matching the user query: "{query}".
Return a JSON array of up to 5 matching medicines with comprehensive medical details:
[
  {{
    "id": "med_query_slug",
    "name": "Brand Name",
    "generic_name": "Generic Name",
    "salt_composition": "Active Salt(s)",
    "category": "Category",
    "dosage_form": "Tablet / Syrup / etc.",
    "usage": "Indications",
    "dosage": "Standard Dosage",
    "side_effects": ["Side effect 1", "Side effect 2"],
    "warnings": ["Warning 1"],
    "price_inr": "₹XX - ₹YY",
    "confidence": 0.95
  }}
]
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini medicine search failed: {e}", exc_info=True)
        return []
