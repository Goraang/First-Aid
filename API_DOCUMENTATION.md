# 🔌 FirstAid API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Endpoints

### Register New User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response (409 Conflict):**
```json
{
  "error": "Email already registered"
}
```

---

### User Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid email or password"
}
```

---

### Get Current User

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

## 💊 Pharmacy Endpoints

### Scan Medicine from Image

**Endpoint:** `POST /pharmacy/scan`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Parameters:**
- `image` (File, required): Medicine image (JPG, PNG, WebP, BMP)
- Max file size: 10MB

**Example:**
```bash
curl -X POST http://localhost:5000/api/pharmacy/scan \
  -H "Authorization: Bearer <token>" \
  -F "image=@medicine.jpg"
```

**Response (200 OK):**
```json
{
  "medicine": {
    "id": "med_001",
    "name": "Paracetamol",
    "generic_name": "Acetaminophen",
    "type": "Analgesic / Antipyretic",
    "composition": "Paracetamol 500mg",
    "usage": "Used to treat mild to moderate pain and reduce fever.",
    "dosage": "1 tablet every 4-6 hours. Maximum 4g per day.",
    "side_effects": ["Nausea", "Allergic reactions", "Rash"],
    "warnings": [
      "May cause liver damage if taken in excessive amounts",
      "Do not mix with alcohol",
      "Overdose can be fatal"
    ],
    "interactions": ["Alcohol", "Warfarin"],
    "storage": "Store at room temperature, away from moisture"
  },
  "confidence": 0.95,
  "extracted_text": "Paracetamol 500mg...",
  "scan_id": "scan_abc123",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "No image provided or file too large"
}
```

---

### Get Medicine History

**Endpoint:** `GET /pharmacy/history`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 10)

**Example:**
```bash
curl http://localhost:5000/api/pharmacy/history?page=1&limit=5 \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "history": [
    {
      "scan_id": "scan_abc123",
      "medicine_name": "Paracetamol",
      "confidence": 0.95,
      "image_url": "/uploads/scan_abc123.jpg",
      "timestamp": "2024-01-15T10:35:00Z"
    },
    {
      "scan_id": "scan_def456",
      "medicine_name": "Amoxicillin",
      "confidence": 0.92,
      "image_url": "/uploads/scan_def456.jpg",
      "timestamp": "2024-01-15T09:20:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 5,
    "total": 23,
    "pages": 5
  }
}
```

---

### Get Medicine Details

**Endpoint:** `GET /pharmacy/medicine/{medicine_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl http://localhost:5000/api/pharmacy/medicine/med_001 \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "medicine": {
    "id": "med_001",
    "name": "Paracetamol",
    "generic_name": "Acetaminophen",
    "type": "Analgesic / Antipyretic",
    "composition": "Paracetamol 500mg",
    "usage": "...",
    "dosage": "...",
    "side_effects": [...],
    "warnings": [...],
    "interactions": [...],
    "storage": "..."
  }
}
```

---

### Search Medicines

**Endpoint:** `GET /pharmacy/search`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `q` (string, required): Search query

**Example:**
```bash
curl http://localhost:5000/api/pharmacy/search?q=paracetamol \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "med_001",
      "name": "Paracetamol",
      "generic_name": "Acetaminophen",
      "type": "Analgesic / Antipyretic",
      "match_score": 0.98
    },
    {
      "id": "med_005",
      "name": "Paracetamol + Ibuprofen",
      "generic_name": "Paracetamol + Ibuprofen",
      "type": "Pain Reliever Combination",
      "match_score": 0.85
    }
  ],
  "total": 2
}
```

---

### Get Pharmacy Statistics

**Endpoint:** `GET /pharmacy/stats`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "total_scans": 45,
  "medicines_identified": 38,
  "accuracy": 98.5,
  "average_confidence": 0.94,
  "scans_this_week": 12,
  "most_scanned": "Paracetamol"
}
```

---

### Delete Scan History Entry

**Endpoint:** `DELETE /pharmacy/history/{scan_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Scan deleted successfully",
  "scan_id": "scan_abc123"
}
```

---

## 🔬 Dermatology Endpoints

### Analyze Skin Condition

**Endpoint:** `POST /dermatology/analyze`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Parameters:**
- `image` (File, required): Skin condition image
- `body_part` (string, optional): Affected body part (e.g., "face", "arm", "leg")
- `symptoms` (array, optional): Reported symptoms

**Example:**
```bash
curl -X POST http://localhost:5000/api/dermatology/analyze \
  -H "Authorization: Bearer <token>" \
  -F "image=@skin_condition.jpg" \
  -F "body_part=face" \
  -F 'symptoms=["itching", "redness"]'
```

**Response (200 OK):**
```json
{
  "disease": {
    "id": "disease_001",
    "name": "Acne",
    "scientific_name": "Acne vulgaris",
    "description": "A common skin condition characterized by pimples...",
    "causes": [
      "Excess sebum production",
      "Bacterial growth (P. acnes)",
      "Dead skin cells",
      "Hormonal changes"
    ],
    "symptoms": [
      "Pimples",
      "Blackheads",
      "Whiteheads",
      "Redness",
      "Inflammation"
    ],
    "treatments": [
      "Benzoyl peroxide",
      "Salicylic acid",
      "Topical retinoids",
      "Oral antibiotics"
    ],
    "prevention": [
      "Regular cleansing",
      "Avoid touching face",
      "Use non-comedogenic products"
    ],
    "affected_areas": ["Face", "Chest", "Shoulders", "Back"]
  },
  "severity": "mild",
  "confidence": 0.92,
  "body_part": "face",
  "analysis_id": "analysis_xyz789",
  "timestamp": "2024-01-15T11:00:00Z",
  "recommendations": {
    "immediate": "Keep the area clean and dry",
    "medication": "Consider benzoyl peroxide or salicylic acid",
    "lifestyle": "Reduce stress, avoid touching face",
    "follow_up": "Consult dermatologist if symptoms persist"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "No image provided or file too large"
}
```

