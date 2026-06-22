# FirstAid Platform - Complete Setup Guide

## 📚 Quick Start (5 Minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "FLASK_ENV=development
FLASK_PORT=5000
JWT_SECRET_KEY=firstaid-dev-key-2026" > .env

# Run backend
python run.py
```

✅ Backend running on: `http://localhost:5000`

### 2. Frontend Setup

```bash
# In new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Start frontend
npm start
```

✅ Frontend running on: `http://localhost:3000`

### 3. Access Platform

Open your browser and visit: **http://localhost:3000**

## 🔧 Troubleshooting

### Tesseract Not Found Error

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Port Already in Use

**Kill existing process:**
```bash
# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CORS Issues

Ensure backend CORS is enabled in `app/__init__.py`:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### OCR Not Extracting Text

1. Ensure image is clear and well-lit
2. Try different file formats (JPG, PNG)
3. Check Tesseract installation: `tesseract --version`

## 📝 File Guide

### Key Files You'll Use

**Backend Core Files:**
- `backend/run.py` - Start backend server
- `backend/app/__init__.py` - Flask app configuration
- `backend/app/routes/*.py` - API endpoints
- `backend/app/services/*.py` - Business logic
- `backend/database/*.json` - Data files

**Frontend Core Files:**
- `frontend/src/App.jsx` - Main React component
- `frontend/src/pages/*.jsx` - Page components
- `frontend/src/services/*.js` - API calls
- `frontend/src/styles/*.css` - Styling
- `frontend/package.json` - Dependencies

## 🧪 Testing the Application

### Test Pharmacy Module

1. Go to **Pharmacy** section
2. Click "Upload Medicine Image"
3. Upload a medicine packet photo
4. Click "Scan Medicine"
5. View results with:
   - Medicine name
   - Composition & dosage
   - Warnings & interactions
   - Side effects

### Test Dermatology Module

1. Go to **Dermatology** section
2. Click "Upload Skin Image"
3. Upload a skin condition photo
4. Select affected body part (optional)
5. Click "Analyze"
6. View results with:
   - Disease name
   - Causes & symptoms
   - Treatment recommendations
   - Prevention tips

## 🔑 Test Credentials

Create account on registration page:
- **Email**: test@example.com
- **Password**: test123456
- **Name**: Test User

## 📦 Project Dependencies

### Backend
- Flask 3.0.0
- pytesseract 0.3.10
- opencv-python 4.8.0.76
- pillow 10.0.0
- tensorflow 2.14.0
- numpy 1.24.3

### Frontend
- react 18.2.0
- react-router-dom 6.20.0
- axios 1.6.0
- react-dropzone 14.2.3
- react-toastify 9.1.3

## 🎯 API Testing with Curl

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"test123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"test123"}'
```

### Scan Medicine
```bash
curl -X POST http://localhost:5000/api/pharmacy/scan \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@medicine.jpg"
```

### Analyze Skin
```bash
curl -X POST http://localhost:5000/api/dermatology/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@skin.jpg" \
  -F "body_part=face"
```

## 🎨 Customization

### Change Brand Colors

**Edit `frontend/src/styles/global.css`:**
```css
:root {
  --pharma-primary: #0ea5e9;        /* Pharmacy blue */
  --derm-primary: #f43f5e;          /* Dermatology rose */
  /* ... more colors */
}
```

### Add More Medicines

**Edit `database/medicines.json`:**
```json
{
  "id": "med_011",
  "name": "Your Medicine",
  "generic_name": "Generic Name",
  "type": "Medicine Type",
  "composition": "Composition",
  "usage": "Usage description",
  "dosage": "Dosage information",
  "warnings": [...],
  "side_effects": [...],
  "interactions": [...],
  "storage": "Storage info"
}
```

### Add More Diseases

**Edit `database/skin_diseases.json`:**
```json
{
  "id": "disease_011",
  "name": "Disease Name",
  "scientific_name": "Scientific Name",
  "description": "Description",
  "causes": [...],
  "symptoms": [...],
  "treatments": [...],
  "prevention": [...],
  "severity": "mild/moderate/severe",
  "affected_areas": [...]
}
```

## 🚀 Deployment

### Deploy Backend (Heroku/Railway)

1. Create Procfile:
```
web: gunicorn run:app
```

2. Deploy:
```bash
git push heroku main
```

### Deploy Frontend (Vercel/Netlify)

1. Build:
```bash
npm run build
```

2. Deploy build folder to Vercel/Netlify

## 📊 Database Schema

### Medicines Table
| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| name | string | Medicine name |
| generic_name | string | Generic name |
| type | string | Medicine type |
| composition | string | Active composition |
| dosage | string | Recommended dosage |
| warnings | array | Important warnings |
| side_effects | array | Possible side effects |
| interactions | array | Drug interactions |

### Skin Diseases Table
| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| name | string | Disease name |
| scientific_name | string | Scientific classification |
| causes | array | Disease causes |
| symptoms | array | Disease symptoms |
| treatments | array | Treatment options |
| prevention | array | Prevention methods |
| severity | string | Severity level |
| affected_areas | array | Body areas affected |

## 🔒 Security Best Practices

1. **Change JWT Secret:**
   ```env
   JWT_SECRET_KEY=your-very-long-random-secret-key
   ```

2. **Use HTTPS in Production:**
   - Configure SSL certificates
   - Update API_URL to https://

3. **Rate Limiting:**
   - Implement rate limiting middleware
   - Prevent API abuse

4. **Input Validation:**
   - Validate all file uploads
   - Check file size & type
   - Sanitize user input

## 📈 Performance Optimization

1. **Image Optimization:**
   - Compress images before upload
   - Use appropriate formats (WEBP, JPG)
   - Lazy load images

2. **Caching:**
   - Cache medicine & disease data
   - Use browser caching for assets

3. **Database:**
   - Index frequently searched fields
   - Implement pagination
   - Use connection pooling

## 🐛 Debugging

### Enable Debug Logging

**Backend:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
- Open DevTools (F12)
- Check Console tab for errors
- Use Network tab to inspect API calls

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| OCR not working | Install tesseract |
| Image not uploading | Check file size & format |
| Slow response | Check image quality, optimize |
| API not responding | Verify backend is running |
| Login fails | Check credentials in database |

## 📞 Support

- Check README.md for details
- Review error messages in console
- Check backend logs: `tail -f backend/run.py output`
- Debug network requests in DevTools

## 🎉 You're Ready!

Your FirstAid Platform is now ready to use. Start by:
1. Creating an account
2. Testing pharmacy scanner
3. Testing dermatology analyzer
4. Exploring features

**Happy healthcare! 🏥**

---

**Need Help?**
- Review API docs in README.md
- Check individual component files
- Enable debug logging
- Test with curl commands

**Version**: 2.0.0
**Last Updated**: June 2026
