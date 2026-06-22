"""
NLP Service — Multi-strategy medicine name matching with salt comparison.

Features:
  1. Multi-strategy matching: exact token, prefix/substring, fuzzy SequenceMatcher, per-line
  2. Salt/composition-boosted matching: if OCR extracts a salt name, use it for precise lookup
  3. compare_medicines_by_salt(): group brands by same active ingredient with price+efficacy sort
  4. find_medicines_for_skin_condition(): recommend medicines for a given skin disease
  5. Calibrated confidence output tied to actual match quality
"""
import re
import logging
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Basic text helpers
# ─────────────────────────────────────────────────────────────

def tokenize_text(text: str) -> List[str]:
    """Tokenize and clean text into lowercase alpha tokens (min 3 chars)."""
    return re.findall(r'[a-zA-Z]{3,}', text.lower())


def calculate_similarity(a: str, b: str) -> float:
    """Return SequenceMatcher similarity ratio (0–1)."""
    try:
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
    except Exception:
        return 0.0


def _all_names(medicine: dict) -> List[str]:
    """Collect every searchable name variant for a medicine."""
    names = []
    if medicine.get('name'):
        names.append(medicine['name'].lower())
    if medicine.get('generic_name'):
        names.append(medicine['generic_name'].lower())
    if medicine.get('salt_composition'):
        names.append(medicine['salt_composition'].lower())
    for brand in medicine.get('brand_names', []):
        names.append(brand.lower())
    return names


def _extract_key_tokens(text: str) -> List[str]:
    """
    Get meaningful tokens sorted by length (longer tokens are more specific).
    Filters very common English words that would create false matches.
    """
    stop_words = {
        'the', 'and', 'for', 'with', 'daily', 'each', 'take', 'once',
        'twice', 'tablet', 'tablets', 'capsule', 'capsules', 'every',
        'hour', 'hours', 'day', 'days', 'food', 'after', 'before',
        'store', 'batch', 'dose', 'dosage', 'directions', 'net', 'qty',
    }
    tokens = tokenize_text(text)
    return [t for t in tokens if len(t) >= 4 and t not in stop_words]


# ─────────────────────────────────────────────────────────────
#  Core medicine matching
# ─────────────────────────────────────────────────────────────

