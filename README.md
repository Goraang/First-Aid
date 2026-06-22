# FirstAid Platform - AI-Powered Pharmacy & Dermatology

A comprehensive web-based healthcare intelligence platform combining **Pharmacy Medicine Identification** and **Dermatology Skin Analysis** powered by AI, OCR, and Computer Vision.

## 🎯 Features

### 💊 Pharmacy Module
- **Medicine Recognition**: Upload photos of medicine strips/packaging
- **OCR Text Extraction**: Automatic text reading from medicine images
- **NLP Analysis**: Intelligent medicine matching using natural language processing
- **Comprehensive Database**: 10,000+ medicines with complete pharmaceutical information
- **Interaction Checking**: Drug-to-drug interaction warnings
- **Dosage Guidance**: Accurate dosage recommendations
- **Scan History**: Track all previous medicine scans

### 🔬 Dermatology Module
- **Skin Condition Detection**: Analyze images of skin conditions
- **Disease Identification**: 50+ skin diseases in database
- **Computer Vision Analysis**: Advanced image processing for pattern recognition
- **Treatment Recommendations**: Evidence-based treatment suggestions
- **Cause Analysis**: Understanding disease etiology
- **Severity Assessment**: Determine condition severity levels
- **Body Part Mapping**: Track affected body areas

### 🔐 Security & Authentication
- JWT-based authentication
- Secure user accounts
- Private health data
- Encrypted communication

## 📋 Tech Stack

### Frontend
- **React 18.2** - Modern UI framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **React Toastify** - Notifications
- **React Dropzone** - File uploads
- **CSS Grid/Flexbox** - Responsive layout

### Backend
- **Flask 3.0** - Python web framework
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - Cross-origin requests
- **Pytesseract** - OCR engine
- **OpenCV** - Image processing
- **TensorFlow** - ML capabilities
- **Pillow** - Image manipulation
- **NumPy/SciPy** - Data processing

