"""
Dermatology Routes — /api/dermatology
Skin condition analysis with comprehensive medicine recommendations.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json
import logging
from app.services.skin_analysis_service import (
    analyze_skin_condition,
    get_alternative_medicines_for_condition,
    get_treatment_recommendations,
)
from datetime import datetime

logger = logging.getLogger(__name__)
dermatology_bp = Blueprint('dermatology', __name__)

# In-memory history (replace with DB in production)
dermatology_history = {}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff', 'tif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_diseases_db():
    """Load skin diseases from database file."""
    db_path = os.path.join(os.path.dirname(__file__), '../../database/skin_diseases.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('skin_diseases', [])
    except Exception as e:
        logger.error(f"Skin diseases DB load error: {e}")
        return []


def load_medicines_db():
    """Load medicines from database file."""
    db_path = os.path.join(os.path.dirname(__file__), '../../database/medicines.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('medicines', [])
    except Exception as e:
        logger.error(f"Medicines DB load error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
#  POST /api/dermatology/analyze
#  Analyze skin condition from image + symptoms
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """
    Analyze skin condition from image and/or symptom description.

    Form-data:
      image         (file, optional) — Skin image (PNG, JPG, WEBP, etc.)
      body_part     (str, optional)  — Affected body part (e.g. 'face', 'arm')
      symptoms      (str, optional)  — Free-text symptom description
      symptom_text  (str, optional)  — Alias for symptoms

    Returns:
      disease:                   Detected skin condition details
      confidence:                Detection confidence (0–1)
      top_alternatives:          Other possible conditions
      recommended_medicines:     Primary treatment medicines (full data)
      alternative_medicines:     Other medicines that can treat the same condition
      treatments:                Treatment regimen list
      image_features:            Color and texture analysis results
    """
    try:
        email = get_jwt_identity()

        body_part = request.form.get('body_part', 'unknown')
        symptoms = request.form.get('symptoms', '')
        symptom_text = request.form.get('symptom_text', symptoms).strip()

        filepath = None
        image_features = None

        # ── Handle image upload ───────────────────────────────
        if 'image' in request.files:
            file = request.files['image']
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                logger.info(f"Skin image uploaded: {filename}, body_part={body_part}")
            elif file.filename:
                return jsonify({
                    'error': f'Invalid file type. Supported: {", ".join(ALLOWED_EXTENSIONS).upper()}'
                }), 400

        if not filepath and not symptom_text:
            return jsonify({
                'error': 'Please provide an image and/or symptom description'
            }), 400

        try:
            # ── Analyze skin condition ────────────────────────
            if filepath:
                analysis_result = analyze_skin_condition(filepath, body_part, symptom_text)
                from app.services.skin_analysis_service import analyze_image_features
                image_features = analyze_image_features(filepath)
            else:
                # Text-only analysis: use the medical analysis service
                from app.services.medical_analysis_service import analyze_symptoms
                text_result = analyze_symptoms(
                    symptom_text=symptom_text or 'skin rash',
                    body_part=body_part,
                    category_filter='dermatology',
                    top_n=5
                )
                # Convert to skin analysis format
                top = text_result.get('top_match', {})
                diseases_db = load_diseases_db()
                matched_disease = next(
                    (d for d in diseases_db if d.get('name', '').lower() == top.get('name', '').lower()),
                    top
                )
                analysis_result = {
                    'disease': matched_disease,
                    'confidence': top.get('confidence', 0.60),
                    'body_part': body_part,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'top_alternatives': [
                        {'name': a.get('name'), 'confidence': a.get('confidence')}
                        for a in text_result.get('alternatives', [])[:4]
                    ],
                    'recommended_medicines': [],
                    'alternative_medicines': [],
                }

        finally:
            # Clean up uploaded file
            if filepath:
                try:
                    os.remove(filepath)
                except Exception:
                    pass

        if analysis_result.get('error'):
            return jsonify({
                'success': False,
                'error': analysis_result['error'],
                'suggestion': 'Please upload a clear, well-lit photo of the skin condition.'
            }), 200

        # ── Enrich result with additional medicine data ────────
        disease = analysis_result.get('disease', {})
        disease_name = disease.get('name', '')
        confidence = analysis_result.get('confidence', 0.60)

        # Ensure recommended/alternative medicines are present
        rec_meds = analysis_result.get('recommended_medicines', [])
        alt_meds = analysis_result.get('alternative_medicines', [])

        if not rec_meds and disease_name:
            medicines_db = load_medicines_db()
            all_for_cond = get_alternative_medicines_for_condition(disease_name, top_n=8)
            rec_names = {n.lower() for n in disease.get('recommended_medicines', [])}
            for med in all_for_cond:
                if any(r in med.get('name', '').lower() for r in rec_names):
                    rec_meds.append(med)
                else:
                    alt_meds.append(med)

        # Slim medicine data for response
        def _slim_med(med: dict) -> dict:
            return {
                'id': med.get('id'),
                'name': med.get('name'),
                'generic_name': med.get('generic_name'),
                'salt_composition': med.get('salt_composition'),
                'brand_names': med.get('brand_names', [])[:3],
                'type': med.get('type'),
                'price_inr': med.get('price_inr'),
                'efficacy_rating': med.get('efficacy_rating'),
                'usage': med.get('usage'),
                'dosage': med.get('dosage'),
                'side_effects': med.get('side_effects', [])[:3],
                'warnings': med.get('warnings', [])[:2],
                'recommendation_reason': med.get('recommendation_reason', ''),
            }

        slim_rec = [_slim_med(m) for m in rec_meds[:5]]
        slim_alt = [_slim_med(m) for m in alt_meds[:5]]

        # ── Save to history ───────────────────────────────────
        if email not in dermatology_history:
            dermatology_history[email] = []

        scan_record = {
            'id': f"scan_{datetime.now().timestamp()}",
            'disease_name': disease_name,
            'confidence': confidence,
            'body_part': body_part,
            'timestamp': datetime.now().isoformat(),
        }
        dermatology_history[email].append(scan_record)

        response = {
            'success': True,
            'disease': disease,
            'confidence': confidence,
            'body_part': body_part,
            'top_alternatives': analysis_result.get('top_alternatives', []),
            'recommended_medicines': slim_rec,
            'alternative_medicines': slim_alt,
            'treatments': disease.get('treatments', []),
            'prevention': disease.get('prevention', []),
            'severity': disease.get('severity', 'moderate'),
            'analysis_timestamp': analysis_result.get('analysis_timestamp'),
        }

        if image_features:
            response['image_features'] = image_features

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Dermatology analysis error: {e}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/dermatology/medicines-for-disease/<disease_id>
#  Get all medicines for a specific disease by ID
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/medicines-for-disease/<disease_id>', methods=['GET'])
@jwt_required()
def get_medicines_for_disease(disease_id):
    """
    Get primary and alternative medicines for a specific skin disease.

    Returns:
      disease:               Disease details
      primary_medicines:     Directly recommended medicines
      alternative_medicines: Additional options (different salts, same condition)
    """
    try:
        diseases = load_diseases_db()
        disease = next((d for d in diseases if d.get('id') == disease_id), None)

        if not disease:
            return jsonify({'error': f'Disease {disease_id} not found'}), 404

        disease_name = disease.get('name', '')
        medicines_db = load_medicines_db()

        from app.services.nlp_service import find_medicines_for_skin_condition
        rec_names = disease.get('recommended_medicines', [])
        all_meds = find_medicines_for_skin_condition(
            disease_name, medicines_db, rec_names, top_n=12
        )

        rec_names_l = {n.lower() for n in rec_names}
        primary = []
        alternatives = []

        for med in all_meds:
            is_primary = any(
                r in med.get('name', '').lower() or
                r in med.get('generic_name', '').lower() or
                r in med.get('salt_composition', '').lower()
                for r in rec_names_l
            )
            med_slim = {
                'id': med.get('id'),
                'name': med.get('name'),
                'generic_name': med.get('generic_name'),
                'salt_composition': med.get('salt_composition'),
                'brand_names': med.get('brand_names', [])[:3],
                'type': med.get('type'),
                'price_inr': med.get('price_inr'),
                'efficacy_rating': med.get('efficacy_rating'),
                'usage': med.get('usage'),
                'dosage': med.get('dosage'),
                'for_conditions': med.get('for_conditions', []),
                'side_effects': med.get('side_effects', [])[:3],
                'recommendation_reason': med.get('recommendation_reason', ''),
            }
            if is_primary:
                primary.append(med_slim)
            else:
                alternatives.append(med_slim)

        return jsonify({
            'success': True,
            'disease': disease,
            'primary_medicines': primary,
            'alternative_medicines': alternatives,
            'total_medicines': len(all_meds),
            'note': (
                'Primary medicines are directly listed in clinical guidelines for this condition. '
                'Alternative medicines contain the same or different active ingredients '
                'that are also used to treat this condition.'
            ),
        }), 200

    except Exception as e:
        logger.error(f"Medicines for disease error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/dermatology/history
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's skin analysis history."""
    try:
        email = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        scans = dermatology_history.get(email, [])
        total = len(scans)
        start = (page - 1) * limit
        paginated = scans[start:start + limit]

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
#  GET /api/dermatology/disease/<disease_id>
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/disease/<disease_id>', methods=['GET'])
@jwt_required()
def get_disease(disease_id):
    """Get detailed information about a skin disease."""
    try:
        diseases = load_diseases_db()
        disease = next((d for d in diseases if d.get('id') == disease_id), None)

        if not disease:
            return jsonify({'error': 'Disease not found'}), 404

        return jsonify({'success': True, 'disease': disease}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/dermatology/conditions
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/conditions', methods=['GET'])
@jwt_required()
def get_conditions():
    """Get list of all skin conditions in the database."""
    try:
        diseases = load_diseases_db()
        slim = [
            {
                'id': d.get('id'),
                'name': d.get('name'),
                'scientific_name': d.get('scientific_name', ''),
                'severity': d.get('severity', 'moderate'),
                'affected_areas': d.get('affected_areas', [])[:3],
                'description': d.get('description', '')[:150],
            }
            for d in diseases
        ]
        return jsonify({
            'success': True,
            'conditions': slim,
            'total': len(slim)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/dermatology/stats
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dermatology module statistics."""
    try:
        email = get_jwt_identity()
        user_scans = len(dermatology_history.get(email, []))
        diseases = load_diseases_db()
        medicines = load_medicines_db()
        skin_meds = [m for m in medicines if m.get('for_conditions')]

        return jsonify({
            'success': True,
            'total_analyses': user_scans,
            'diseases_in_db': len(diseases),
            'skin_medicines_in_db': len(skin_meds),
            'features': [
                'Image-based skin condition detection',
                'OCR text analysis from skin images',
                'Primary and alternative medicine recommendations',
                'Price vs efficacy comparison',
                'Treatment guidelines',
            ]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  DELETE /api/dermatology/history/<scan_id>
# ═══════════════════════════════════════════════════════════════

@dermatology_bp.route('/history/<scan_id>', methods=['DELETE'])
@jwt_required()
def delete_scan(scan_id):
    """Delete a scan from history."""
    try:
        email = get_jwt_identity()
        if email in dermatology_history:
            dermatology_history[email] = [
                s for s in dermatology_history[email] if s.get('id') != scan_id
            ]
        return jsonify({'success': True, 'message': 'Scan deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