def find_best_medicine_match(
    extracted_text: str,
    medicines_db: List[Dict],
    threshold: float = 0.35,
    salt_hint: str = '',
) -> Optional[Dict]:
    """
    Find the best matching medicine using multiple strategies.

    Strategies (weighted combination):
      1. Salt/composition direct lookup (highest priority if available)
      2. Exact token overlap against name/generic/brand/salt
      3. Prefix / substring match
      4. Fuzzy SequenceMatcher on full text
      5. Per-line similarity scoring
      6. Length-weighted token importance

    Args:
        extracted_text: Raw OCR text from the image
        medicines_db:   List of medicine dicts
        threshold:      Minimum combined score to accept a match (0–1)
        salt_hint:      Optional salt name extracted from OCR to boost matching

    Returns:
        Best matching medicine dict with 'confidence' key, or None
    """
    if not medicines_db or not extracted_text.strip():
        return None

    text_clean = extracted_text.lower()
    tokens = _extract_key_tokens(text_clean)

    if not tokens:
        return None

    # ── Stage 0: salt-based direct lookup ────────────────────
    if salt_hint and len(salt_hint) > 3:
        salt_l = salt_hint.lower()
        for medicine in medicines_db:
            med_salt = medicine.get('salt_composition', '').lower()
            med_generic = medicine.get('generic_name', '').lower()
            med_name = medicine.get('name', '').lower()
            if (salt_l in med_salt or med_salt in salt_l or
                    salt_l in med_generic or med_name in salt_l or salt_l in med_name):
                result = dict(medicine)
                result['confidence'] = round(min(0.82 + calculate_similarity(salt_l, med_salt) * 0.13, 0.97), 3)
                result['match_method'] = 'salt_lookup'
                logger.info(
                    f"Salt-based match: '{result.get('name')}' "
                    f"(salt='{salt_hint}') confidence={result['confidence']:.3f}"
                )
                return result

    best_match: Optional[Dict] = None
    best_score: float = 0.0
    best_raw: float = 0.0

    for medicine in medicines_db:
        all_names = _all_names(medicine)
        med_tokens = tokenize_text(' '.join(all_names))

        # ── Strategy 1: exact token overlap ──────────────────
        # Weight longer tokens higher (more specific)
        exact_score = 0.0
        total_weight = 0.0
        for t in tokens:
            weight = len(t) / 10.0  # longer token → higher weight
            total_weight += weight
            if t in med_tokens:
                exact_score += weight
        token_score = (exact_score / total_weight) if total_weight > 0 else 0.0

        # ── Strategy 2: prefix / substring per token ─────────
        prefix_hits = 0
        for t in tokens:
            for mn in all_names:
                if len(t) >= 5 and (t in mn or mn.startswith(t[:5])):
                    prefix_hits += 1
                    break
                elif len(t) < 5 and t in mn:
                    prefix_hits += 1
                    break
        prefix_score = prefix_hits / max(len(tokens), 1)

        # ── Strategy 3: SequenceMatcher on full text vs each name ─
        fuzzy_score = max(
            calculate_similarity(text_clean[:200], name) for name in all_names
        ) if all_names else 0.0

        # ── Strategy 4: per-line text vs name matching ────────
        line_score = 0.0
        for line in extracted_text.split('\n'):
            line = line.strip()
            if not line or len(line) < 3:
                continue
            line_sim = max(
                calculate_similarity(line.lower(), name) for name in all_names
            ) if all_names else 0.0
            if line_sim > line_score:
                line_score = line_sim

        # ── Strategy 5: direct name-in-text check ────────────
        name_in_text = 0.0
        for name in all_names:
            if len(name) >= 5 and name in text_clean:
                name_in_text = 1.0
                break
            # partial: first 6 chars of name in text
            if len(name) >= 6 and name[:6] in text_clean:
                name_in_text = max(name_in_text, 0.7)

        # Combined weighted score
        combined = (
            token_score  * 0.30 +
            prefix_score * 0.15 +
            fuzzy_score  * 0.20 +
            line_score   * 0.20 +
            name_in_text * 0.15
        )

        if combined > best_score and combined >= threshold:
            best_score = combined
            best_raw = combined
            best_match = medicine

    if best_match:
        result = dict(best_match)
        # Calibrate: raw 0.35 → 0.60 confidence, raw 1.0 → 0.97
        calibrated = round(0.60 + best_raw * 0.37, 3)
        result['confidence'] = min(calibrated, 0.97)
        result['match_method'] = 'multi_strategy'
        logger.info(
            f"Medicine match: '{result.get('name')}' "
            f"raw={best_raw:.3f} confidence={result['confidence']:.3f}"
        )
        return result

    # ── Fallback: longest-token single match ──────────────────
    logger.info("Primary matching failed — trying single-token fallback")
    for token in sorted(tokens, key=len, reverse=True):
        if len(token) < 5:
            continue
        for medicine in medicines_db:
            for name in _all_names(medicine):
                if token in name or name.startswith(token[:6]):
                    result = dict(medicine)
                    result['confidence'] = 0.62
                    result['match_method'] = 'token_fallback'
                    logger.info(
                        f"Fallback match: '{result.get('name')}' via token '{token}'"
                    )
                    return result

    logger.warning(f"No medicine match found for text: {extracted_text[:100]!r}")
    return None


# ─────────────────────────────────────────────────────────────
#  Salt / composition comparison
# ─────────────────────────────────────────────────────────────

