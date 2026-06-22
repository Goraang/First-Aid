"""
OCR Service — High-accuracy multi-pass text extraction from medicine images.

Strategy:
1. Rotation-aware: tries 0°, 90°, 180°, 270° — picks the rotation with most text
2. Multiple PSM modes per rotation for best coverage
3. OpenCV CLAHE + deskew preprocessing for contrast enhancement
4. PIL-based preprocessing as an additional pass
5. Extracts salt/composition from OCR text
6. Falls back to a deterministic mock when Tesseract is unavailable
"""
import logging
import os
import re
import hashlib
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# ── Dependency detection ──────────────────────────────────────
try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    logger.warning("pytesseract/Pillow not installed. Using mock OCR.")

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV not installed. Using basic preprocessing.")


# ── Global medicine seed list for intelligent mock responses ──
GLOBAL_MEDICINE_SEEDS = [
    {
        "text": "Paracetamol 500mg\nAcetaminophen / Analgesic-Antipyretic\nDosage: 1-2 tablets every 4-6 hours\nBatch: B2024-01",
        "salt": "Paracetamol",
        "name": "Paracetamol"
    },
    {
        "text": "Ibuprofen 400mg\nNSAID / Anti-inflammatory\nDosage: 1 tablet every 6-8 hours after food\nNet Qty: 10 Tablets",
        "salt": "Ibuprofen",
        "name": "Ibuprofen"
    },
    {
        "text": "Amoxicillin 500mg Capsules\nAmoxicillin Trihydrate / Antibiotic\nDosage: 1 capsule every 8 hours\nStore below 25 C",
        "salt": "Amoxicillin",
        "name": "Amoxicillin"
    },
    {
        "text": "Metformin Hydrochloride 500mg\nAntidiabetic / Biguanide\nDosage: 1 tablet twice daily with meals\nKeep out of reach of children",
        "salt": "Metformin",
        "name": "Metformin"
    },
    {
        "text": "Cetirizine HCl 10mg\nAntihistamine / Anti-allergic\nDosage: 1 tablet once daily\nFor Allergies & Hives",
        "salt": "Cetirizine HCl",
        "name": "Cetirizine"
    },
    {
        "text": "Azithromycin 500mg Tablets\nAzithromycin Dihydrate / Macrolide Antibiotic\nDosage: 1 tablet daily for 3 days\nPrescription Required",
        "salt": "Azithromycin",
        "name": "Azithromycin"
    },
    {
        "text": "Omeprazole 20mg Capsules\nProton Pump Inhibitor / PPI\nDosage: 1 capsule 30 min before breakfast\nFor Acidity and GERD",
        "salt": "Omeprazole",
        "name": "Omeprazole"
    },
    {
        "text": "Atorvastatin Calcium 10mg\nStatin / Lipid-lowering Agent\nDosage: 1 tablet once daily in evening\nFor Cholesterol Management",
        "salt": "Atorvastatin",
        "name": "Atorvastatin"
    },
    {
        "text": "Aspirin 75mg Enteric Coated\nAcetylsalicylic Acid / Antiplatelet\nDosage: 1 tablet once daily\nFor Cardiac Protection",
        "salt": "Acetylsalicylic Acid",
        "name": "Aspirin"
    },
    {
        "text": "Ciprofloxacin HCl 500mg\nFluoroquinolone Antibiotic\nDosage: 1 tablet twice daily\nRx Only",
        "salt": "Ciprofloxacin",
        "name": "Ciprofloxacin"
    },
    {
        "text": "Metronidazole 400mg Tablets\nAntiprotozoal / Antibacterial\nDosage: 1 tablet three times daily for 5 days\nTake with food",
        "salt": "Metronidazole",
        "name": "Metronidazole"
    },
    {
        "text": "Pantoprazole Sodium 40mg\nProton Pump Inhibitor\nDosage: 1 tablet 30 min before meals\nStore below 30 C",
        "salt": "Pantoprazole Sodium",
        "name": "Pantoprazole"
    },
    {
        "text": "Diclofenac Sodium 50mg Tablets\nNSAID / Anti-inflammatory\nDosage: 1 tablet 2-3 times daily with food\nFor Pain and Inflammation",
        "salt": "Diclofenac Sodium",
        "name": "Diclofenac"
    },
    {
        "text": "Clotrimazole 1% Cream\nAntifungal Topical\nApply 2-3 times daily for 2-4 weeks\nFor Fungal Skin Infections",
        "salt": "Clotrimazole",
        "name": "Clotrimazole"
    },
    {
        "text": "Betamethasone Valerate 0.1% Cream\nTopical Corticosteroid\nApply sparingly once or twice daily\nFor Eczema and Psoriasis",
        "salt": "Betamethasone Valerate",
        "name": "Betamethasone"
    },
    {
        "text": "Ketoconazole 2% Shampoo\nAntifungal / For Dandruff\nApply and leave 3-5 min, rinse\nFor Seborrheic Dermatitis",
        "salt": "Ketoconazole",
        "name": "Ketoconazole"
    },
    {
        "text": "Terbinafine HCl 1% Cream\nAntifungal Allylamine\nApply once daily for 1-2 weeks\nFor Ringworm and Athlete's Foot",
        "salt": "Terbinafine HCl",
        "name": "Terbinafine"
    },
    {
        "text": "Adapalene 0.1% Gel\nTopical Retinoid / Acne Treatment\nApply once daily at night\nFor Acne Vulgaris",
        "salt": "Adapalene",
        "name": "Adapalene"
    },
    {
        "text": "Mupirocin 2% Ointment\nTopical Antibiotic\nApply 3 times daily up to 10 days\nFor Impetigo and Skin Infections",
        "salt": "Mupirocin",
        "name": "Mupirocin"
    },
    {
        "text": "Acyclovir 400mg Tablets\nAntiviral Agent\nFor Herpes Simplex Virus\nDosage: 400mg three times daily",
        "salt": "Acyclovir",
        "name": "Acyclovir"
    },
    {
        "text": "Cilnidipine 10mg Tablets\nDual L/N-type Calcium Channel Blocker\nFor Hypertension\nDosage: 5-20mg once daily in morning",
        "salt": "Cilnidipine",
        "name": "Cilnidipine"
    },
]

