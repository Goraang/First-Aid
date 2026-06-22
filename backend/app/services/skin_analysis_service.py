"""
Skin Analysis Service — Intelligent keyword-based disease matching with medicine recommendations.

Features:
  - Image feature extraction via OpenCV (color, texture, tone)
  - Disease scoring against skin_diseases.json
  - Returns recommended medicines + alternative medicines for the detected condition
  - Integrates with medicines database for full medicine data
"""
import json
import os
import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# ── Optional CV2 ─────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# ── Database caches ───────────────────────────────────────────
_diseases_cache: Optional[List[Dict]] = None
_medicines_cache: Optional[List[Dict]] = None


def _db_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), f'../../database/{filename}')


def load_diseases_database() -> List[Dict]:
    """Load and cache the skin diseases database."""
    global _diseases_cache
    if _diseases_cache is not None:
        return _diseases_cache
    try:
        with open(_db_path('skin_diseases.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            _diseases_cache = data.get('skin_diseases', [])
            logger.info(f"Loaded {len(_diseases_cache)} skin diseases")
            return _diseases_cache
    except Exception as e:
        logger.error(f"Skin diseases DB load error: {e}")
        return []


def load_medicines_database() -> List[Dict]:
    """Load and cache the medicines database."""
    global _medicines_cache
    if _medicines_cache is not None:
        return _medicines_cache
    try:
        with open(_db_path('medicines.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            _medicines_cache = data.get('medicines', [])
            logger.info(f"Loaded {len(_medicines_cache)} medicines")
            return _medicines_cache
    except Exception as e:
        logger.error(f"Medicines DB load error: {e}")
        return []


# ── Image feature extraction ──────────────────────────────────
def analyze_image_features(image_path: str) -> dict:
    """
    Extract color and texture features from the skin image.
    Returns a dict with clues for disease matching.
    """
    base = {
        'red_percentage': 0.0,
        'white_percentage': 0.0,
        'brown_percentage': 0.0,
        'edge_density': 0.0,
        'color_variance': 1000.0,
        'brightness': 128.0,
        'dominant_tone': 'unknown',
        'texture': 'unknown',
    }

    if not image_path or not os.path.exists(image_path):
        return base

    if not HAS_CV2:
        return base

    try:
        image = cv2.imread(image_path)
        if image is None:
            return base

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Red channel: captures inflammation, rashes, erythema
        lower_red1 = np.array([0, 60, 60])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 60, 60])
        upper_red2 = np.array([180, 255, 255])
        mask_r = cv2.bitwise_or(
            cv2.inRange(hsv, lower_red1, upper_red1),
            cv2.inRange(hsv, lower_red2, upper_red2)
        )
        red_pct = float(np.sum(mask_r > 0) / mask_r.size * 100)

        # White/silvery areas: vitiligo, psoriasis scales
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        white_pct = float(np.sum(mask_white > 0) / mask_white.size * 100)

        # Brown/tan: hyperpigmentation, melasma
        lower_brown = np.array([10, 40, 40])
        upper_brown = np.array([30, 255, 200])
        mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
        brown_pct = float(np.sum(mask_brown > 0) / mask_brown.size * 100)

        # Yellow/crusted: impetigo (honey-colored crusts), seborrheic dermatitis
        lower_yellow = np.array([20, 80, 100])
        upper_yellow = np.array([35, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        yellow_pct = float(np.sum(mask_yellow > 0) / mask_yellow.size * 100)

        # Edge density: rough/scaly texture
        edges = cv2.Canny(gray, 80, 200)
        edge_density = float(np.sum(edges > 0) / edges.size * 100)

        brightness = float(np.mean(gray))
        color_variance = float(np.var(image))

        # Derive dominant tone
        if white_pct > 20:
            dominant_tone = 'pale_white'
        elif red_pct > 15:
            dominant_tone = 'red_inflamed'
        elif brown_pct > 20:
            dominant_tone = 'brown_pigmented'
        elif yellow_pct > 10:
            dominant_tone = 'yellow_crusted'
        elif brightness < 80:
            dominant_tone = 'dark'
        else:
            dominant_tone = 'normal'

        # Texture roughness
        if edge_density > 15:
            texture = 'rough_scaly'
        elif edge_density > 7:
            texture = 'textured'
        else:
            texture = 'smooth'

        return {
            'red_percentage': red_pct,
            'white_percentage': white_pct,
            'brown_percentage': brown_pct,
            'yellow_percentage': yellow_pct,
            'edge_density': edge_density,
            'color_variance': color_variance,
            'brightness': brightness,
            'dominant_tone': dominant_tone,
            'texture': texture,
        }

    except Exception as e:
        logger.error(f"Image feature analysis error: {e}")
        return base


# ── Disease scoring ───────────────────────────────────────────
def _score_disease(disease: dict, features: dict, body_part: str,
                   symptom_text: str = '') -> float:
    """
    Score a disease against all available context signals.
    Higher score = better match.
    """
    score = 0.0
    body_part_l = body_part.lower()
    symptom_l = symptom_text.lower()

    keywords = [k.lower() for k in disease.get('keywords', [])]
    affected = [a.lower() for a in disease.get('affected_areas', [])]
    disease_name = disease.get('name', '').lower()
    description = disease.get('description', '').lower()
    symptoms_list = [s.lower() for s in disease.get('symptoms', [])]

    # 1. Body part matches affected areas
    if body_part_l and body_part_l != 'unknown':
        for area in affected:
            if body_part_l in area or any(word in area for word in body_part_l.split()):
                score += 2.5
                break

    # 2. Symptom text keyword matching (highest weight)
    if symptom_l:
        for kw in keywords:
            if kw in symptom_l:
                score += 3.0
        for sym in symptoms_list:
            sym_words = [w for w in sym.split() if len(w) > 3]
            if sum(1 for w in sym_words if w in symptom_l) >= 2:
                score += 2.0
            elif any(w in symptom_l for w in sym_words):
                score += 0.8
        # Direct disease name in symptom text
        disease_first = disease_name.split()[0] if disease_name else ''
        if disease_first and len(disease_first) > 3 and disease_first in symptom_l:
            score += 5.0
        # Description word overlap with symptoms
        desc_words = set(re.findall(r'[a-z]{5,}', description))
        symp_words = set(re.findall(r'[a-z]{4,}', symptom_l))
        overlap = len(desc_words & symp_words) / max(len(symp_words), 1)
        score += overlap * 2.5

    # 3. Image feature hints
    tone = features.get('dominant_tone', 'unknown')
    texture = features.get('texture', 'unknown')
    red_pct = features.get('red_percentage', 0)
    white_pct = features.get('white_percentage', 0)
    brown_pct = features.get('brown_percentage', 0)
    yellow_pct = features.get('yellow_percentage', 0)

    combined_text = ' '.join(keywords) + ' ' + description

    # Pale/white → vitiligo, psoriasis (scale), tinea versicolor
    if tone == 'pale_white' or white_pct > 20:
        white_kws = ['white patches', 'vitiligo', 'leucoderma', 'depigment',
                     'pityriasis', 'versicolor', 'pale', 'hypopigment', 'silver scale']
        if any(wk in combined_text for wk in white_kws):
            score += 3.0

    # Red/inflamed → eczema, psoriasis, rosacea, urticaria, contact dermatitis
    if tone == 'red_inflamed' or red_pct > 15:
        red_kws = ['red', 'inflamed', 'erythema', 'redness', 'rash', 'urticaria',
                   'eczema', 'psoriasis', 'dermatitis', 'impetigo', 'ring', 'rosacea']
        if any(rk in combined_text for rk in red_kws):
            score += 2.5

    # Rough/scaly → psoriasis, ringworm, seborrheic dermatitis
    if texture == 'rough_scaly' or features.get('edge_density', 0) > 15:
        scaly_kws = ['scaly', 'scale', 'flaking', 'plaque', 'psoriasis', 'tinea',
                     'seborrheic', 'ichthyosis', 'rough', 'keratosis', 'ringworm']
        if any(sk in combined_text for sk in scaly_kws):
            score += 2.5

    # Brown/pigmented → melasma, post-inflammatory hyperpigmentation
    if tone == 'brown_pigmented' or brown_pct > 15:
        brown_kws = ['brown', 'pigment', 'hyperpigment', 'melasma', 'dark patches',
                     'discolour', 'post-inflammatory', 'chloasma']
        if any(bk in combined_text for bk in brown_kws):
            score += 3.0

    # Yellow/crusted → impetigo, seborrheic dermatitis
    if tone == 'yellow_crusted' or yellow_pct > 10:
        yellow_kws = ['honey', 'crust', 'impetigo', 'seborrheic', 'yellow']
        if any(yk in combined_text for yk in yellow_kws):
            score += 2.5

    # 4. Prevalence bonus (breaks ties in favour of common conditions)
    prev_bonus = {'very_high': 1.0, 'high': 0.6, 'moderate': 0.3, 'low': 0.0}
    score += prev_bonus.get(disease.get('india_prevalence', 'moderate'), 0.3)

    return score


# ── Medicine lookup ───────────────────────────────────────────
def get_full_medicine_data(name_or_salt: str, medicines_db: List[Dict]) -> Optional[Dict]:
    """Find a medicine by name, generic name, salt, or brand name."""
    query = name_or_salt.lower().strip()
    for med in medicines_db:
        if (query in med.get('name', '').lower() or
                query in med.get('generic_name', '').lower() or
                query in med.get('salt_composition', '').lower() or
                any(query in b.lower() for b in med.get('brand_names', []))):
            return med
    return None


def build_medicine_recommendations(
    disease: Dict,
    medicines_db: List[Dict]
) -> Dict:
    """
    Build primary and alternative medicine recommendations for a skin disease.

    Returns:
      primary:      medicines directly listed in disease.recommended_medicines
      alternative:  medicines for same condition via NLP mapping (different salts)
      all_for_condition: combined & de-duplicated, sorted by efficacy
    """
    from app.services.nlp_service import find_medicines_for_skin_condition

    recommended_names = disease.get('recommended_medicines', [])
    disease_name = disease.get('name', '')

    # Get all medicines for the condition
    all_meds = find_medicines_for_skin_condition(
        disease_name, medicines_db, recommended_names, top_n=10
    )

    # Split into primary (from DB recommendations) and alternatives
    rec_names_lower = {n.lower() for n in recommended_names}
    primary = []
    alternatives = []

    for med in all_meds:
        is_primary = any(
            r in med.get('name', '').lower() or
            r in med.get('generic_name', '').lower() or
            r in med.get('salt_composition', '').lower()
            for r in rec_names_lower
        )
        if is_primary:
            primary.append(med)
        else:
            alternatives.append(med)

    return {
        'primary_medicines': primary,
        'alternative_medicines': alternatives,
        'all_for_condition': all_meds,
    }


# ── Main disease matching ─────────────────────────────────────
def match_disease_from_features(
    features: dict,
    body_part: str = 'unknown',
    symptom_text: str = ''
) -> Optional[dict]:
    """
    Intelligently match a skin disease using feature scoring.
    Returns the best-matched disease with confidence and medicine recommendations.
    """
    try:
        diseases = load_diseases_database()
        medicines_db = load_medicines_database()

        if not diseases:
            logger.warning("No diseases in database")
            return None

        # Score all diseases
        scored = []
        for disease in diseases:
            s = _score_disease(disease, features, body_part, symptom_text)
            scored.append((s, disease))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_disease = scored[0]

        # Confidence calibration: score of 0 → 0.55, score of 15+ → 0.95
        max_possible = 18.0
        raw_conf = min(best_score / max_possible, 1.0)
        confidence = round(0.55 + raw_conf * 0.40, 2)

        logger.info(
            f"Best skin match: '{best_disease.get('name')}' "
            f"score={best_score:.2f} confidence={confidence:.2f}"
        )

        # Build top alternatives (next 4)
        top_alternatives = [
            {
                'name': d.get('name'),
                'id': d.get('id'),
                'severity': d.get('severity'),
                'confidence': round(0.55 + min(s / max_possible, 1.0) * 0.30, 2)
            }
            for s, d in scored[1:5]
            if s > 0
        ]

        # Medicine recommendations
        med_recs = build_medicine_recommendations(best_disease, medicines_db)

        return {
            'disease': best_disease,
            'confidence': confidence,
            'body_part': body_part,
            'analysis_timestamp': datetime.now().isoformat(),
            'top_alternatives': top_alternatives,
            'recommended_medicines': med_recs['primary_medicines'],
            'alternative_medicines': med_recs['alternative_medicines'],
        }

    except Exception as e:
        logger.error(f"Disease matching error: {e}")
        return None


# ── Main public entry point ───────────────────────────────────
def analyze_skin_condition(
    image_path: str,
    body_part: str = 'unknown',
    symptom_text: str = ''
) -> dict:
    """
    Main entry point for skin condition analysis.

    Args:
        image_path:    Path to uploaded image
        body_part:     User-reported body part (e.g. 'face', 'arm', 'scalp')
        symptom_text:  Optional free-text symptoms provided by the user

    Returns:
        dict with disease info, confidence, alternatives, and medicine recommendations
    """
    try:
        logger.info(
            f"Analyzing skin image: {os.path.basename(image_path)}, "
            f"body_part={body_part}"
        )

        features = analyze_image_features(image_path)
        logger.info(
            f"Image features: tone={features.get('dominant_tone')}, "
            f"texture={features.get('texture')}, "
            f"red%={features.get('red_percentage', 0):.1f}"
        )

        result = match_disease_from_features(features, body_part, symptom_text)

        if not result:
            return {'error': 'Could not identify condition', 'confidence': 0}

        return result

    except Exception as e:
        logger.error(f"Skin analysis error: {e}")
        return {'error': f'Analysis failed: {str(e)}', 'confidence': 0}


# ── Treatment recommendations helper ─────────────────────────
def get_treatment_recommendations(disease_name: str) -> list:
    """Get treatment recommendations for a named disease."""
    try:
        diseases = load_diseases_database()
        disease = next(
            (d for d in diseases if d['name'].lower() == disease_name.lower()), None
        )
        if disease:
            treatments = disease.get('treatments', disease.get('treatment', []))
            if isinstance(treatments, str):
                return [treatments]
            return treatments
        return ['Consult a qualified dermatologist for an accurate diagnosis and treatment plan.']
    except Exception as e:
        logger.error(f"Treatment retrieval error: {e}")
        return ['Consult a healthcare professional.']


def get_alternative_medicines_for_condition(
    disease_name: str,
    top_n: int = 6
) -> List[Dict]:
    """
    Public helper: get alternative medicines for a skin condition by name.
    Returns full medicine dicts sorted by efficacy.
    """
    try:
        medicines_db = load_medicines_database()
        diseases_db = load_diseases_database()
        disease = next(
            (d for d in diseases_db if d.get('name', '').lower() == disease_name.lower()),
            None
        )
        recommended_names = disease.get('recommended_medicines', []) if disease else []
        from app.services.nlp_service import find_medicines_for_skin_condition
        return find_medicines_for_skin_condition(
            disease_name, medicines_db, recommended_names, top_n=top_n
        )
    except Exception as e:
        logger.error(f"Alternative medicines error: {e}")
        return []