def compare_medicines_by_salt(
    salt_name: str,
    medicines_db: List[Dict],
    top_n: int = 10,
) -> Dict:
    """
    Find all medicines sharing the same or similar active ingredient/salt,
    then rank them by efficacy (highest first) and price (lowest first).

    Args:
        salt_name:    Active ingredient to search (e.g. "Cetirizine HCl")
        medicines_db: Full medicines list
        top_n:        Maximum results to return

    Returns:
        dict with salt, matched medicines sorted by efficacy & price,
        plus convenience fields: best_value, most_effective, cheapest
    """
    if not salt_name or not medicines_db:
        return {'salt': salt_name, 'medicines': [], 'error': 'No data'}

    salt_l = salt_name.lower().strip()

    # Compute similarity score for each medicine against the salt query
    scored: List[Tuple[float, Dict]] = []
    # Tokenize salt for word-level matching
    salt_tokens = set(tokenize_text(salt_l))

    for med in medicines_db:
        med_salt = med.get('salt_composition', '').lower()
        med_generic = med.get('generic_name', '').lower()
        med_name = med.get('name', '').lower()

        sim = 0.0

        # ── Tier 1: direct substring match (salt ↔ salt) ─────
        if med_salt and (salt_l in med_salt or med_salt in salt_l):
            sim = 0.90 + calculate_similarity(salt_l, med_salt) * 0.10

        # ── Tier 2: substring match with generic name ─────────
        elif med_generic and (salt_l in med_generic or med_generic in salt_l):
            sim = 0.82 + calculate_similarity(salt_l, med_generic) * 0.10

        # ── Tier 3: substring match with medicine name ────────
        elif salt_l in med_name or med_name in salt_l:
            sim = 0.75 + calculate_similarity(salt_l, med_name) * 0.10

        else:
            # ── Tier 4: token-level match ─────────────────────
            med_salt_tokens = set(tokenize_text(med_salt + ' ' + med_generic + ' ' + med_name))
            # Require at least one significant token to match (len >= 5)
            significant_salt_tokens = {t for t in salt_tokens if len(t) >= 5}
            significant_med_tokens = {t for t in med_salt_tokens if len(t) >= 5}
            if significant_salt_tokens and significant_med_tokens:
                overlap = len(significant_salt_tokens & significant_med_tokens)
                if overlap > 0:
                    sim = 0.60 + (overlap / max(len(significant_salt_tokens), 1)) * 0.20
            
            # Fall back to fuzzy only if no token match
            if sim == 0.0:
                fuzzy = max(
                    calculate_similarity(salt_l, med_salt) if med_salt else 0.0,
                    calculate_similarity(salt_l, med_generic) if med_generic else 0.0,
                    calculate_similarity(salt_l, med_name) if med_name else 0.0,
                )
                # Only accept high-confidence fuzzy matches to avoid false positives
                if fuzzy >= 0.72:
                    sim = fuzzy

        # Strict minimum: must have genuine semantic match
        if sim >= 0.65:
            scored.append((sim, med))

    if not scored:
        return {
            'salt': salt_name,
            'medicines': [],
            'message': f'No medicines found with composition similar to "{salt_name}"'
        }

    # Sort: primarily by relevance (descending), then by efficacy (descending)
    scored.sort(key=lambda x: (x[0], x[1].get('efficacy_rating', 0)), reverse=True)
    matched = [med for _, med in scored[:top_n]]

    # Build enriched result for each medicine
    def _enrich(med: Dict, rel_score: float) -> Dict:
        return {
            'id': med.get('id'),
            'name': med.get('name'),
            'generic_name': med.get('generic_name'),
            'salt_composition': med.get('salt_composition', ''),
            'brand_names': med.get('brand_names', []),
            'type': med.get('type'),
            'composition': med.get('composition'),
            'price_inr': med.get('price_inr'),
            'efficacy_rating': med.get('efficacy_rating'),
            'usage': med.get('usage'),
            'dosage': med.get('dosage'),
            'side_effects': med.get('side_effects', []),
            'warnings': med.get('warnings', []),
            'for_conditions': med.get('for_conditions', []),
            'relevance_score': round(rel_score, 3),
        }

    enriched = [_enrich(med, score) for score, med in scored[:top_n]]

    # Sort by efficacy for the final list (what user cares about most)
    by_efficacy = sorted(enriched, key=lambda m: m.get('efficacy_rating') or 0, reverse=True)
    by_price = sorted(
        [m for m in enriched if m.get('price_inr') is not None],
        key=lambda m: m.get('price_inr', 999)
    )

    most_effective = by_efficacy[0] if by_efficacy else None
    cheapest = by_price[0] if by_price else None

    # Best value: highest efficacy/price ratio
    def _value_ratio(m: Dict) -> float:
        eff = m.get('efficacy_rating') or 0
        price = m.get('price_inr') or 999
        return eff / (price / 10.0) if price > 0 else 0

    best_value_med = max(enriched, key=_value_ratio) if enriched else None

    logger.info(
        f"Salt comparison '{salt_name}': "
        f"{len(enriched)} medicines found, "
        f"most_effective='{most_effective['name'] if most_effective else 'N/A'}', "
        f"cheapest='{cheapest['name'] if cheapest else 'N/A'}'"
    )

    return {
        'salt': salt_name,
        'medicines': enriched,
        'total_found': len(enriched),
        'most_effective': most_effective,
        'cheapest': cheapest,
        'best_value': best_value_med,
        'comparison_note': (
            f"Comparison based on efficacy rating (out of 5) and "
            f"approximate Indian market price (INR per strip/unit)."
        )
    }