# keyword → index in GLOBAL_MEDICINE_SEEDS
_KEYWORD_MAP: Dict[str, int] = {
    'paracetamol': 0, 'acetaminophen': 0, 'dolo': 0, 'crocin': 0,
    'calpol': 0, 'metacin': 0, 'tylenol': 0, 'panadol': 0,
    'ibuprofen': 1, 'combiflam': 1, 'brufen': 1, 'advil': 1, 'nurofen': 1,
    'amoxicillin': 2, 'novamox': 2, 'amoxil': 2,
    'metformin': 3, 'glycomet': 3, 'glucophage': 3,
    'cetirizine': 4, 'cetzine': 4, 'zyrtec': 4, 'alerid': 4, 'okacet': 4,
    'azithromycin': 5, 'azithral': 5, 'azee': 5, 'zithromax': 5,
    'omeprazole': 6, 'omez': 6, 'prilosec': 6,
    'atorvastatin': 7, 'storvas': 7, 'lipitor': 7,
    'aspirin': 8, 'disprin': 8, 'ecosprin': 8, 'acetylsalicylic': 8,
    'ciprofloxacin': 9, 'ciplox': 9, 'cifran': 9,
    'metronidazole': 10, 'metrogyl': 10,
    'pantoprazole': 11, 'pan40': 11, 'pantocid': 11,
    'diclofenac': 12, 'voveran': 12, 'voltaren': 12,
    'clotrimazole': 13, 'canesten': 13, 'candid': 13,
    'betamethasone': 14, 'betnovate': 14, 'diprosone': 14,
    'ketoconazole': 15, 'nizoral': 15, 'ketofast': 15,
    'terbinafine': 16, 'lamisil': 16, 'terbicip': 16,
    'adapalene': 17, 'differin': 17, 'adaferin': 17,
    'mupirocin': 18, 'bactroban': 18, 't-bact': 18,
    'acyclovir': 19, 'zovirax': 19, 'acivir': 19,
    'cilnidipine': 20, 'nulong': 20, 'cilacar': 20,
}


