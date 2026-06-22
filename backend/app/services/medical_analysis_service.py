"""
Medical Analysis Service — Universal multi-category disease detection.
Loads both skin diseases and general diseases, scores all conditions
against free-text symptoms + image features + body part context.
"""
import json
import os
import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Database caches ───────────────────────────────────────────
_skin_cache: Optional[List[Dict]] = None
_general_cache: Optional[List[Dict]] = None

# ── Symptom clusters for category pre-classification ──────────
SYMPTOM_CLUSTERS = {
    'respiratory': [
        'cough', 'breathless', 'wheeze', 'wheezing', 'shortness', 'dyspnoea',
        'sputum', 'phlegm', 'chest', 'lung', 'inhaler', 'asthma', 'bronchial',
        'pneumonia', 'tb', 'tuberculosis', 'haemoptysis', 'copd'
    ],
    'cardiovascular': [
        'chest pain', 'heart', 'palpitation', 'palpitations', 'cardiac',
        'angina', 'myocardial', 'hypertension', 'blood pressure', 'bp',
        'stroke', 'tia', 'fainting', 'syncope', 'ankle swelling', 'oedema',
        'edema', 'arrhythmia', 'tachycardia', 'bradycardia'
    ],
    'gastrointestinal': [
        'stomach', 'abdominal', 'abdomen', 'nausea', 'vomiting', 'diarrhoea',
        'diarrhea', 'constipation', 'heartburn', 'acidity', 'reflux', 'ulcer',
        'liver', 'jaundice', 'yellow', 'hepatitis', 'bowel', 'indigestion',
        'bloating', 'rectal', 'anal', 'haematemesis', 'melaena'
    ],
    'neurological': [
        'headache', 'migraine', 'seizure', 'convulsion', 'fit', 'stroke',
        'weakness', 'paralysis', 'numbness', 'tingling', 'confusion',
        'memory', 'dizziness', 'vertigo', 'fainting', 'tremor', 'epilepsy',
        'meningitis', 'neck stiff', 'vision loss', 'diplopia'
    ],
    'dermatology': [
        'rash', 'skin', 'itch', 'itching', 'redness', 'blister', 'patch',
        'spots', 'bumps', 'pimples', 'acne', 'eczema', 'psoriasis', 'hives',
        'urticaria', 'swelling skin', 'lesion', 'wound', 'ulcer skin',
        'hair loss', 'alopecia', 'nail', 'fungal', 'ringworm'
    ],
    'endocrine': [
        'diabetes', 'blood sugar', 'thyroid', 'weight gain', 'weight loss',
        'thirst', 'urination', 'fatigue thyroid', 'pcos', 'polycystic',
        'insulin', 'glucose', 'hba1c', 'hypothyroid', 'hyperthyroid',
        'cushing', 'adrenal', 'hormonal'
    ],
    'infectious': [
        'fever', 'malaria', 'dengue', 'typhoid', 'infection', 'viral',
        'bacterial', 'leptospirosis', 'cholera', 'tuberculosis', 'hiv',
        'covid', 'influenza', 'flu', 'worm', 'parasite', 'tropical'
    ],
    'mental_health': [
        'depression', 'anxiety', 'panic', 'worry', 'stress', 'mood',
        'suicidal', 'bipolar', 'schizophrenia', 'hallucination', 'ocd',
        'ptsd', 'phobia', 'social anxiety', 'insomnia', 'sleep'
    ],
    'renal': [
        'kidney', 'urine', 'urinary', 'dysuria', 'uti', 'renal',
        'proteinuria', 'haematuria', 'blood in urine', 'kidney stone',
        'nephrotic', 'nephritis', 'dialysis', 'creatinine', 'ureter'
    ],
    'musculoskeletal': [
        'joint', 'arthritis', 'bone', 'muscle', 'back pain', 'knee pain',
        'hip pain', 'shoulder', 'stiffness', 'gout', 'uric acid',
        'rheumatoid', 'osteoarthritis', 'spondylitis', 'fibromyalgia'
    ],
    'haematological': [
        'anaemia', 'anemia', 'pale', 'pallor', 'haemoglobin', 'hemoglobin',
        'iron deficiency', 'leukaemia', 'lymphoma', 'platelet', 'bleeding',
        'bruising', 'sickle cell', 'thalassaemia', 'blood disorder'
    ],
    'ophthalmological': [
        'eye', 'vision', 'sight', 'blind', 'glaucoma', 'cataract',
        'retina', 'conjunctivitis', 'red eye', 'blurred vision', 'floater',
        'diabetic retinopathy', 'macular', 'cornea', 'iris'
    ],
    'ent': [
        'ear', 'nose', 'throat', 'tonsil', 'sore throat', 'hearing',
        'rhinitis', 'sinusitis', 'sneezing', 'allergy nose', 'vertigo',
        'tinnitus', 'deafness', 'nasal', 'pharyngitis', 'laryngitis'
    ],
    'gynaecological': [
        'period', 'menstrual', 'menstruation', 'pcos', 'ovary', 'uterus',
        'endometriosis', 'fibroid', 'pregnancy', 'vaginal', 'cervical',
        'breast', 'irregular periods', 'fertility', 'gynaecological'
    ]
}

