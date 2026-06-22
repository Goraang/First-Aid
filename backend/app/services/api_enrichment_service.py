"""
API Enrichment Service — Real-time data from free medical APIs.
Integrates:
  - OpenFDA (fda.gov) — FDA drug labels, adverse events
  - RxNorm (NLM/NIH) — canonical drug names, interactions, RxCUI
  - Open Disease API (disease.sh) — global disease statistics
  - WHO ICD-11 (Tokenless public endpoint)

All APIs are completely free to use. No API key required.
Responses are cached in memory to avoid repeated calls.
"""
import requests
import logging
import time
from typing import Dict, List, Optional, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── HTTP request config ───────────────────────────────────────
REQUEST_TIMEOUT = 8          # seconds
REQUEST_HEADERS = {
    'User-Agent': 'FirstAid-Platform/2.0 (Medical Reference App; contact@firstaid.app)',
    'Accept': 'application/json'
}

# ── Simple in-memory cache ────────────────────────────────────
_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}
CACHE_TTL = 3600  # 1 hour


def _cached_get(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """HTTP GET with simple TTL caching."""
    cache_key = url + str(sorted(params.items()) if params else '')
    now = time.time()

    if cache_key in _cache:
        if now - _cache_timestamps.get(cache_key, 0) < CACHE_TTL:
            logger.debug(f"Cache hit: {url}")
            return _cache[cache_key]

    try:
        resp = requests.get(url, params=params, headers=REQUEST_HEADERS,
                            timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            _cache[cache_key] = data
            _cache_timestamps[cache_key] = now
            return data
        else:
            logger.warning(f"API {url} returned {resp.status_code}")
            return None
    except requests.RequestException as e:
        logger.warning(f"API request failed {url}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  OpenFDA Drug API
# ═══════════════════════════════════════════════════════════════

OPENFDA_DRUG_LABEL_URL = "https://api.fda.gov/drug/label.json"
OPENFDA_DRUG_EVENT_URL = "https://api.fda.gov/drug/event.json"

def get_fda_drug_label(drug_name: str) -> Optional[Dict]:
    """
    Fetch FDA drug label information from OpenFDA.
    Returns structured dict with indications, warnings, dosage etc.
    """
    try:
        params = {
            'search': f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
            'limit': 1
        }
        data = _cached_get(OPENFDA_DRUG_LABEL_URL, params)
        if not data or 'results' not in data or not data['results']:
            # Try broader search
            params = {'search': f'openfda.generic_name:"{drug_name}"', 'limit': 1}
            data = _cached_get(OPENFDA_DRUG_LABEL_URL, params)

        if data and 'results' in data and data['results']:
            result = data['results'][0]
            openfda = result.get('openfda', {})
            return {
                'source': 'OpenFDA',
                'brand_names': openfda.get('brand_name', []),
                'generic_names': openfda.get('generic_name', []),
                'manufacturer': openfda.get('manufacturer_name', []),
                'drug_class': openfda.get('pharm_class_epc', []),
                'indications': result.get('indications_and_usage', [''])[0][:800] if result.get('indications_and_usage') else '',
                'warnings': result.get('warnings', [''])[0][:600] if result.get('warnings') else '',
                'dosage': result.get('dosage_and_administration', [''])[0][:600] if result.get('dosage_and_administration') else '',
                'contraindications': result.get('contraindications', [''])[0][:400] if result.get('contraindications') else '',
                'adverse_reactions': result.get('adverse_reactions', [''])[0][:400] if result.get('adverse_reactions') else '',
                'drug_interactions': result.get('drug_interactions', [''])[0][:400] if result.get('drug_interactions') else '',
                'pregnancy': result.get('pregnancy', [''])[0][:200] if result.get('pregnancy') else '',
            }
        return None
    except Exception as e:
        logger.error(f"OpenFDA label error for {drug_name}: {e}")
        return None


def get_fda_adverse_events(drug_name: str, limit: int = 5) -> List[Dict]:
    """
    Get adverse event reports from FDA FAERS database.
    """
    try:
        params = {
            'search': f'patient.drug.medicinalproduct:"{drug_name}"',
            'count': 'patient.reaction.reactionmeddrapt.exact',
            'limit': limit
        }
        data = _cached_get(OPENFDA_DRUG_EVENT_URL, params)
        if data and 'results' in data:
            return [
                {'reaction': r.get('term', ''), 'count': r.get('count', 0)}
                for r in data['results'][:limit]
            ]
        return []
    except Exception as e:
        logger.error(f"OpenFDA events error for {drug_name}: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
#  RxNorm API (NLM / NIH)
# ═══════════════════════════════════════════════════════════════

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"

def get_rxnorm_info(drug_name: str) -> Optional[Dict]:
    """
    Get canonical drug information from RxNorm.
    Returns RxCUI, concept name, and related information.
    """
    try:
        # Step 1: Get RxCUI
        url = f"{RXNORM_BASE}/rxcui.json"
        data = _cached_get(url, {'name': drug_name, 'search': 1})
        if not data:
            return None

        id_group = data.get('idGroup', {})
        rxcuis = id_group.get('rxnormId', [])
        if not rxcuis:
            return None

        rxcui = rxcuis[0]

        # Step 2: Get drug properties
        props_url = f"{RXNORM_BASE}/rxcui/{rxcui}/properties.json"
        props_data = _cached_get(props_url)

        # Step 3: Get related names (brand names, generics)
        related_url = f"{RXNORM_BASE}/rxcui/{rxcui}/allrelated.json"
        related_data = _cached_get(related_url)

        properties = props_data.get('properties', {}) if props_data else {}

        # Extract brand names from related concepts
        brand_names = []
        if related_data:
            concept_groups = related_data.get('allRelatedGroup', {}).get('conceptGroup', [])
            for group in concept_groups:
                if group.get('tty') in ('BN', 'SBD', 'BPCK'):  # Brand name types
                    concepts = group.get('conceptProperties', [])
                    brand_names.extend([c.get('name', '') for c in concepts[:3]])

        return {
            'source': 'RxNorm (NIH)',
            'rxcui': rxcui,
            'name': properties.get('name', drug_name),
            'synonym': properties.get('synonym', ''),
            'drug_class': properties.get('termType', ''),
            'brand_names': brand_names[:5],
            'rxnorm_link': f"https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm={rxcui}"
        }
    except Exception as e:
        logger.error(f"RxNorm error for {drug_name}: {e}")
        return None


def check_drug_interactions(drug_names: List[str]) -> List[Dict]:
    """
    Check interactions between multiple drugs using RxNorm API.
    """
    try:
        if len(drug_names) < 2:
            return []

        # Get RxCUIs for all drugs
        rxcuis = []
        for drug in drug_names[:5]:  # Limit to 5 drugs
            url = f"{RXNORM_BASE}/rxcui.json"
            data = _cached_get(url, {'name': drug, 'search': 1})
            if data:
                ids = data.get('idGroup', {}).get('rxnormId', [])
                if ids:
                    rxcuis.append(ids[0])

        if len(rxcuis) < 2:
            return [{'message': 'Could not resolve drug names to RxNorm identifiers.'}]

        # Check interactions
        rxcui_str = '+'.join(rxcuis)
        interaction_url = f"{RXNORM_BASE}/interaction/list.json"
        data = _cached_get(interaction_url, {'rxcuis': rxcui_str})

        if not data:
            return []

        interactions = []
        full_interactions = data.get('fullInteractionTypeGroup', [])
        for group in full_interactions:
            for interaction_type in group.get('fullInteractionType', []):
                for pair in interaction_type.get('interactionPair', []):
                    severity = pair.get('severity', 'unknown')
                    description = pair.get('description', '')
                    drug1 = pair.get('interactionConcept', [{}])[0].get('minConceptItem', {}).get('name', '')
                    drug2 = pair.get('interactionConcept', [{}])[-1].get('minConceptItem', {}).get('name', '') if len(pair.get('interactionConcept', [])) > 1 else ''
                    interactions.append({
                        'drug1': drug1,
                        'drug2': drug2,
                        'severity': severity,
                        'description': description
                    })

        return interactions[:10]  # Limit to 10 interactions

    except Exception as e:
        logger.error(f"Drug interaction check error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
#  Open Disease API
# ═══════════════════════════════════════════════════════════════

DISEASE_API_BASE = "https://disease.sh/v3"

def get_covid_global_stats() -> Optional[Dict]:
    """Get current global COVID-19 statistics."""
    try:
        data = _cached_get(f"{DISEASE_API_BASE}/covid-19/all")
        if data:
            return {
                'source': 'disease.sh (Johns Hopkins)',
                'cases': data.get('cases', 0),
                'deaths': data.get('deaths', 0),
                'recovered': data.get('recovered', 0),
                'active': data.get('active', 0),
                'updated': data.get('updated', 0)
            }
        return None
    except Exception as e:
        logger.error(f"COVID stats error: {e}")
        return None


def get_disease_country_stats(disease: str = 'covid-19', country: str = 'India') -> Optional[Dict]:
    """Get disease statistics for a specific country."""
    try:
        url = f"{DISEASE_API_BASE}/{disease}/countries/{country}"
        data = _cached_get(url)
        if data:
            return {
                'source': 'disease.sh',
                'country': data.get('country', country),
                'cases': data.get('cases', 0),
                'deaths': data.get('deaths', 0),
                'recovered': data.get('recovered', 0),
                'active': data.get('active', 0),
                'critical': data.get('critical', 0),
                'cases_per_million': data.get('casesPerOneMillion', 0),
                'updated': data.get('updated', 0)
            }
        return None
    except Exception as e:
        logger.error(f"Country stats error for {country}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  WHO ICD-11 API (No key required for tokenless access)
# ═══════════════════════════════════════════════════════════════

ICD11_BASE = "https://id.who.int/icd/release/11/2024-01/mms"

def search_icd11(query: str, limit: int = 5) -> List[Dict]:
    """
    Search WHO ICD-11 classification for a disease or symptom.
    Uses the WHO ICD-11 API (free, no auth required for basic access).
    """
    try:
        url = "https://icd11.who.int/ct11/2024-01/SearchFast"
        params = {
            'q': query,
            'count': limit,
            'useFlexisearch': 'false',
            'flatResults': 'true',
            'highlightingEnabled': 'false'
        }
        headers = {
            **REQUEST_HEADERS,
            'Accept-Language': 'en',
        }
        resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []
        for entity in data.get('destinationEntities', [])[:limit]:
            results.append({
                'source': 'WHO ICD-11',
                'title': entity.get('title', ''),
                'icd_code': entity.get('theCode', ''),
                'definition': entity.get('definition', ''),
                'synonyms': entity.get('synonyms', []),
                'icd_link': entity.get('id', '')
            })
        return results
    except Exception as e:
        logger.warning(f"ICD-11 search error for '{query}': {e}")
        return []


# ═══════════════════════════════════════════════════════════════
#  Combined Drug Information
# ═══════════════════════════════════════════════════════════════

def get_enriched_drug_info(drug_name: str) -> Dict:
    """
    Get comprehensive drug information from all available sources.
    Combines local DB data with OpenFDA and RxNorm API data.
    """
    result = {
        'name': drug_name,
        'sources': [],
        'fda_data': None,
        'rxnorm_data': None,
        'adverse_events': []
    }

    # OpenFDA
    fda_data = get_fda_drug_label(drug_name)
    if fda_data:
        result['fda_data'] = fda_data
        result['sources'].append('OpenFDA')

    # RxNorm
    rxnorm_data = get_rxnorm_info(drug_name)
    if rxnorm_data:
        result['rxnorm_data'] = rxnorm_data
        result['sources'].append('RxNorm')

    # Top adverse events
    adverse = get_fda_adverse_events(drug_name, limit=5)
    if adverse:
        result['adverse_events'] = adverse
        if 'OpenFDA' not in result['sources']:
            result['sources'].append('OpenFDA')

    result['enriched'] = len(result['sources']) > 0

    if not result['enriched']:
        result['message'] = (
            'Could not retrieve live API data for this drug. '
            'The local database information is shown. '
            'Try searching by the international generic name (INN).'
        )

    return result
