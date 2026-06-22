# 🚀 FirstAid Platform - Installation & Quick Start Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Project Structure](#project-structure)

---

## System Requirements

### Global Prerequisites
- **Python 3.9+** (for backend)
- **Node.js 16+** & **npm 8+** (for frontend)
- **Tesseract-OCR** (for medicine text extraction)
- **Git** (optional, for version control)

### macOS Installation
```bash
# Using Homebrew - Install Tesseract
brew install tesseract

# Verify installation
tesseract --version
```

### Ubuntu/Debian Installation
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
tesseract --version
```

### Windows Installation
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Follow the installer wizard
- Add to PATH: `C:\Program Files\Tesseract-OCR`

---

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd /Users/goraangnayyar/firstaid-platform/backend
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Environment File
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and set your configuration
nano .env
```

**Important .env values:**
```env
FLASK_ENV=development
FLASK_PORT=5000
JWT_SECRET_KEY=your-super-secret-key-change-in-production
TESSERACT_PATH=/usr/local/bin/tesseract  # Update based on your installation
```

### Step 5: Create Uploads Directory
```bash
mkdir -p uploads
chmod 755 uploads
```

### Step 6: Test Backend
```bash
# Run the backend server
python run.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * Warning: This is a development server. Do not use it in production.
```

Visit: `http://localhost:5000/api/health`
Expected response: `{"status": "ok", "message": "FirstAid API is running"}`

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd /Users/goraangnayyar/firstaid-platform/frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Create Environment File
```bash
# Copy the example .env file
cp .env.example .env

# Verify .env content
cat .env
```

**Expected .env content:**
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENV=development
```

### Step 4: Start Development Server
```bash
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view firstaid-platform in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

The app should automatically open in your default browser.

---

## Running the Application

### Complete Startup Sequence

**Terminal 1 - Backend:**
```bash
cd /Users/goraangnayyar/firstaid-platform/backend
source venv/bin/activate
python run.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd /Users/goraangnayyar/firstaid-platform/frontend
npm start
# App opens at http://localhost:3000
```

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000/api
- **Health Check:** http://localhost:5000/api/health

---

## Testing the Features

### 1. User Authentication
```
1. Go to http://localhost:3000
2. Click "Get Started Free" or "Sign Up"
3. Enter:
   - Name: John Doe
   - Email: john@example.com
   - Password: password123
4. Submit the form
5. You should be redirected to home page as logged-in user
```

### 2. Pharmacy Module
```
1. Click "💊 Pharmacy" from navbar
2. Upload a clear image of:
   - Medicine strip
   - Tablet packaging
   - Medicine label
3. Click "🔍 Scan Medicine"
4. Wait for OCR processing
5. View extracted medicine information
6. Check history tab to see past scans
```

### 3. Dermatology Module
```
1. Click "🔬 Dermatology" from navbar
2. Upload a clear image of skin condition:
   - Acne
   - Eczema
   - Rashes
   - Any skin marking
3. (Optional) Select affected body part
4. Click "🔍 Analyze Skin"
5. View diagnosis and recommendations
6. Check history tab
```

### 4. User Profile
```
1. Click "Profile" in navbar (when logged in)
2. View scan history
3. View statistics
4. Review saved analyses
```

---

## Troubleshooting

### Backend Issues

**Issue: "ModuleNotFoundError: No module named 'pytesseract'"**
```bash
# Solution: Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Issue: "Tesseract is not installed or not found in PATH"**
```bash
# Check installation
tesseract --version

# If not found, reinstall:
# macOS:
brew install tesseract

# Ubuntu:
sudo apt-get install tesseract-ocr

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**Issue: "Port 5000 is already in use"**
```bash
# Find and kill process using port 5000
# macOS/Linux:
lsof -i :5000
kill -9 <PID>

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port:
export FLASK_PORT=5001
python run.py
```

**Issue: "CORS Error" when calling API from frontend**
```
# Solution: Make sure backend is running on http://localhost:5000
# Check REACT_APP_API_URL in frontend .env
# Restart both servers if needed
```

### Frontend Issues

**Issue: "npm command not found"**
```bash
# Install Node.js from https://nodejs.org/
# Or via Homebrew:
brew install node
```

**Issue: "Port 3000 is already in use"**
```bash
# macOS/Linux:
lsof -i :3000
kill -9 <PID>

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Issue: "Blank white screen / cannot see content"**
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm start
```

**Issue: "Images not uploading"**
```
1. Check browser console (F12) for errors
2. Verify backend is running
3. Check uploads directory exists: backend/uploads/
4. Check file size is under 10MB
5. Try different image formats (JPG, PNG, WebP)
```

### Database/Data Issues

**Issue: "No medicines found" or "OCR not working"**
```bash
# Verify database files exist:
ls -la database/medicines.json
ls -la database/skin_diseases.json

# Check file format (valid JSON):
python -m json.tool database/medicines.json

# If files are missing, they'll be recreated on first scan
```

**Issue: "Scans not saving to history"**
```
1. Make sure you're logged in (JWT token valid)
2. Check browser console for auth errors
3. Restart backend server
4. Clear browser cache/cookies
```

---

## Project Structure