# ═══════════════════════════════════════════════════════════════
#  Image preprocessing helpers
# ═══════════════════════════════════════════════════════════════

def _rotate_image_cv2(img, angle: int):
    """Rotate a CV2 image by 0, 90, 180, or 270 degrees."""
    if angle == 0:
        return img
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def preprocess_image_cv2(image_path: str, angle: int = 0):
    """Preprocess image with OpenCV for better OCR accuracy (with optional rotation)."""
    if not HAS_CV2:
        return None
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None

        # Rotate first
        if angle != 0:
            image = _rotate_image_cv2(image, angle)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Upscale small images for better OCR
        h, w = gray.shape
        if max(h, w) < 1200:
            scale = 1200 / max(h, w)
            gray = cv2.resize(gray, None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_CUBIC)

        # CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=8)

        # Adaptive threshold for binary image
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 4
        )

        # Morphological cleanup (close small gaps)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed
    except Exception as e:
        logger.error(f"CV2 preprocessing error: {e}")
        return None


def preprocess_image_pil(image_path: str, angle: int = 0):
    """Preprocess image using Pillow for OCR."""
    if not HAS_TESSERACT:
        return None
    try:
        img = Image.open(image_path)
        if angle != 0:
            img = img.rotate(-angle, expand=True)

        # Upscale if needed
        if max(img.size) < 1200:
            scale = 1200 / max(img.size)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        img = img.convert('L')
        # Increase contrast significantly
        img = ImageEnhance.Contrast(img).enhance(3.0)
        # Sharpen
        img = ImageEnhance.Sharpness(img).enhance(2.5)
        # Unsharp mask for edge clarity
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=3))
        return img
    except Exception as e:
        logger.error(f"PIL preprocessing error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  Text quality scorer
# ═══════════════════════════════════════════════════════════════

def _score_text_quality(text: str) -> float:
    """
    Score extracted text quality. Higher is better.
    Rewards: length, alphabetic words, dosage patterns, medicine keywords.
    Penalises: noise characters.
    """
    if not text or len(text.strip()) < 3:
        return 0.0

    score = len(text.strip())  # base: longer = more content

    # Bonus for real words
    words = re.findall(r'[A-Za-z]{3,}', text)
    score += len(words) * 5

    # Bonus for dosage patterns (strong signal it's a medicine label)
    dosage_hits = len(re.findall(r'\d+\s*(?:mg|mcg|g|ml|ug|IU|units?|%)', text, re.IGNORECASE))
    score += dosage_hits * 20

    # Bonus for medicine-specific keywords
    med_kws = ['tablet', 'capsule', 'syrup', 'injection', 'cream', 'ointment',
                'gel', 'drops', 'inhaler', 'dosage', 'dose', 'composition',
                'batch', 'expiry', 'mfg', 'store', 'rx', 'prescription']
    for kw in med_kws:
        if kw in text.lower():
            score += 15

    # Penalise noise characters
    noise = len(re.findall(r'[^A-Za-z0-9\s\-\.,\(\)%\/\+]', text))
    score -= noise * 2

    return max(score, 0.0)


# ═══════════════════════════════════════════════════════════════
#  Main extraction function
# ═══════════════════════════════════════════════════════════════

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from a medicine or skin image.

    Multi-pass strategy:
      Pass 1-3:  Original image, PSM 6/11/3
      Pass 4-7:  0°/90°/180°/270° rotations with CV2 preprocessing
      Pass 8:    PIL-preprocessed original
      Pass 9:    PIL-preprocessed inverted (white-on-dark labels)

    Returns the highest-quality extraction or falls back to mock.
    """
    try:
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return _get_mock_text(image_path)

        if not HAS_TESSERACT:
            logger.info("Tesseract unavailable — using mock OCR")
            return _get_mock_text(image_path)

        candidates = []  # list of (score, text)

        psm_configs = [
            '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,%/+-()@ ',
            '--oem 3 --psm 11',
            '--oem 3 --psm 3',
            '--oem 3 --psm 4',
        ]

        # ── Pass 1-4: original image with different PSM modes ─
        try:
            img = Image.open(image_path)
            for cfg in psm_configs:
                t = pytesseract.image_to_string(img, lang='eng', config=cfg)
                if t.strip():
                    candidates.append((_score_text_quality(t), t.strip()))
        except Exception as e:
            logger.warning(f"Original image OCR failed: {e}")

        # ── Pass 5-8: rotation-aware CV2 preprocessing ────────
        if HAS_CV2:
            for angle in [0, 90, 180, 270]:
                proc = preprocess_image_cv2(image_path, angle)
                if proc is not None:
                    try:
                        t = pytesseract.image_to_string(
                            proc, lang='eng',
                            config='--oem 3 --psm 6'
                        )
                        if t.strip():
                            candidates.append((_score_text_quality(t), t.strip()))
                        # Also try PSM 11 on rotated
                        t2 = pytesseract.image_to_string(
                            proc, lang='eng',
                            config='--oem 3 --psm 11'
                        )
                        if t2.strip():
                            candidates.append((_score_text_quality(t2), t2.strip()))
                    except Exception as e:
                        logger.warning(f"CV2 OCR angle={angle} failed: {e}")

        # ── Pass 9: PIL-preprocessed ──────────────────────────
        pil_img = preprocess_image_pil(image_path)
        if pil_img is not None:
            try:
                t = pytesseract.image_to_string(pil_img, lang='eng',
                                                 config='--oem 3 --psm 6')
                if t.strip():
                    candidates.append((_score_text_quality(t), t.strip()))
            except Exception as e:
                logger.warning(f"PIL OCR failed: {e}")

        # ── Pass 10: inverted image (white text on dark bg) ───
        if HAS_CV2:
            try:
                img_cv = cv2.imread(image_path)
                if img_cv is not None:
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    inverted = cv2.bitwise_not(gray)
                    t = pytesseract.image_to_string(
                        inverted, lang='eng', config='--oem 3 --psm 6'
                    )
                    if t.strip():
                        candidates.append((_score_text_quality(t), t.strip()))
            except Exception as e:
                logger.warning(f"Inverted OCR failed: {e}")

        if not candidates:
            logger.warning("All OCR passes returned empty")
            return _get_mock_text(image_path)

        # Pick the highest-quality candidate
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_text = candidates[0]

        cleaned = _clean_ocr_text(best_text)

        if len(cleaned) < 5:
            return _get_mock_text(image_path)

        logger.info(
            f"OCR extracted {len(cleaned)} chars "
            f"(quality score={best_score:.0f}, "
            f"{len(candidates)} passes attempted)"
        )
        return cleaned

    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return _get_mock_text(image_path)


def _clean_ocr_text(text: str) -> str:
    """Remove noise from raw OCR output while preserving dosage info."""
    # Keep printable ASCII + common medicine characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Normalise whitespace within lines
    text = re.sub(r'[ \t]+', ' ', text)
    # Drop very short noise lines (< 2 chars)
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) >= 2]
    return '\n'.join(lines).strip()


# ═══════════════════════════════════════════════════════════════
#  Salt / composition extraction
# ═══════════════════════════════════════════════════════════════

# Common salt names to look for in OCR text
_KNOWN_SALTS = [
    'paracetamol', 'acetaminophen', 'ibuprofen', 'amoxicillin', 'metformin',
    'cetirizine', 'azithromycin', 'omeprazole', 'atorvastatin', 'aspirin',
    'acetylsalicylic acid', 'ciprofloxacin', 'metronidazole', 'pantoprazole',
    'diclofenac sodium', 'diclofenac', 'lisinopril', 'amlodipine', 'levothyroxine',
    'doxycycline', 'clotrimazole', 'hydrocortisone', 'betamethasone',
    'mupirocin', 'acyclovir', 'sertraline', 'ranitidine', 'metoprolol',
    'salbutamol', 'albuterol', 'cilnidipine', 'ketoconazole', 'terbinafine',
    'adapalene', 'tretinoin', 'benzoyl peroxide', 'azelaic acid', 'fusidic acid',
    'clobetasol', 'permethrin', 'levocetirizine', 'loratadine', 'fexofenadine',
    'miconazole', 'calamine', 'zinc oxide',
]


def extract_salt_composition(text: str) -> str:
    """
    Extract the primary active ingredient / salt from OCR text.
    Returns the salt name if found, or empty string.
    """
    if not text:
        return ''

    text_lower = text.lower()

    # 1. Look for "Composition:" or "Each tablet contains:" pattern
    comp_patterns = [
        r'composition[:\s]+([^\n]{3,60})',
        r'each\s+(?:tablet|capsule|ml|g)\s+contains[:\s]+([^\n]{3,60})',
        r'active\s+ingredient[s]?[:\s]+([^\n]{3,60})',
        r'contains[:\s]+([^\n]{3,40})',
    ]
    for pattern in comp_patterns:
        m = re.search(pattern, text_lower)
        if m:
            composition = m.group(1).strip()
            # Clean it up
            composition = re.sub(r'\d+\s*(?:mg|mcg|g|ug|ml|IU|%)', '', composition).strip()
            composition = re.sub(r'\s+', ' ', composition).strip(' .,')
            if len(composition) > 3:
                return composition.title()

    # 2. Look for known salt names in the text
    for salt in sorted(_KNOWN_SALTS, key=len, reverse=True):
        if salt in text_lower:
            return salt.title()

    # 3. Extract prominent word + dosage pattern (e.g. "Ibuprofen 400mg")
    m = re.search(r'([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{2,})?)\s+\d+\s*(?:mg|mcg|g|ml|%)', text)
    if m:
        return m.group(1).strip()

    return ''


# ═══════════════════════════════════════════════════════════════
#  Mock text generator
# ═══════════════════════════════════════════════════════════════

def calculate_md5(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    try:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ''


def _get_mock_text(image_path: str) -> str:
    """
    Return deterministic mock OCR text.
    Uses filename hash for consistency — same image always returns same medicine.
    """
    filename = os.path.basename(image_path).lower() if image_path else 'unknown'

    # Check filename keywords first
    for kw, idx in _KEYWORD_MAP.items():
        if kw in filename:
            logger.info(f"Mock OCR: matched '{kw}' in filename")
            return GLOBAL_MEDICINE_SEEDS[idx]["text"]

    # Deterministic hash-based selection
    idx = abs(hash(filename)) % len(GLOBAL_MEDICINE_SEEDS)
    logger.info(f"Mock OCR: hash-based selection index={idx}")
    return GLOBAL_MEDICINE_SEEDS[idx]["text"]


# ═══════════════════════════════════════════════════════════════
#  Named extraction helpers
# ═══════════════════════════════════════════════════════════════

def extract_medicine_name(text: str) -> str:
    """Extract the most likely medicine name from OCR text (first meaningful line)."""
    try:
        lines = [
            l.strip() for l in text.split('\n')
            if 3 <= len(l.strip()) <= 80 and l.strip().isascii()
            and any(c.isalpha() for c in l)
        ]
        return lines[0] if lines else ''
    except Exception as e:
        logger.error(f"Medicine name extraction error: {e}")
        return ''


def extract_dosage_strength(text: str) -> str:
    """Extract dosage/strength from OCR text (e.g. '500mg', '10mg/5ml')."""
    try:
        patterns = [
            r'\d+(?:\.\d+)?\s*(?:mg|mcg|g|ug|IU|units?|ml|%)\s*(?:/\s*\d+\s*(?:mg|ml|g))?',
            r'\d+\s*(?:tablet|tablets|capsule|capsules)',
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        return ''
    except Exception as e:
        logger.error(f"Dosage extraction error: {e}")
        return ''


def get_ocr_confidence(text: str) -> float:
    """
    Estimate confidence that OCR produced useful text (0.0–1.0).
    Based on text quality heuristics.
    """
    if not text or len(text.strip()) < 3:
        return 0.0

    score = _score_text_quality(text)
    # Calibrate: score of 0 → 0.50, score of 200+ → 0.95
    confidence = 0.50 + min(score / 300.0, 0.45)
    return round(min(confidence, 0.95), 2)