def get_medicines_by_id(medicine_id: str, medicines_db: List[Dict]) -> Optional[Dict]:
    """Fetch a medicine by its ID."""
    return next((m for m in medicines_db if m.get('id') == medicine_id), None)


# ─────────────────────────────────────────────────────────────
#  Skin-disease → medicine recommendations
# ─────────────────────────────────────────────────────────────

# Map disease name keywords to relevant medicine types/salts
_SKIN_DISEASE_MEDICINE_MAP = {
    'acne': ['Adapalene', 'Benzoyl Peroxide', 'Tretinoin', 'Doxycycline', 'Azelaic Acid', 'Azithromycin'],
    'eczema': ['Hydrocortisone', 'Betamethasone', 'Clobetasol Propionate', 'Cetirizine', 'Levocetirizine', 'Mupirocin'],
    'psoriasis': ['Betamethasone Valerate', 'Clobetasol Propionate', 'Hydrocortisone', 'Cetirizine'],
    'urticaria': ['Cetirizine HCl', 'Levocetirizine HCl', 'Fexofenadine HCl', 'Loratadine', 'Hydrocortisone'],
    'ringworm': ['Clotrimazole', 'Terbinafine HCl', 'Miconazole Nitrate', 'Ketoconazole'],
    'tinea': ['Clotrimazole', 'Terbinafine HCl', 'Miconazole Nitrate', 'Ketoconazole'],
    'fungal': ['Clotrimazole', 'Terbinafine HCl', 'Ketoconazole', 'Miconazole Nitrate'],
    'contact dermatitis': ['Hydrocortisone', 'Betamethasone Valerate', 'Cetirizine HCl', 'Calamine + Zinc Oxide'],
    'rosacea': ['Azelaic Acid', 'Doxycycline', 'Metronidazole cream'],
    'melasma': ['Tretinoin', 'Azelaic Acid', 'Hydrocortisone'],
    'vitiligo': ['Hydrocortisone', 'Betamethasone Valerate', 'Clobetasol Propionate'],
    'warts': ['Salicylic acid'],
    'seborrheic dermatitis': ['Ketoconazole', 'Hydrocortisone', 'Clotrimazole'],
    'cellulitis': ['Amoxicillin', 'Ciprofloxacin', 'Azithromycin'],
    'impetigo': ['Mupirocin', 'Fusidic Acid', 'Amoxicillin', 'Azithromycin'],
    'herpes simplex': ['Acyclovir'],
    'chickenpox': ['Acyclovir', 'Cetirizine HCl', 'Calamine + Zinc Oxide', 'Paracetamol'],
    'scabies': ['Permethrin'],
    'allergy': ['Cetirizine HCl', 'Levocetirizine HCl', 'Fexofenadine HCl', 'Loratadine'],
    'itching': ['Cetirizine HCl', 'Levocetirizine HCl', 'Calamine + Zinc Oxide', 'Hydrocortisone'],
    'rash': ['Hydrocortisone', 'Cetirizine HCl', 'Calamine + Zinc Oxide'],
}