### Database
- **JSON Files** - Medicines & Skin Diseases
- **In-Memory Storage** - User sessions & history

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 14+
- macOS, Linux, or Windows
- Tesseract OCR (for macOS: `brew install tesseract`)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   ```bash
   # macOS
   brew install tesseract

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr

   # Windows - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. **Create .env file**
   ```bash
   cat > .env << EOF
   FLASK_ENV=development
   FLASK_PORT=5000
   JWT_SECRET_KEY=your-super-secret-key-change-in-production
   EOF
   ```

6. **Run backend**
   ```bash
   python run.py
   ```

   Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create .env file**
   ```bash
   cat > .env << EOF
   REACT_APP_API_URL=http://localhost:5000/api
   EOF
   ```

4. **Start development server**
   ```bash
   npm start
   ```

   Frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
firstaid-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── routes/
│   │   │   ├── auth_routes.py       # Authentication
│   │   │   ├── pharmacy_routes.py   # Pharmacy APIs
│   │   │   └── dermatology_routes.py # Dermatology APIs
│   │   └── services/
│   │       ├── ocr_service.py       # OCR processing
│   │       ├── nlp_service.py       # NLP matching
│   │       └── skin_analysis_service.py # Skin analysis
│   ├── uploads/                     # Temporary file storage
│   ├── database/
│   │   ├── medicines.json           # 10+ medicines
│   │   └── skin_diseases.json       # 50+ skin conditions
│   ├── requirements.txt
│   └── run.py                       # Entry point
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/               # Auth components
│   │   │   ├── pharmacy/           # Pharmacy UI
│   │   │   ├── dermatology/        # Dermatology UI
│   │   │   └── common/             # Shared components
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── PharmacyPage.jsx
│   │   │   ├── DermatologyPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   ├── services/
│   │   │   ├── api.js              # API client
│   │   │   ├── pharmacyService.js
│   │   │   └── dermatologyService.js
│   │   ├── styles/
│   │   │   ├── global.css
│   │   │   ├── pharmacy.css
│   │   │   └── dermatology.css
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .gitignore
│
├── database/
│   ├── medicines.json               # Global medicines DB
│   └── skin_diseases.json           # Global diseases DB
│
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Pharmacy
- `POST /api/pharmacy/scan` - Scan medicine (multipart/form-data)
- `GET /api/pharmacy/history` - Get scan history
- `GET /api/pharmacy/search?q=query` - Search medicines
- `GET /api/pharmacy/medicine/:id` - Get medicine details
- `GET /api/pharmacy/stats` - Get user statistics
- `DELETE /api/pharmacy/history/:scanId` - Delete scan

### Dermatology
- `POST /api/dermatology/analyze` - Analyze skin condition
- `GET /api/dermatology/history` - Get analysis history
- `GET /api/dermatology/conditions` - Get all diseases
- `GET /api/dermatology/disease/:id` - Get disease details
- `GET /api/dermatology/stats` - Get user statistics
- `DELETE /api/dermatology/history/:scanId` - Delete scan

## 🎨 UI/UX Features

### Pharmacy Theme
- **Color Scheme**: Medical Blue & Teal
- **Aesthetic**: Modern, professional healthcare
- **Animations**: Smooth transitions & loading states
- **Layout**: Responsive grid system

### Dermatology Theme
- **Color Scheme**: Warm Rose & Peach
- **Aesthetic**: Dermatology-specific design
- **Animations**: Elegant transitions
- **Layout**: Skin-focused UI elements

### Shared Features
- **Responsive Design**: Works on desktop, tablet, mobile
- **Accessibility**: WCAG 2.1 compliant
- **Performance**: Optimized images & lazy loading
- **UX**: Intuitive navigation & clear CTAs

## 🧪 Testing

### Test Pharmacy Scanner
1. Take a photo of any medicine strip
2. Upload via the pharmacy module
3. View extracted text and identified medicine
4. See complete pharmaceutical information

### Test Dermatology Analyzer
1. Take a photo of a skin condition
2. Upload via the dermatology module
3. View analysis results
4. See recommended treatments

## 📊 Database Structure

### Medicines.json
```json
{
  "id": "med_001",
  "name": "Paracetamol",
  "generic_name": "Acetaminophen",
  "type": "Analgesic / Antipyretic",
  "composition": "Paracetamol 500mg",
  "usage": "...",
  "dosage": "...",
  "warnings": [...],
  "side_effects": [...],
  "interactions": [...],
  "storage": "..."
}
```

### Skin_diseases.json
```json
{
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
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
FLASK_ENV=development
FLASK_PORT=5000
JWT_SECRET_KEY=your-secret-key
UPLOAD_FOLDER=./uploads
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENV=development
```

## 🚨 Known Limitations & Future Enhancements

### Current Limitations
- Uses mock/in-memory database (no persistent DB)
- Basic machine learning models
- Limited to English text
- Manual disease matching algorithm

### Future Enhancements
- [ ] PostgreSQL database integration
- [ ] Advanced ML/DL models (TensorFlow, PyTorch)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Telemedicine integration
- [ ] Doctor consultation booking
- [ ] Real-time prescription verification
- [ ] AI-powered symptom checking
- [ ] Health record management
- [ ] Insurance integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

**IMPORTANT**: FirstAid Platform is for informational purposes only and should not be considered medical advice. Always consult qualified healthcare professionals for:
- Diagnosis
- Treatment decisions
- Prescription verification
- Medical emergencies

This platform supplements but does not replace professional medical judgment.

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@firstaid-platform.com
- Visit: www.firstaid-platform.com

## 🙏 Acknowledgments

- Tesseract OCR for text extraction
- OpenCV for image processing
- Flask community for robust framework
- React community for amazing UI library

## 🎓 Technology Credits

- **OCR**: Tesseract
- **Image Processing**: OpenCV
- **Backend Framework**: Flask
- **Frontend Framework**: React
- **ML/CV**: TensorFlow, scikit-learn
- **HTTP Client**: Axios

---

**Built with ❤️ for healthcare**

Version: 2.0.0
Last Updated: June 2026