---

### Get Skin Analysis History

**Endpoint:** `GET /dermatology/history`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 10)

**Response (200 OK):**
```json
{
  "history": [
    {
      "analysis_id": "analysis_xyz789",
      "disease_name": "Acne",
      "severity": "mild",
      "confidence": 0.92,
      "body_part": "face",
      "image_url": "/uploads/analysis_xyz789.jpg",
      "timestamp": "2024-01-15T11:00:00Z"
    },
    {
      "analysis_id": "analysis_xyz790",
      "disease_name": "Eczema",
      "severity": "moderate",
      "confidence": 0.88,
      "body_part": "hands",
      "image_url": "/uploads/analysis_xyz790.jpg",
      "timestamp": "2024-01-15T10:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 12,
    "pages": 2
  }
}
```

---

### Get Disease Information

**Endpoint:** `GET /dermatology/disease/{disease_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl http://localhost:5000/api/dermatology/disease/disease_001 \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
{
  "disease": {
    "id": "disease_001",
    "name": "Acne",
    "scientific_name": "Acne vulgaris",
    "description": "...",
    "causes": [...],
    "symptoms": [...],
    "treatments": [...],
    "prevention": [...],
    "severity": "mild",
    "affected_areas": [...]
  }
}
```

---

### Get Dermatology Statistics

**Endpoint:** `GET /dermatology/stats`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "total_analyses": 23,
  "diseases_detected": 8,
  "average_confidence": 0.91,
  "severity_breakdown": {
    "mild": 12,
    "moderate": 8,
    "severe": 3
  },
  "most_detected": "Acne",
  "analyses_this_month": 15
}
```

---

### Delete Skin Analysis

**Endpoint:** `DELETE /dermatology/history/{analysis_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Analysis deleted successfully",
  "analysis_id": "analysis_xyz789"
}
```

---

## 🏥 Health Check

### System Health

**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "ok",
  "message": "FirstAid API is running",
  "version": "2.0.0"
}
```

---

## Error Handling

All error responses follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| `INVALID_INPUT` | 400 | Bad request or invalid parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists (email taken) |
| `SERVER_ERROR` | 500 | Internal server error |
| `PROCESSING_ERROR` | 500 | Error during image processing/OCR |

---

## Rate Limiting

Currently, no rate limiting is enforced. In production:
- Rate limit: 100 requests per minute per user
- File upload limit: 10MB per request
- Scan timeout: 60 seconds

---

## Response Times

Expected response times:
- **Authentication**: ~100ms
- **Medicine Scan**: 2-5 seconds (OCR processing)
- **Skin Analysis**: 2-4 seconds (CV processing)
- **History Retrieval**: ~200ms
- **Database Queries**: ~100-300ms

---

## Example Integration

### JavaScript/Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('firstaid_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Register
async function register(name, email, password) {
  const { data } = await api.post('/auth/register', {
    name, email, password
  });
  localStorage.setItem('firstaid_token', data.token);
  return data;
}

// Scan medicine
async function scanMedicine(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const { data } = await api.post('/pharmacy/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}

// Analyze skin
async function analyzeSkin(imageFile, bodyPart) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('body_part', bodyPart);
  
  const { data } = await api.post('/dermatology/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}
```

### Python/Requests

```python
import requests
import json

BASE_URL = 'http://localhost:5000/api'

class FirstAidClient:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    
    def register(self, name, email, password):
        resp = requests.post(f'{BASE_URL}/auth/register', json={
            'name': name,
            'email': email,
            'password': password
        })
        data = resp.json()
        self.token = data['token']
        return data
    
    def scan_medicine(self, image_path):
        with open(image_path, 'rb') as f:
            files = {'image': f}
            headers = {'Authorization': f'Bearer {self.token}'}
            resp = requests.post(
                f'{BASE_URL}/pharmacy/scan',
                files=files,
                headers=headers
            )
        return resp.json()
    
    def analyze_skin(self, image_path, body_part='unknown'):
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'body_part': body_part}
            headers = {'Authorization': f'Bearer {self.token}'}
            resp = requests.post(
                f'{BASE_URL}/dermatology/analyze',
                files=files,
                data=data,
                headers=headers
            )
        return resp.json()
```

---

## Webhooks (Future)

Future versions may support webhooks for:
- Scan completion notifications
- Analysis result updates
- User activity alerts

---

## Versioning

Current API version: **2.0.0**

Backward compatibility is maintained for all versions with v1 endpoints.

---

## Support

For API issues or questions:
1. Check this documentation
2. Review example integrations above
3. Check browser console (F12) for error details
4. See INSTALLATION.md troubleshooting section

---

**API Documentation v2.0 | Last Updated: January 2024**