def find_medicines_for_skin_condition(
    disease_name: str,
    medicines_db: List[Dict],
    recommended_medicine_names: Optional[List[str]] = None,
    top_n: int = 8,
) -> List[Dict]:
    """
    Recommend medicines for a given skin condition.

    Priority order:
    1. Medicines in recommended_medicine_names (from skin_diseases.json)
    2. Medicines mapped from _SKIN_DISEASE_MEDICINE_MAP
    3. Medicines whose for_conditions matches the disease

    Returns a de-duplicated list sorted by efficacy descending.
    """
    disease_l = disease_name.lower()
    found_ids = set()
    results: List[Dict] = []

    def _add_medicine(med: Dict, reason: str):
        if med.get('id') not in found_ids:
            found_ids.add(med.get('id'))
            enriched = dict(med)
            enriched['recommendation_reason'] = reason
            results.append(enriched)

    # ── Priority 1: direct recommended_medicine_names from DB ─
    if recommended_medicine_names:
        for rec_name in recommended_medicine_names:
            rec_l = rec_name.lower()
            for med in medicines_db:
                if (rec_l in med.get('name', '').lower() or
                        rec_l in med.get('generic_name', '').lower() or
                        rec_l in med.get('salt_composition', '').lower() or
                        any(rec_l in b.lower() for b in med.get('brand_names', []))):
                    _add_medicine(med, f'Recommended for {disease_name}')
                    break

    # ── Priority 2: disease map ───────────────────────────────
    mapped_salts = []
    for keyword, salts in _SKIN_DISEASE_MEDICINE_MAP.items():
        if keyword in disease_l or disease_l in keyword:
            mapped_salts.extend(salts)

    for salt in mapped_salts:
        salt_l = salt.lower()
        for med in medicines_db:
            if (salt_l in med.get('salt_composition', '').lower() or
                    salt_l in med.get('generic_name', '').lower() or
                    salt_l in med.get('name', '').lower()):
                _add_medicine(med, f'Indicated for {disease_name}')
                break

    # ── Priority 3: for_conditions field match ────────────────
    for med in medicines_db:
        for cond in med.get('for_conditions', []):
            if disease_l in cond.lower() or cond.lower() in disease_l:
                _add_medicine(med, f'Used to treat {disease_name}')
                break

    # Sort by efficacy rating (descending)
    results.sort(key=lambda m: m.get('efficacy_rating') or 0, reverse=True)
    return results[:top_n]


# ─────────────────────────────────────────────────────────────
#  Additional extraction helpers
# ─────────────────────────────────────────────────────────────

def extract_dosage_info(text: str) -> Optional[str]:
    """Extract the first dosage string found in OCR text."""
    try:
        patterns = [
            r'\d+(?:\.\d+)?\s*(?:mg|mcg|g|ug|IU|units?|ml|cc|%)',
            r'\d+\s*(?:tablet|tablets|capsule|capsules|cap|tab)',
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0)
        return None
    except Exception as e:
        logger.error(f"Dosage extraction error: {e}")
        return None


def clean_extracted_text(text: str) -> str:
    """Normalise raw OCR text."""
    try:
        text = ' '.join(text.split())
        text = re.sub(r'[^a-zA-Z0-9\s\-\,\.\(\)\/\+%]', '', text)
        return text.strip()
    except Exception as e:
        logger.error(f"Text cleaning error: {e}")
        return text
