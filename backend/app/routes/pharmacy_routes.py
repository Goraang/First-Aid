"""
Pharmacy Routes — /api/pharmacy
Medicine scanning, salt comparison, condition-based recommendations, and drug interaction checking.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import json
import re
from app.services.ocr_service import (
    extract_text_from_image,
    extract_salt_composition,
    extract_medicine_name,
    extract_dosage_strength,
    get_ocr_confidence,
)
from app.services.nlp_service import (
    find_best_medicine_match,
    compare_medicines_by_salt,
    find_medicines_for_skin_condition,
)
from app.services.gemini_service import analyze_medicine_image_with_gemini, search_medicines_with_gemini
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

pharmacy_bp = Blueprint('pharmacy', __name__)

# In-memory scan history (replace with DB in production)
pharmacy_history = {}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff', 'tif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_medicines_db() -> list:
    """Load medicines from database file."""
    db_path = os.path.join(os.path.dirname(__file__), '../../database/medicines.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('medicines', [])
    except Exception as e:
        logger.error(f"Medicines DB load error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
#  POST /api/pharmacy/scan
#  Scan and identify medicine from an image (OCR + NLP matching)
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_medicine():
    """
    Scan and identify medicine from image using OCR + NLP.

    Form-data:
      image   (file, required) — Medicine image (PNG, JPG, WEBP, BMP, GIF, TIFF)

    Returns:
      medicine:         Full matched medicine data
      confidence:       Match confidence (0–1)
      ocr_confidence:   OCR text extraction quality (0–1)
      extracted_text:   Raw OCR text
      detected_salt:    Active ingredient detected from image
      detected_name:    Medicine name detected from image
      detected_strength: Dosage strength detected
    """
    try:
        email = get_jwt_identity()

        if 'image' not in request.files:
            return jsonify({'error': 'No image provided. Please upload an image file.'}), 400

        file = request.files['image']
        if not file.filename or not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Supported formats: {", ".join(ALLOWED_EXTENSIONS).upper()}'
            }), 400

        # Save uploaded file
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        logger.info(f"Scanning medicine image: {filename}")

        try:
            # ── Direct Gemini Vision Analysis ───────────────────
            gemini_result = analyze_medicine_image_with_gemini(filepath)
            
            if gemini_result and not gemini_result.get('error'):
                best_match = {
                    'id': f"gemini_{datetime.now().timestamp()}",
                    'name': gemini_result.get('name'),
                    'generic_name': gemini_result.get('generic_name'),
                    'salt_composition': gemini_result.get('salt_composition'),
                    'type': gemini_result.get('dosage_form', 'Tablet'),
                    'usage': gemini_result.get('usage', ''),
                    'dosage': gemini_result.get('dosage', ''),
                    'side_effects': gemini_result.get('side_effects', []),
                    'warnings': gemini_result.get('warnings', []),
                    'price_inr': gemini_result.get('price_inr', 'N/A'),
                    'confidence': gemini_result.get('confidence', 0.95),
                    'match_method': 'gemini_multimodal_vision'
                }
                detected_name = gemini_result.get('name')
                detected_salt = gemini_result.get('salt_composition')
                detected_strength = gemini_result.get('strength')
                ocr_conf = 0.95
                extracted_text = f"{detected_name} - {detected_salt}"
                similar = gemini_result.get('alternatives', [])
            else:
                # Fallback to local OCR + DB matching if Gemini fails
                extracted_text = extract_text_from_image(filepath)

                if not extracted_text or len(extracted_text.strip()) < 3:
                    return jsonify({
                        'error': 'Could not extract text from image. '
                                 'Please upload a clearer, well-lit photo of the medicine label.',
                        'tip': 'Ensure the text on the medicine is in focus and not obscured.'
                    }), 400

                detected_salt = extract_salt_composition(extracted_text)
                detected_name = extract_medicine_name(extracted_text)
                detected_strength = extract_dosage_strength(extracted_text)
                ocr_conf = get_ocr_confidence(extracted_text)

                medicines = load_medicines_db()
                best_match = find_best_medicine_match(
                    extracted_text,
                    medicines,
                    threshold=0.30,
                    salt_hint=detected_salt,
                )

                if not best_match and detected_name:
                    name_l = detected_name.lower()
                    for med in medicines:
                        all_names = (
                            [med.get('name', ''), med.get('generic_name', '')] +
                            med.get('brand_names', []) +
                            [med.get('salt_composition', '')]
                        )
                        if any(name_l in n.lower() for n in all_names if n):
                            best_match = dict(med)
                            best_match['confidence'] = 0.65
                            best_match['match_method'] = 'name_search_fallback'
                            break

                if not best_match:
                    return jsonify({
                        'success': True,
                        'warning': 'Medicine not found',
                        'extracted_text': extracted_text[:500],
                        'detected_salt': detected_salt,
                        'detected_name': detected_name,
                        'detected_strength': detected_strength,
                        'ocr_confidence': ocr_conf,
                    }), 200

                salt_for_comparison = (
                    best_match.get('salt_composition') or
                    best_match.get('generic_name') or
                    detected_salt or
                    best_match.get('name', '')
                )
                alternatives_result = compare_medicines_by_salt(
                    salt_for_comparison, medicines, top_n=5
                )
                similar = [
                    m for m in alternatives_result.get('medicines', [])
                    if m.get('id') != best_match.get('id')
                ][:4]

            # ── Step 6: Save to history ────────────────────────
            if email not in pharmacy_history:
                pharmacy_history[email] = []

            scan_record = {
                'id': f"scan_{datetime.now().timestamp()}",
                'medicine_name': best_match.get('name'),
                'medicine': best_match,
                'extracted_text': extracted_text[:500],
                'detected_salt': detected_salt,
                'confidence': best_match.get('confidence', 0.70),
                'timestamp': datetime.now().isoformat(),
            }
            pharmacy_history[email].append(scan_record)

        finally:
            # Always clean up uploaded file
            try:
                os.remove(filepath)
            except Exception:
                pass

        return jsonify({
            'success': True,
            'medicine': best_match,
            'confidence': best_match.get('confidence', 0.70),
            'ocr_confidence': ocr_conf,
            'extracted_text': extracted_text[:500],
            'detected_salt': detected_salt,
            'detected_name': detected_name,
            'detected_strength': detected_strength,
            'match_method': best_match.get('match_method', 'unknown'),
            'similar_medicines': similar,
            'tip': (
                f"Found {len(similar)} similar medicine(s) with the same active ingredient. "
                f"Use /api/pharmacy/compare-by-salt for full comparison."
            ) if similar else None
        }), 200

    except Exception as e:
        logger.error(f"Scan error: {e}", exc_info=True)
        return jsonify({'error': f'Scanning failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════
#  POST /api/pharmacy/compare-by-salt
#  Compare medicines with the same active ingredient (salt)
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/compare-by-salt', methods=['POST'])
@jwt_required()
def compare_by_salt():
    """
    Compare all medicines sharing the same active ingredient/salt.
    Returns efficacy rating, price (INR), side effects, and best-value pick.

    Body (JSON):
      salt_name    (str)  — Active ingredient to compare (e.g. "Cetirizine HCl")
      medicine_id  (str)  — OR provide a medicine ID to auto-extract its salt
      top_n        (int)  — Max results (default: 10)
    """
    try:
        data = request.get_json(silent=True) or {}
        salt_name = data.get('salt_name', '').strip()
        medicine_id = data.get('medicine_id', '').strip()
        top_n = min(int(data.get('top_n', 10)), 20)

        medicines = load_medicines_db()

        # If medicine_id given, look up its salt
        if medicine_id and not salt_name:
            target = next((m for m in medicines if m.get('id') == medicine_id), None)
            if not target:
                return jsonify({'error': f'Medicine ID "{medicine_id}" not found'}), 404
            salt_name = (
                target.get('salt_composition') or
                target.get('generic_name') or
                target.get('name', '')
            )

        if not salt_name or len(salt_name) < 2:
            return jsonify({
                'error': 'Provide "salt_name" (active ingredient) or "medicine_id"'
            }), 400

        result = compare_medicines_by_salt(salt_name, medicines, top_n=top_n)

        if not result.get('medicines'):
            return jsonify({
                'success': False,
                'salt': salt_name,
                'message': result.get('message', f'No medicines found with salt: {salt_name}'),
                'suggestion': 'Try common salt names like "Cetirizine", "Ibuprofen", "Clotrimazole".'
            }), 200

        # Build comparison table (sorted: most effective first, then cheapest)
        meds = result['medicines']
        comparison_table = []
        for med in sorted(meds, key=lambda m: (-(m.get('efficacy_rating') or 0), (m.get('price_inr') or 9999))):
            comparison_table.append({
                'id': med.get('id'),
                'name': med.get('name'),
                'generic_name': med.get('generic_name'),
                'salt': med.get('salt_composition'),
                'brands': med.get('brand_names', [])[:3],
                'type': med.get('type'),
                'price_inr': med.get('price_inr'),
                'efficacy_rating': med.get('efficacy_rating'),
                'efficacy_label': _efficacy_label(med.get('efficacy_rating')),
                'for_conditions': med.get('for_conditions', []),
                'side_effects': med.get('side_effects', [])[:4],
                'dosage': med.get('dosage'),
                'usage': med.get('usage'),
            })

        return jsonify({
            'success': True,
            'salt_searched': salt_name,
            'total_medicines': len(meds),
            'comparison_table': comparison_table,
            'most_effective': {
                'name': result['most_effective']['name'],
                'efficacy_rating': result['most_effective']['efficacy_rating'],
                'price_inr': result['most_effective']['price_inr'],
            } if result.get('most_effective') else None,
            'cheapest': {
                'name': result['cheapest']['name'],
                'price_inr': result['cheapest']['price_inr'],
                'efficacy_rating': result['cheapest']['efficacy_rating'],
            } if result.get('cheapest') else None,
            'best_value': {
                'name': result['best_value']['name'],
                'price_inr': result['best_value']['price_inr'],
                'efficacy_rating': result['best_value']['efficacy_rating'],
                'reason': 'Best efficacy-to-price ratio',
            } if result.get('best_value') else None,
            'note': result.get('comparison_note', ''),
        }), 200

    except Exception as e:
        logger.error(f"Compare-by-salt error: {e}", exc_info=True)
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/pharmacy/medicines-for-condition?condition=<name>
#  Get medicines recommended for a skin/medical condition
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/medicines-for-condition', methods=['GET'])
@jwt_required()
def medicines_for_condition():
    """
    Get medicines recommended for a given skin or medical condition.

    Query params:
      condition   (str, required) — Disease/condition name (e.g. 'eczema', 'acne')
      top_n       (int, optional) — Max results (default 8)
    """
    try:
        condition = request.args.get('condition', '').strip()
        top_n = min(request.args.get('top_n', 8, type=int), 15)

        if not condition or len(condition) < 2:
            return jsonify({'error': 'condition parameter is required (min 2 chars)'}), 400

        medicines = load_medicines_db()
        results = find_medicines_for_skin_condition(
            condition, medicines, top_n=top_n
        )

        if not results:
            return jsonify({
                'success': True,
                'condition': condition,
                'medicines': [],
                'message': (
                    f'No specific medicines found for "{condition}". '
                    'Please consult a healthcare professional.'
                )
            }), 200

        # Slim down for response
        slim = []
        for med in results:
            slim.append({
                'id': med.get('id'),
                'name': med.get('name'),
                'generic_name': med.get('generic_name'),
                'salt_composition': med.get('salt_composition'),
                'brand_names': med.get('brand_names', [])[:3],
                'type': med.get('type'),
                'price_inr': med.get('price_inr'),
                'efficacy_rating': med.get('efficacy_rating'),
                'efficacy_label': _efficacy_label(med.get('efficacy_rating')),
                'for_conditions': med.get('for_conditions', []),
                'usage': med.get('usage'),
                'dosage': med.get('dosage'),
                'side_effects': med.get('side_effects', [])[:3],
                'warnings': med.get('warnings', [])[:2],
                'recommendation_reason': med.get('recommendation_reason', ''),
            })

        return jsonify({
            'success': True,
            'condition': condition,
            'total': len(slim),
            'medicines': slim,
            'sorted_by': 'efficacy_rating (descending)',
        }), 200

    except Exception as e:
        logger.error(f"Medicines-for-condition error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/pharmacy/history
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's scan history."""
    try:
        email = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        scans = pharmacy_history.get(email, [])
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
#  GET /api/pharmacy/medicine/<medicine_id>
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/medicine/<medicine_id>', methods=['GET'])
@jwt_required()
def get_medicine(medicine_id):
    """Get detailed information about a specific medicine."""
    try:
        medicines = load_medicines_db()
        medicine = next((m for m in medicines if m.get('id') == medicine_id), None)

        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404

        # Also fetch same-salt alternatives
        salt = medicine.get('salt_composition') or medicine.get('generic_name', '')
        similar_result = compare_medicines_by_salt(salt, medicines, top_n=6)
        similar = [m for m in similar_result.get('medicines', []) if m.get('id') != medicine_id][:5]

        return jsonify({
            'success': True,
            'medicine': medicine,
            'similar_medicines': similar,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/pharmacy/search?q=<query>
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/search', methods=['GET'])
@jwt_required()
def search_medicine():
    """Search medicines by name, salt, generic name, or brand."""
    try:
        query = request.args.get('q', '').strip().lower()
        limit = min(request.args.get('limit', 20, type=int), 50)

        if not query or len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400

        medicines = load_medicines_db()
        results = []
        for m in medicines:
            all_text = ' '.join([
                m.get('name', ''),
                m.get('generic_name', ''),
                m.get('salt_composition', ''),
                m.get('type', ''),
                ' '.join(m.get('brand_names', [])),
                ' '.join(m.get('for_conditions', [])),
            ]).lower()
            if query in all_text:
                results.append(m)

        return jsonify({
            'success': True,
            'query': query,
            'results': results[:limit],
            'total': len(results)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  GET /api/pharmacy/stats
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get pharmacy module statistics."""
    try:
        email = get_jwt_identity()
        user_scans = len(pharmacy_history.get(email, []))
        medicines = load_medicines_db()

        return jsonify({
            'success': True,
            'total_scans': user_scans,
            'medicines_in_db': len(medicines),
            'features': [
                'OCR-based medicine identification',
                'Multi-pass rotation-aware text extraction',
                'Salt/active-ingredient comparison',
                'Condition-based medicine recommendations',
                'Price vs efficacy analysis',
            ]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  DELETE /api/pharmacy/history/<scan_id>
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/history/<scan_id>', methods=['DELETE'])
@jwt_required()
def delete_scan(scan_id):
    """Delete a scan from history."""
    try:
        email = get_jwt_identity()
        if email in pharmacy_history:
            pharmacy_history[email] = [
                s for s in pharmacy_history[email] if s.get('id') != scan_id
            ]
        return jsonify({'success': True, 'message': 'Scan deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
#  POST /api/pharmacy/check-interactions
#  Check drug-drug interactions
# ═══════════════════════════════════════════════════════════════

@pharmacy_bp.route('/check-interactions', methods=['POST'])
@jwt_required()
def check_interactions():
    """Check for drug-to-drug interactions among a list of medicine IDs."""
    try:
        data = request.get_json(silent=True) or {}
        medicine_ids = data.get('medicine_ids', [])

        if not medicine_ids or not isinstance(medicine_ids, list):
            return jsonify({'error': 'medicine_ids must be a non-empty list'}), 400

        medicines = load_medicines_db()
        selected_meds = [m for m in medicines if m.get('id') in medicine_ids]

        if len(selected_meds) < 2:
            return jsonify({
                'error': 'At least 2 valid medicine IDs required to check interactions'
            }), 400

        interactions_detected = []
        n_meds = len(selected_meds)

        for i in range(n_meds):
            for j in range(i + 1, n_meds):
                med1 = selected_meds[i]
                med2 = selected_meds[j]

                conflict = False
                matched_trigger = ''

                def _words_match(query: str, target: str) -> bool:
                    q = re.sub(r'[^a-z0-9\s]', '', query.lower()).strip()
                    t = re.sub(r'[^a-z0-9\s]', '', target.lower()).strip()
                    if not q or not t:
                        return False
                    if q in t or t in q:
                        return True
                    q_words = [re.sub(r's$', '', w) for w in q.split() if len(w) > 3]
                    t_words = [re.sub(r's$', '', w) for w in t.split() if len(w) > 3]
                    return any(qw in t_words for qw in q_words)

                med1_targets = [med2.get('name', ''), med2.get('generic_name', ''), med2.get('type', '')]
                for query in med1.get('interactions', []):
                    if any(_words_match(query, tgt) for tgt in med1_targets):
                        conflict = True
                        matched_trigger = query
                        break

                if not conflict:
                    med2_targets = [med1.get('name', ''), med1.get('generic_name', ''), med1.get('type', '')]
                    for query in med2.get('interactions', []):
                        if any(_words_match(query, tgt) for tgt in med2_targets):
                            conflict = True
                            matched_trigger = query
                            break

                if conflict:
                    interactions_detected.append({
                        'med1': {
                            'id': med1.get('id'),
                            'name': med1.get('name'),
                            'generic_name': med1.get('generic_name'),
                        },
                        'med2': {
                            'id': med2.get('id'),
                            'name': med2.get('name'),
                            'generic_name': med2.get('generic_name'),
                        },
                        'trigger': matched_trigger,
                        'severity': 'moderate',
                        'description': (
                            f"Potential interaction: {med1.get('name')} and {med2.get('name')} "
                            f"may interact (matched: '{matched_trigger}'). "
                            f"Consult a pharmacist or physician before co-administering."
                        )
                    })

        return jsonify({
            'success': True,
            'medicines_checked': [m.get('name') for m in selected_meds],
            'interactions': interactions_detected,
            'interaction_count': len(interactions_detected),
            'safe': len(interactions_detected) == 0,
        }), 200

    except Exception as e:
        logger.error(f"Interaction check error: {e}", exc_info=True)
        return jsonify({'error': f'Interaction check failed: {str(e)}'}), 500


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def _efficacy_label(rating: float) -> str:
    """Convert numeric efficacy rating to human-readable label."""
    if rating is None:
        return 'Unknown'
    if rating >= 4.5:
        return 'Excellent'
    if rating >= 4.0:
        return 'Very Good'
    if rating >= 3.5:
        return 'Good'
    if rating >= 3.0:
        return 'Moderate'
    return 'Below Average'
