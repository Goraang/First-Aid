"""
Universal Medical Routes — /api/medical
Endpoints for symptom-based diagnosis, disease search, drug information,
drug interaction checking, and real-time API enrichment.
All endpoints require JWT authentication.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

from app.services.medical_analysis_service import (
    analyze_symptoms,
    search_diseases,
    get_disease_by_id,
    get_categories_summary,
    get_database_stats,
    load_all_diseases,
    load_skin_diseases,
    load_general_diseases,
    SYMPTOM_CLUSTERS,
)
from app.services.api_enrichment_service import (
    get_enriched_drug_info,
    check_drug_interactions,
    search_icd11,
    get_covid_global_stats,
    get_disease_country_stats,
)
from app.services.gemini_service import analyze_symptoms_with_gemini
from app.services.skin_analysis_service import analyze_skin_condition

medical_bp = Blueprint('medical', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# In-memory history store (replace with DB for production)
analysis_history: dict = {}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ═══════════════════════════════════════════════════════════════
#  POST /api/medical/analyze-symptoms
#  Analyse free-text symptoms → top disease matches
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/analyze-symptoms', methods=['POST'])
@jwt_required()
def analyze_symptoms_endpoint():
    """
    Universal symptom analysis.

    Body (JSON or form-data):
      symptoms     (str, required) — Free text description of symptoms
      body_part    (str, optional) — Affected body part or system
      category     (str, optional) — Filter by category (respiratory, cardiovascular, etc.)
    """
    try:
        # Accept both JSON and form-data
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict()

        symptoms = data.get('symptoms', '').strip()
        body_part = data.get('body_part', 'unknown').strip()
        category = data.get('category', None)
        top_n = int(data.get('top_n', 5))

        if not symptoms:
            return jsonify({'error': 'symptoms field is required'}), 400

        if len(symptoms) < 3:
            return jsonify({'error': 'Please provide a more detailed symptom description'}), 400

        # Run analysis via Gemini (with fallback to local if needed)
        gemini_result = analyze_symptoms_with_gemini(
            symptoms=symptoms,
            body_part=body_part,
            category=category
        )
        if gemini_result and not gemini_result.get('error'):
            result = gemini_result
        else:
            result = analyze_symptoms(
                symptom_text=symptoms,
                body_part=body_part,
                category_filter=category,
                top_n=min(top_n, 10)
            )

        # Store in history
        email = get_jwt_identity()
        if email not in analysis_history:
            analysis_history[email] = []
        analysis_history[email].append({
            'id': f"analysis_{datetime.now().timestamp()}",
            'symptoms': symptoms[:200],
            'body_part': body_part,
            'top_match': result.get('top_match', {}).get('name', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'emergency': result.get('emergency', False)
        })

        return jsonify({
            'success': True,
            **result
        }), 200

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════
#  POST /api/medical/analyze-image
#  Universal image + symptom analysis (works for any condition)
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/analyze-image', methods=['POST'])
@jwt_required()
def analyze_image():
    """
    Universal image analysis with optional symptom text.
    Analyses image features and combines with symptoms for richer matching.
    """
    try:
        symptoms = request.form.get('symptoms', '')
        body_part = request.form.get('body_part', 'unknown')
        category = request.form.get('category', None)

        image_features = None
        filepath = None

        if 'image' in request.files:
            file = request.files['image']
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Extract image features using skin analysis service
                from app.services.skin_analysis_service import analyze_image_features
                image_features = analyze_image_features(filepath)

        # Run universal analysis
        result = analyze_symptoms(
            symptom_text=symptoms or f'image analysis for {body_part}',
            body_part=body_part,
            category_filter=category,
            image_features=image_features,
            top_n=5
        )

        # Cleanup
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

        return jsonify({
            'success': True,
            'image_features': image_features,
            **result
        }), 200

    except Exception as e:
        return jsonify({'error': f'Image analysis failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/search-disease?q=<query>&category=<cat>
#  Full-text search across all diseases
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/search-disease', methods=['GET'])
@jwt_required()
def search_disease():
    """Search all diseases by name, keyword, or symptom."""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', None)
        limit = request.args.get('limit', 20, type=int)

        if not query or len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400

        results = search_diseases(query, category=category, limit=min(limit, 50))

        # Slim down results for list view
        slim_results = []
        for d in results:
            slim_results.append({
                'id': d.get('id'),
                'name': d.get('name'),
                'category': d.get('category', 'general'),
                'scientific_name': d.get('scientific_name', ''),
                'description': d.get('description', '')[:200],
                'severity': d.get('severity', 'moderate'),
                'keywords': d.get('keywords', [])[:5]
            })

        return jsonify({
            'success': True,
            'query': query,
            'results': slim_results,
            'total': len(slim_results)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/disease/<disease_id>
#  Get full disease details
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/disease/<disease_id>', methods=['GET'])
@jwt_required()
def get_disease(disease_id):
    """Get full details for a disease by ID."""
    try:
        include_icd = request.args.get('include_icd', 'false').lower() == 'true'

        disease = get_disease_by_id(disease_id)
        if not disease:
            return jsonify({'error': f'Disease {disease_id} not found'}), 404

        response = {'success': True, 'disease': disease}

        # Optionally enrich with ICD-11 data
        if include_icd:
            icd_results = search_icd11(disease.get('name', ''), limit=3)
            response['icd11_data'] = icd_results

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/categories
#  List all disease categories with counts
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all disease categories with disease counts."""
    try:
        categories = get_categories_summary()
        return jsonify({
            'success': True,
            'categories': categories,
            'available_filters': list(SYMPTOM_CLUSTERS.keys())
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/drug-info/<drug_name>
#  Drug information from local DB + OpenFDA + RxNorm
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/drug-info/<drug_name>', methods=['GET'])
@jwt_required()
def get_drug_info(drug_name):
    """
    Get comprehensive drug information from local DB and free APIs.
    Sources: local medicines.json, OpenFDA, RxNorm.
    """
    try:
        enrich = request.args.get('enrich', 'true').lower() == 'true'

        # Load local medicines database
        medicines_db = _load_medicines_db()

        # Search local DB
        drug_name_l = drug_name.lower()
        local_match = None
        for med in medicines_db:
            all_names = [med.get('name', ''), med.get('generic_name', '')]
            all_names += med.get('brand_names', [])
            if any(drug_name_l in n.lower() for n in all_names if n):
                local_match = med
                break

        # Get API enrichment
        api_data = {}
        if enrich:
            search_name = local_match.get('generic_name', drug_name) if local_match else drug_name
            api_data = get_enriched_drug_info(search_name)

        response = {
            'success': True,
            'drug_name': drug_name,
            'local_data': local_match,
            'api_enrichment': api_data if enrich else None,
            'found_locally': local_match is not None
        }

        if not local_match and not api_data.get('enriched'):
            return jsonify({
                **response,
                'message': f'Limited information found for "{drug_name}". '
                           'Try the generic (INN) name for better results.'
            }), 200

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  POST /api/medical/drug-interactions
#  Check interactions between multiple drugs
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/drug-interactions', methods=['POST'])
@jwt_required()
def drug_interactions():
    """
    Check drug-drug interactions via RxNorm API.

    Body (JSON):
      drugs  (list of str, required) — 2-5 drug names to check
    """
    try:
        data = request.get_json(silent=True) or {}
        drugs = data.get('drugs', [])

        if not drugs or len(drugs) < 2:
            return jsonify({'error': 'At least 2 drug names required'}), 400

        if len(drugs) > 5:
            drugs = drugs[:5]

        interactions = check_drug_interactions(drugs)

        return jsonify({
            'success': True,
            'drugs_checked': drugs,
            'interactions': interactions,
            'interaction_count': len(interactions),
            'source': 'RxNorm (NIH National Library of Medicine)'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/icd-search?q=<query>
#  Search WHO ICD-11 classification
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/icd-search', methods=['GET'])
@jwt_required()
def icd_search():
    """Search WHO ICD-11 classification for a condition."""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 5, type=int)

        if not query or len(query) < 3:
            return jsonify({'error': 'Query must be at least 3 characters'}), 400

        results = search_icd11(query, limit=min(limit, 10))

        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'source': 'WHO ICD-11 (2024 release)'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/global-stats?disease=covid-19&country=India
#  Live global disease statistics
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/global-stats', methods=['GET'])
@jwt_required()
def global_stats():
    """Get live global disease statistics."""
    try:
        disease = request.args.get('disease', 'covid-19')
        country = request.args.get('country', 'India')

        if country.lower() in ('global', 'world', 'all'):
            stats = get_covid_global_stats()
        else:
            stats = get_disease_country_stats(disease, country)

        if not stats:
            return jsonify({
                'success': False,
                'message': 'Could not retrieve stats at this time.'
            }), 200

        return jsonify({
            'success': True,
            'stats': stats,
            'disease': disease,
            'region': country
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/stats
#  Database and system statistics
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get statistics about the medical knowledge base."""
    try:
        email = get_jwt_identity()
        db_stats = get_database_stats()
        user_analyses = len(analysis_history.get(email, []))

        medicines_db = _load_medicines_db()

        return jsonify({
            'success': True,
            'database': {
                **db_stats,
                'total_medicines': len(medicines_db),
            },
            'user_stats': {
                'analyses_performed': user_analyses,
            },
            'api_integrations': [
                {'name': 'OpenFDA', 'url': 'https://api.fda.gov', 'status': 'active'},
                {'name': 'RxNorm', 'url': 'https://rxnav.nlm.nih.gov', 'status': 'active'},
                {'name': 'Open Disease API', 'url': 'https://disease.sh', 'status': 'active'},
                {'name': 'WHO ICD-11', 'url': 'https://icd.who.int', 'status': 'active'},
            ]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/history
#  User's analysis history
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get the user's symptom analysis history."""
    try:
        email = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        history = analysis_history.get(email, [])
        total = len(history)

        start = (page - 1) * limit
        paginated = history[start:start + limit]

        return jsonify({
            'success': True,
            'history': paginated,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit if total > 0 else 1
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/medical/symptom-keywords
#  Return all symptom keyword clusters for client-side use
# ═══════════════════════════════════════════════════════════════

@medical_bp.route('/symptom-keywords', methods=['GET'])
@jwt_required()
def symptom_keywords():
    """Return symptom cluster keywords (for autocomplete/hints)."""
    try:
        return jsonify({
            'success': True,
            'clusters': {k: v[:10] for k, v in SYMPTOM_CLUSTERS.items()}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Helper ────────────────────────────────────────────────────

def _load_medicines_db() -> list:
    """Load medicines database."""
    db_path = os.path.join(os.path.dirname(__file__), '../../database/medicines.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('medicines', [])
    except Exception as e:
        logger.error(f"Medicines DB load error: {e}")
        return []


import logging
logger = logging.getLogger(__name__)