# ── Red-flag keywords that escalate severity ──────────────────
RED_FLAG_PATTERNS = [
    (r'chest pain.{0,30}(left arm|jaw|neck|sweat)', 'cardiac_emergency'),
    (r'sudden.{0,20}(weakness|paralysis|vision|speech)', 'stroke_emergency'),
    (r'(cannot|can\'t|unable to).{0,20}breath', 'respiratory_emergency'),
    (r'(vomiting|coughing).{0,10}blood', 'gi_haemorrhage'),
    (r'(stiff neck|neck stiff).{0,20}fever', 'meningitis_emergency'),
    (r'non.{0,5}blanching.{0,20}rash', 'meningococcal_emergency'),
    (r'(unconscious|collapse|unresponsive)', 'emergency'),
    (r'blood.{0,10}urine.{0,20}(severe|flank|back)', 'renal_emergency'),
    (r'suicidal|want to die|end my life', 'mental_health_emergency'),
]

# ── Negation detection ────────────────────────────────────────
NEGATION_WORDS = [
    'no ', 'not ', 'without ', 'no history of ', 'denies ', 'absent ',
    'never ', 'none ', "didn't ", "don't have ", "no "
]


def load_skin_diseases() -> List[Dict]:
    """Load and cache the skin diseases database."""
    global _skin_cache
    if _skin_cache is not None:
        return _skin_cache
    db_path = os.path.join(os.path.dirname(__file__), '../../database/skin_diseases.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            diseases = data.get('skin_diseases', [])
            # Normalise to universal schema
            for d in diseases:
                d.setdefault('category', 'dermatology')
                d.setdefault('body_parts', d.get('affected_areas', []))
                d.setdefault('affected_systems', ['dermatological'])
                d.setdefault('red_flags', d.get('warning_signs', []))
            _skin_cache = diseases
            logger.info(f"Loaded {len(_skin_cache)} skin diseases")
            return _skin_cache
    except Exception as e:
        logger.error(f"Skin DB load error: {e}")
        return []


def load_general_diseases() -> List[Dict]:
    """Load and cache the general diseases database."""
    global _general_cache
    if _general_cache is not None:
        return _general_cache
    db_path = os.path.join(os.path.dirname(__file__), '../../database/general_diseases.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            diseases = data.get('general_diseases', [])
            # Normalise to legacy schema fields
            for d in diseases:
                d.setdefault('india_prevalence', 'moderate')
                d.setdefault('affected_areas', d.get('body_parts', []))
                d.setdefault('recommended_medicines', [])
                d.setdefault('warning_signs', d.get('red_flags', []))
            _general_cache = diseases
            logger.info(f"Loaded {len(_general_cache)} general diseases")
            return _general_cache
    except Exception as e:
        logger.error(f"General DB load error: {e}")
        return []


def load_all_diseases() -> List[Dict]:
    """Load all diseases from both databases."""
    return load_skin_diseases() + load_general_diseases()


def invalidate_cache():
    """Force reload of databases on next access."""
    global _skin_cache, _general_cache
    _skin_cache = None
    _general_cache = None


def detect_red_flags(symptom_text: str) -> List[str]:
    """Detect emergency red-flag patterns in symptom text."""
    flags = []
    text_lower = symptom_text.lower()
    for pattern, flag_type in RED_FLAG_PATTERNS:
        if re.search(pattern, text_lower):
            flags.append(flag_type)
    return flags


def has_negation(symptom_text: str, keyword: str) -> bool:
    """Check if a keyword appears after a negation word."""
    text_lower = symptom_text.lower()
    idx = text_lower.find(keyword.lower())
    if idx == -1:
        return False
    # Look at the 30 characters before the keyword
    prefix = text_lower[max(0, idx - 30):idx]
    return any(neg in prefix for neg in NEGATION_WORDS)


def classify_symptom_category(symptom_text: str) -> List[str]:
    """
    Classify symptom text into probable medical categories.
    Returns list of likely categories (could be multiple).
    """
    text_lower = symptom_text.lower()
    category_scores: Dict[str, float] = {}

    for category, keywords in SYMPTOM_CLUSTERS.items():
        score = 0.0
        for kw in keywords:
            if kw in text_lower:
                if not has_negation(symptom_text, kw):
                    score += 1.0
        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return []  # No classification — search all

    # Return categories above 50% of the max score
    max_score = max(category_scores.values())
    return [cat for cat, score in category_scores.items()
            if score >= max_score * 0.5]


def _similarity(a: str, b: str) -> float:
    """SequenceMatcher ratio."""
    try:
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
    except Exception:
        return 0.0


def _score_disease_universal(disease: Dict, symptom_text: str,
                             body_part: str, image_features: Optional[Dict] = None,
                             candidate_categories: Optional[List[str]] = None) -> float:
    """
    Universal disease scoring function.
    Returns a float score — higher = better match.
    """
    score = 0.0
    symptom_l = symptom_text.lower()
    body_part_l = body_part.lower()

    keywords = [k.lower() for k in disease.get('keywords', [])]
    symptoms_list = [s.lower() for s in disease.get('symptoms', [])]
    description = disease.get('description', '').lower()
    disease_name = disease.get('name', '').lower()
    disease_category = disease.get('category', 'general').lower()

    affected_areas = [a.lower() for a in disease.get('affected_areas', [])]
    body_parts = [b.lower() for b in disease.get('body_parts', [])]
    all_areas = affected_areas + body_parts

    # ── 1. Category pre-filter boost ────────────────────────
    if candidate_categories and disease_category in candidate_categories:
        score += 1.5

    # ── 2. Body part matching ────────────────────────────────
    if body_part_l and body_part_l not in ('unknown', ''):
        for area in all_areas:
            # Check if either contains the other (handles partial matches)
            if body_part_l in area or any(word in area for word in body_part_l.split()):
                score += 2.5
                break

    # ── 3. Keyword matching (highest weight) ────────────────
    for kw in keywords:
        if kw in symptom_l:
            if not has_negation(symptom_text, kw):
                score += 3.0

    # ── 4. Symptom list matching ─────────────────────────────
    for sym in symptoms_list:
        # Match individual meaningful words from symptom string
        sym_words = [w for w in sym.split() if len(w) > 4]
        matched = sum(1 for w in sym_words if w in symptom_l and not has_negation(symptom_text, w))
        if matched >= 2:
            score += 1.5
        elif matched == 1:
            score += 0.5

    # ── 5. Disease name direct match ─────────────────────────
    disease_first_word = disease_name.split()[0] if disease_name else ''
    if disease_first_word and len(disease_first_word) > 3 and disease_first_word in symptom_l:
        score += 5.0
    # Fuzzy name match
    fuzzy = _similarity(symptom_l[:80], disease_name)
    if fuzzy > 0.6:
        score += fuzzy * 3.0

    # ── 6. Description keyword matching ─────────────────────
    desc_words = [w for w in re.findall(r'[a-z]{5,}', description)]
    symp_words = set(re.findall(r'[a-z]{4,}', symptom_l))
    desc_overlap = len(symp_words & set(desc_words)) / max(len(symp_words), 1)
    score += desc_overlap * 2.0

    # ── 7. Image feature scoring (skin diseases) ─────────────
    if image_features:
        tone = image_features.get('dominant_tone', 'unknown')
        texture = image_features.get('texture', 'unknown')
        red_pct = image_features.get('red_percentage', 0)
        white_pct = image_features.get('white_percentage', 0)
        brown_pct = image_features.get('brown_percentage', 0)
        edge_density = image_features.get('edge_density', 0)

        combined_text = ' '.join(keywords) + ' ' + description

        if tone == 'pale_white' or white_pct > 20:
            white_kws = ['white', 'pale', 'vitiligo', 'depigment', 'hypopigment',
                        'versicolor', 'leucoderma']
            if any(wk in combined_text for wk in white_kws):
                score += 2.5

        if tone == 'red_inflamed' or red_pct > 15:
            red_kws = ['red', 'inflam', 'erythema', 'rash', 'urticaria',
                      'eczema', 'psoriasis', 'impetigo', 'dermatitis']
            if any(rk in combined_text for rk in red_kws):
                score += 2.0

        if texture == 'rough_scaly' or edge_density > 15:
            scaly_kws = ['scaly', 'scale', 'flak', 'plaque', 'psoriasis',
                        'tinea', 'seborrh', 'ichthy', 'keratosis']
            if any(sk in combined_text for sk in scaly_kws):
                score += 2.0

        if brown_pct > 15:
            brown_kws = ['brown', 'pigment', 'melanin', 'melasma', 'hyperpigment',
                        'dark patch', 'discolour']
            if any(bk in combined_text for bk in brown_kws):
                score += 2.0

    # ── 8. Prevalence bonus ──────────────────────────────────
    prev_bonus = {'very_high': 1.0, 'high': 0.6, 'moderate': 0.3, 'low': 0.0}
    score += prev_bonus.get(disease.get('india_prevalence', 'moderate'), 0.3)

    # ── 9. Severity penalty for very rare conditions ─────────
    # Prevents exotic diseases from scoring on weak evidence
    if disease.get('india_prevalence') == 'low' and score < 5.0:
        score *= 0.7

    return score


def analyze_symptoms(
    symptom_text: str,
    body_part: str = 'unknown',
    category_filter: Optional[str] = None,
    image_features: Optional[Dict] = None,
    top_n: int = 5
) -> Dict:
    """
    Main universal symptom analysis entry point.

    Args:
        symptom_text:     Free-text description of symptoms
        body_part:        Affected body part or system
        category_filter:  Optional: restrict to one category ('respiratory', etc.)
        image_features:   Optional: image analysis results from skin_analysis_service
        top_n:            Number of top matches to return

    Returns:
        dict with top matches, differential, red_flags, category
    """
    try:
        logger.info(f"Analyzing symptoms: '{symptom_text[:60]}...', body_part='{body_part}'")

        if not symptom_text or not symptom_text.strip():
            return {'error': 'No symptom text provided', 'matches': []}

        # Detect red flags
        red_flags = detect_red_flags(symptom_text)

        # Classify into categories
        candidate_categories = classify_symptom_category(symptom_text)
        if category_filter:
            candidate_categories = [category_filter]

        logger.info(f"Detected categories: {candidate_categories}, red_flags: {red_flags}")

        # Load appropriate disease set
        if category_filter == 'dermatology':
            diseases = load_skin_diseases()
        elif category_filter and category_filter != 'dermatology':
            diseases = load_general_diseases()
        else:
            diseases = load_all_diseases()

        # Score all diseases
        scored: List[Tuple[float, Dict]] = []
        for disease in diseases:
            s = _score_disease_universal(
                disease, symptom_text, body_part,
                image_features, candidate_categories
            )
            if s > 0:
                scored.append((s, disease))

        # Sort descending
        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return {
                'matches': [],
                'red_flags': red_flags,
                'categories': candidate_categories,
                'message': 'No matching conditions found. Please provide more specific symptoms.'
            }

        # Build top matches with confidence
        max_possible = 18.0
        matches = []
        for score, disease in scored[:top_n]:
            raw_conf = min(score / max_possible, 1.0)
            confidence = round(0.55 + raw_conf * 0.40, 2)

            match_entry = {
                'id': disease.get('id'),
                'name': disease.get('name'),
                'category': disease.get('category', 'general'),
                'scientific_name': disease.get('scientific_name', ''),
                'description': disease.get('description', ''),
                'confidence': confidence,
                'severity': disease.get('severity', 'moderate'),
                'symptoms': disease.get('symptoms', []),
                'treatments': disease.get('treatments', []),
                'recommended_medicines': disease.get('recommended_medicines', []),
                'warning_signs': disease.get('warning_signs', disease.get('red_flags', [])),
                'prevention': disease.get('prevention', []),
                'score': round(score, 2)
            }
            matches.append(match_entry)

        # Top match
        top_match = matches[0]
        alternatives = matches[1:top_n]

        logger.info(f"Top match: '{top_match['name']}' confidence={top_match['confidence']}")

        return {
            'top_match': top_match,
            'alternatives': alternatives,
            'red_flags': red_flags,
            'categories_detected': candidate_categories,
            'total_diseases_searched': len(diseases),
            'analysis_timestamp': datetime.now().isoformat(),
            'emergency': len(red_flags) > 0
        }

    except Exception as e:
        logger.error(f"Symptom analysis error: {e}")
        return {'error': str(e), 'matches': []}


def search_diseases(query: str, category: Optional[str] = None,
                    limit: int = 20) -> List[Dict]:
    """
    Full-text search across all diseases.
    Returns list of matching diseases sorted by relevance.
    """
    try:
        if not query or len(query) < 2:
            return []

        diseases = load_all_diseases()
        query_l = query.lower()
        results = []

        for disease in diseases:
            # Category filter
            if category and disease.get('category', '').lower() != category.lower():
                continue

            # Compute search score
            score = 0.0
            name = disease.get('name', '').lower()
            sci_name = disease.get('scientific_name', '').lower()
            desc = disease.get('description', '').lower()
            keywords = [k.lower() for k in disease.get('keywords', [])]

            if query_l in name:
                score += 10.0
            if query_l in sci_name:
                score += 8.0
            if any(query_l in kw for kw in keywords):
                score += 5.0
            if query_l in desc:
                score += 2.0

            # Fuzzy
            fuzzy = max(
                _similarity(query_l, name),
                _similarity(query_l, sci_name),
                max((_similarity(query_l, kw) for kw in keywords), default=0)
            )
            score += fuzzy * 3.0

            if score > 1.0:
                results.append((score, disease))

        results.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in results[:limit]]

    except Exception as e:
        logger.error(f"Disease search error: {e}")
        return []


def get_disease_by_id(disease_id: str) -> Optional[Dict]:
    """Get a specific disease by its ID from any database."""
    try:
        diseases = load_all_diseases()
        return next((d for d in diseases if d.get('id') == disease_id), None)
    except Exception as e:
        logger.error(f"Disease lookup error: {e}")
        return None


def get_categories_summary() -> List[Dict]:
    """Get a summary of all disease categories with counts."""
    try:
        diseases = load_all_diseases()
        from collections import Counter
        cat_counts = Counter(d.get('category', 'general') for d in diseases)
        return [
            {'category': cat, 'count': count,
             'display_name': cat.replace('_', ' ').title()}
            for cat, count in sorted(cat_counts.items())
        ]
    except Exception as e:
        logger.error(f"Categories error: {e}")
        return []


def get_database_stats() -> Dict:
    """Get statistics about the medical databases."""
    try:
        skin = load_skin_diseases()
        general = load_general_diseases()
        all_diseases = skin + general

        from collections import Counter
        severity_counts = Counter(d.get('severity', 'moderate') for d in all_diseases)
        cat_counts = Counter(d.get('category', 'general') for d in all_diseases)

        return {
            'total_diseases': len(all_diseases),
            'skin_diseases': len(skin),
            'general_diseases': len(general),
            'categories': len(cat_counts),
            'severity_breakdown': dict(severity_counts),
            'category_breakdown': dict(cat_counts)
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {}
