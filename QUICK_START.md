# ⚡ FirstAid Platform - Quick Start (5 Minutes)

## Prerequisites Check
Before starting, verify you have:
- Python 3.9+: `python3 --version`
- Node.js 16+: `node --version`
- npm 8+: `npm --version`
- Tesseract: `tesseract --version`

If any are missing, see INSTALLATION.md for setup instructions.

---

## 🚀 Start Backend (Terminal 1)

```bash
# Navigate to backend
cd /Users/goraangnayyar/firstaid-platform/backend

# Activate virtual environment
source venv/bin/activate

# Start backend server
python run.py
```

**Wait for this message:**
```
* Running on http://0.0.0.0:5000
* WARNING: This is a development server. Do not use it in production.
```

✅ **Backend is ready!** Don't close this terminal.

---

## 🎨 Start Frontend (Terminal 2)

```bash
# Open a NEW terminal window/tab
cd /Users/goraangnayyar/firstaid-platform/frontend

# Start frontend server
npm start
```

**Your browser should open automatically to:**
```
http://localhost:3000
```

✅ **Frontend is ready!** You should see the FirstAid homepage.

---

## 🧪 Test Everything (5 minutes)

### Step 1: Create Account (30 seconds)
1. Click **"Get Started Free"** button
2. Fill in the form:
   - Name: `Test User`
   - Email: `test@example.com`
   - Password: `TestPassword123`
3. Check "I agree to Terms"
4. Click **"Create Account"**
5. ✅ You're logged in!

### Step 2: Test Pharmacy Module (2 minutes)
1. Click **"💊 Pharmacy"** in the navbar
2. Click the upload area or drag-drop an image of:
   - Any medicine package/strip
   - Or use a sample image
3. Click **"🔍 Scan Medicine"**
4. Wait 2-3 seconds for OCR processing
5. View the medicine details:
   - ✅ Name and generic name
   - ✅ Composition
   - ✅ Dosage
   - ✅ Warnings
   - ✅ Drug interactions

### Step 3: Test Dermatology Module (2 minutes)
1. Click **"🔬 Dermatology"** in the navbar
2. Upload an image of a skin condition
3. (Optional) Select affected body part
4. Click **"🔍 Analyze Skin"**
5. Wait 2-3 seconds for analysis
6. View results:
   - ✅ Disease name
   - ✅ Severity level
   - ✅ Causes
   - ✅ Treatment recommendations
   - ✅ Lifestyle tips

### Step 4: Check Profile (30 seconds)
1. Click **"Profile"** in navbar
2. View your scan history
3. See statistics (total scans, etc.)

---

## 📊 Test API Directly (Optional)

### Health Check
```bash
curl http://localhost:5000/api/health
```
Expected: `{"status":"ok","message":"FirstAid API is running"}`

### Test User Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name":"John Doe",
    "email":"john@example.com",
    "password":"password123"
  }'
```

### Test User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"john@example.com",
    "password":"password123"
  }'
```

---

## 🛑 Stop Servers

### Stop Backend (Terminal 1)
```bash
# Press Ctrl+C
```

### Stop Frontend (Terminal 2)
```bash
# Press Ctrl+C
```

---

## 📱 Common Issues (Quick Fixes)

### "Cannot find module 'react-dropzone'"
```bash
cd frontend
npm install
npm start
```

### "Port 3000 already in use"
```bash
# macOS/Linux:
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Backend returns 'module not found' error"
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

### "Cannot read image file"
- Make sure image is under 10MB
- Try JPG or PNG format
- Ensure image is clear and not corrupted

### "OCR not working / blank results"
- Tesseract not installed: `brew install tesseract`
- Check backend console for errors
- Image might be too small or low quality

---

## 📂 File Locations

| What | Where |
|------|-------|
| Backend | `/Users/goraangnayyar/firstaid-platform/backend/` |
| Frontend | `/Users/goraangnayyar/firstaid-platform/frontend/` |
| Medicines DB | `/Users/goraangnayyar/firstaid-platform/database/medicines.json` |
| Skin Diseases DB | `/Users/goraangnayyar/firstaid-platform/database/skin_diseases.json` |
| Uploaded Images | `/Users/goraangnayyar/firstaid-platform/backend/uploads/` |

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (3000)                    │
│  ┌────────────────┬──────────────┬──────────────────┐    │
│  │  Home          │ Pharmacy     │  Dermatology     │    │
│  │  Login/Signup  │  Scanner     │  Skin Analyzer   │    │
│  │  Profile       │  History     │  History         │    │
│  └────────────────┴──────────────┴──────────────────┘    │
└────────────────────────────┬────────────────────────────┘
                             │ Axios API Calls
                             ↓
┌─────────────────────────────────────────────────────────┐
│              Flask Backend API (5000)                     │
│  ┌──────────────┬──────────────┬──────────────────┐      │
│  │ Auth Routes  │ Pharmacy     │ Dermatology      │      │
│  │ JWT Token    │ Routes       │ Routes           │      │
│  │ User Mgmt    │              │                  │      │
│  └──────────────┴──────────────┴──────────────────┘      │
│                                                           │
│  ┌──────────────┬──────────────┬──────────────────┐      │
│  │ OCR Service  │ NLP Service  │ CV Service       │      │
│  │ Tesseract    │ Text Matching│ Image Analysis   │      │
│  └──────────────┴──────────────┴──────────────────┘      │
└────────────────────────────┬────────────────────────────┘
                             │ File I/O
                             ↓
            ┌────────────────────────────────┐
            │  JSON Databases                │
            │  ├─ medicines.json             │
            │  └─ skin_diseases.json         │
            │                                │
            │  Upload Directory              │
            │  └─ Temporary Images           │
            └────────────────────────────────┘
```

---

## 📚 Full Documentation

For detailed information, see:
- **INSTALLATION.md** - Complete setup guide
- **README.md** - Project overview and features
- **SETUP_GUIDE.md** - Comprehensive configuration

---

## ✅ Verification Checklist

After starting both servers:
- [ ] Browser opens to http://localhost:3000
- [ ] Homepage loads without errors
- [ ] Can see "Get Started" button
- [ ] Can navigate to Pharmacy and Dermatology
- [ ] Terminal shows Flask running on :5000
- [ ] No "CORS" errors in browser console (F12)
- [ ] Backend responds to health check

---

## 🎓 Next Steps

1. **Create Test Account** - Sign up with test email
2. **Try Pharmacy Scan** - Upload medicine image
3. **Try Skin Analysis** - Upload skin condition image
4. **Check Profile** - View your scan history
5. **Review Database** - Check medicines.json and skin_diseases.json
6. **Explore Code** - Check services and components

---

## 🆘 Still Having Issues?

1. **Check Console Logs**
   - Browser: Press F12 → Console tab
   - Backend: Check terminal output

2. **Verify Environment**
   - Backend .env file exists and configured
   - Frontend .env file exists
   - Both files have correct URLs

3. **Restart Everything**
   - Stop both servers (Ctrl+C)
   - Wait 5 seconds
   - Start backend first, then frontend

4. **Check Ports**
   - Backend: http://localhost:5000/api/health
   - Frontend: http://localhost:3000

5. **See INSTALLATION.md** - Full troubleshooting guide

---

## 🎉 Success!

You should now see:
- ✅ FirstAid homepage with welcome banner
- ✅ Pharmacy and Dermatology modules
- ✅ Login/Register functionality
- ✅ Image upload capabilities
- ✅ Real-time scanning and analysis

**Enjoy using FirstAid! 🚀**