```
firstaid-platform/
│
├── backend/                          # Flask Backend Server
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── routes/
│   │   │   ├── auth_routes.py       # Authentication endpoints
│   │   │   ├── pharmacy_routes.py   # Medicine scanning endpoints
│   │   │   └── dermatology_routes.py # Skin analysis endpoints
│   │   └── services/
│   │       ├── ocr_service.py       # Tesseract OCR wrapper
│   │       ├── nlp_service.py       # Medicine name matching
│   │       └── skin_analysis_service.py # CV-based skin analysis
│   ├── uploads/                      # Temporary image storage
│   ├── requirements.txt              # Python dependencies
│   ├── run.py                        # Entry point
│   ├── .env.example                  # Environment template
│   └── .env                          # Configuration (create from .example)
│
├── frontend/                         # React Frontend App
│   ├── public/
│   │   └── index.html               # HTML entry point
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/                # Auth-related components
│   │   │   └── common/              # Reusable components
│   │   ├── pages/
│   │   │   ├── HomePage.jsx         # Landing page
│   │   │   ├── PharmacyPage.jsx     # Medicine scanner
│   │   │   ├── DermatologyPage.jsx  # Skin analyzer
│   │   │   └── ProfilePage.jsx      # User profile
│   │   ├── services/
│   │   │   ├── api.js               # Axios instance
│   │   │   ├── pharmacyService.js   # API calls for pharmacy
│   │   │   └── dermatologyService.js # API calls for dermatology
│   │   ├── styles/
│   │   │   ├── global.css           # Global styles
│   │   │   ├── pharmacy.css         # Pharmacy module styles
│   │   │   └── dermatology.css      # Dermatology module styles
│   │   ├── App.jsx                  # Main app component
│   │   └── index.js                 # React entry point
│   ├── package.json                 # Dependencies
│   ├── .env.example                 # Environment template
│   └── .env                         # Configuration
│
├── database/
│   ├── medicines.json               # 10,000+ medicines database
│   └── skin_diseases.json           # 50+ skin diseases database
│
├── README.md                        # Project overview
└── INSTALLATION.md                  # This file

```

---

## Key Features by Module

### 💊 Pharmacy Module
- ✅ OCR-based medicine recognition
- ✅ NLP-powered medicine matching
- ✅ Comprehensive medicine information
- ✅ Drug interaction warnings
- ✅ Dosage recommendations
- ✅ Side effects database
- ✅ Scan history tracking

### 🔬 Dermatology Module
- ✅ Skin condition detection
- ✅ Computer vision analysis
- ✅ Disease severity assessment
- ✅ Cause and symptom analysis
- ✅ Treatment recommendations
- ✅ Lifestyle tips
- ✅ Analysis history

### 🔐 Security Features
- ✅ JWT authentication
- ✅ User registration/login
- ✅ Encrypted data transmission
- ✅ Secure file uploads
- ✅ Private health records

---

## API Documentation

### Authentication Endpoints

**Register User**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}

Response: { token, user }
```

**Login User**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Response: { token, user }
```

### Pharmacy Endpoints

**Scan Medicine**
```bash
POST /api/pharmacy/scan
Content-Type: multipart/form-data
Authorization: Bearer <token>

FormData:
- image: <File>

Response: {
  medicine: { name, generic_name, composition, dosage, ... },
  confidence: 0.95,
  extracted_text: "..."
}
```

**Get Medicine History**
```bash
GET /api/pharmacy/history?page=1&limit=10
Authorization: Bearer <token>

Response: { history: [...], total: 45 }
```

### Dermatology Endpoints

**Analyze Skin**
```bash
POST /api/dermatology/analyze
Content-Type: multipart/form-data
Authorization: Bearer <token>

FormData:
- image: <File>
- body_part: "face"
- symptoms: ["itching", "redness"]

Response: {
  disease: { name, causes, treatments, ... },
  severity: "moderate",
  confidence: 0.92
}
```

**Get Skin History**
```bash
GET /api/dermatology/history?page=1&limit=10
Authorization: Bearer <token>

Response: { history: [...], total: 23 }
```

---

## Performance Tips

1. **Image Optimization**: Use clear, well-lit photos for best OCR/CV results
2. **Browser Cache**: Clear cache if experiencing issues
3. **Database**: Pre-load medicines.json for faster searches
4. **Image Size**: Keep uploaded images under 10MB
5. **API Response**: Typical scan takes 2-5 seconds

---

## Future Enhancements

- [ ] Real database (PostgreSQL/MongoDB)
- [ ] Advanced ML models for better accuracy
- [ ] Mobile apps (React Native)
- [ ] Real-time notifications
- [ ] Doctor consultation integration
- [ ] Prescription verification
- [ ] Video consultation
- [ ] Multi-language support
- [ ] Offline mode
- [ ] Payment integration

---

## Support & Contributions

For issues, questions, or contributions:
1. Check README.md for detailed documentation
2. Review troubleshooting section above
3. Check console logs (browser F12, terminal)
4. Create an issue with detailed description

---

## License

FirstAid Platform © 2024. All rights reserved.

**Disclaimer**: This platform is for informational purposes only. Always consult a qualified healthcare professional for medical advice.

---

**Happy coding! 🚀**
