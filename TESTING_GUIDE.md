# 🧪 FirstAid Platform - Testing Guide

## Testing Overview

This guide provides comprehensive testing procedures for all FirstAid modules.

---

## ✅ Pre-Testing Checklist

Before testing, ensure:
- [ ] Both backend and frontend servers are running
- [ ] Backend: http://localhost:5000 ✅
- [ ] Frontend: http://localhost:3000 ✅
- [ ] Tesseract OCR is installed
- [ ] No errors in browser console (F12)
- [ ] No errors in backend terminal
- [ ] Temporary uploads folder exists

---

## 🔐 Authentication Testing

### Test 1: User Registration

**Procedure:**
1. Go to http://localhost:3000
2. Click "Get Started Free"
3. Fill in form:
   - Name: `Test User 1`
   - Email: `test1@example.com`
   - Password: `Test123!@#`
4. Check "I agree to Terms"
5. Click "Create Account"

**Expected Results:**
- ✅ Account created successfully
- ✅ Redirected to homepage
- ✅ User name appears in navbar
- ✅ JWT token saved in localStorage
- ✅ Success toast notification appears

**Verification:**
- Open DevTools (F12) → Application → LocalStorage
- Should see `firstaid_token` key with JWT value

---

### Test 2: User Login

**Procedure:**
1. Click "Logout" (from previous test)
2. Click "Login" in navbar
3. Enter:
   - Email: `test1@example.com`
   - Password: `Test123!@#`
4. Click "Sign In"

**Expected Results:**
- ✅ Login successful
- ✅ Redirected to homepage
- ✅ User name shows in navbar
- ✅ Welcome message appears
- ✅ Can access Pharmacy and Dermatology modules

---

### Test 3: Invalid Credentials

**Procedure:**
1. Go to login page
2. Enter:
   - Email: `wrong@email.com`
   - Password: `wrongpass123`
3. Click "Sign In"

**Expected Results:**
- ✅ Error toast appears
- ✅ Error message: "Invalid email or password"
- ✅ Not redirected
- ✅ Page remains at login

---

### Test 4: Duplicate Email Registration

**Procedure:**
1. Go to register page
2. Try registering with previously used email
3. Fill:
   - Name: `Another User`
   - Email: `test1@example.com` (same as before)
   - Password: `password123`
4. Click "Create Account"

**Expected Results:**
- ✅ Error message: "Email already registered"
- ✅ Account not created
- ✅ Error toast notification appears

---

## 💊 Pharmacy Module Testing

### Test 5: Medicine Image Upload

**Procedure:**
1. Login with test account
2. Click "💊 Pharmacy" in navbar
3. Click upload area
4. Select a medicine image (JPG/PNG)
5. Verify image preview appears

**Expected Results:**
- ✅ Image preview displays
- ✅ Remove button (✕) appears
- ✅ Image shows correctly scaled
- ✅ No console errors
- ✅ Scan button is enabled

---

### Test 6: Medicine Scanning

**Procedure:**
1. With medicine image uploaded
2. Click "🔍 Scan Medicine" button
3. Wait 2-5 seconds for processing

**Expected Results:**
- ✅ Loading overlay appears
- ✅ Processing steps displayed
- ✅ After processing, medicine details show
- ✅ Results include:
  - Medicine name
  - Generic name
  - Composition
  - Dosage
  - Side effects
  - Warnings
  - Drug interactions
- ✅ Confidence score displayed (0-100%)
- ✅ Success toast notification

**Verification in DevTools:**
- Network tab: POST request to /api/pharmacy/scan
- Response includes medicine object with all fields
- Status: 200 OK

---

### Test 7: Multiple Scans

**Procedure:**
1. Upload a different medicine image
2. Scan it
3. Upload another medicine image
4. Scan it again
5. Repeat 2-3 times

**Expected Results:**
- ✅ Each scan completes successfully
- ✅ Different medicines identified
- ✅ Different confidence scores
- ✅ All scans process without errors
- ✅ No memory leaks in browser

---

### Test 8: Medicine History

**Procedure:**
1. After multiple scans, click "📋 History" tab
2. Verify all scans appear in list
3. Click on a scan in history

**Expected Results:**
- ✅ All past scans displayed
- ✅ Each item shows:
  - Medicine thumbnail
  - Medicine name
  - Confidence score
  - Timestamp
- ✅ Clicking opens scan details
- ✅ History shows newest first
- ✅ Pagination works (if >10 items)

---

### Test 9: Medicine Search

**Procedure:**
1. Go to pharmacy module
2. Look for search functionality
3. Search for "paracetamol"
4. Review results

**Expected Results:**
- ✅ Search returns relevant medicines
- ✅ Results include:
  - Exact matches first
  - Similar matches below
  - Match confidence score
- ✅ Clicking result shows details
- ✅ No console errors

---

### Test 10: Pharmacy Statistics

**Procedure:**
1. View pharmacy dashboard
2. Check statistics cards at top

**Expected Results:**
- ✅ Statistics show:
  - Total scans performed
  - Medicines identified
  - Accuracy rate (%)
  - Medicine database size
- ✅ Numbers update after new scans
- ✅ All cards render correctly

---

### Test 11: Large File Upload

**Procedure:**
1. Try uploading image larger than 10MB
2. Observe error handling

**Expected Results:**
- ✅ Error message: "File size must be less than 10MB"
- ✅ File not uploaded
- ✅ Error toast appears
- ✅ No backend errors

---

### Test 12: Invalid File Type

**Procedure:**
1. Try uploading non-image file (PDF, TXT)
2. Observe handling

**Expected Results:**
- ✅ File rejected by dropzone
- ✅ Error message appears
- ✅ No file is sent to backend
- ✅ User prompted to upload image

---

## 🔬 Dermatology Module Testing

### Test 13: Skin Condition Upload

**Procedure:**
1. Click "🔬 Dermatology" in navbar
2. Click upload area
3. Upload skin condition image
4. Verify preview

**Expected Results:**
- ✅ Image preview displays
- ✅ Body part selector visible
- ✅ Remove button (✕) works
- ✅ Analyze button enabled

---

### Test 14: Body Part Selection

**Procedure:**
1. With skin image uploaded
2. Click different body parts:
   - Face
   - Arm
   - Leg
   - Back
   - etc.

**Expected Results:**
- ✅ Selected body part highlights
- ✅ Selection stored in form
- ✅ Can deselect by clicking again
- ✅ Multiple selections allowed (or single as designed)

---

### Test 15: Skin Analysis

**Procedure:**
1. Upload skin condition image
2. Select body part (optional)
3. Click "🔍 Analyze Skin"
4. Wait 2-4 seconds

**Expected Results:**
- ✅ Loading overlay appears
- ✅ Analysis steps shown
- ✅ After processing, results display:
  - Disease name
  - Scientific name
  - Severity (Mild/Moderate/Severe)
  - Confidence score
  - Causes listed
  - Symptoms listed
  - Treatments listed
  - Lifestyle tips shown
- ✅ Medical disclaimer appears
- ✅ Success notification

**Verification:**
- POST request to /api/dermatology/analyze
- Response includes disease object
- Status: 200 OK

---

### Test 16: Severity Badges

**Procedure:**
1. Analyze multiple skin conditions
2. Observe severity badges

**Expected Results:**
- ✅ Badges display correct severity:
  - Green for Mild
  - Orange for Moderate
  - Red for Severe
- ✅ Badge styling matches theme
- ✅ Severity matches disease data

---

### Test 17: Skin Analysis History

**Procedure:**
1. After multiple analyses, click "📋 History"
2. View all past analyses

**Expected Results:**
- ✅ All analyses display in list
- ✅ Each shows:
  - Disease thumbnail
  - Disease name
  - Severity level
  - Confidence score
  - Timestamp
- ✅ Newest first
- ✅ Clicking shows full results

---

### Test 18: Dermatology Statistics

**Procedure:**
1. View dermatology dashboard
2. Check statistics cards

**Expected Results:**
- ✅ Statistics include:
  - Total analyses
  - Diseases detected
  - Average confidence
  - Severity breakdown
- ✅ Numbers update after new analyses
- ✅ All cards render correctly

---

## 📱 Responsive Design Testing

### Test 19: Desktop View (1920x1080)

**Procedure:**
1. Use full desktop screen
2. Test all features
3. Check layout

**Expected Results:**
- ✅ All content visible
- ✅ Proper spacing
- ✅ Navbar and sidebar aligned
- ✅ Cards well-arranged
- ✅ No horizontal scrolling

---

### Test 20: Tablet View (768x1024)

**Procedure:**
1. Open DevTools (F12)
2. Toggle device toolbar
3. Select iPad/tablet size
4. Test functionality

**Expected Results:**
- ✅ Layout adapts properly
- ✅ Touch interactions work
- ✅ Text readable
- ✅ Images scale appropriately
- ✅ No overflow issues

---

### Test 21: Mobile View (375x812)

**Procedure:**
1. DevTools → Mobile device
2. Select iPhone size
3. Test all features

**Expected Results:**
- ✅ Mobile-optimized layout
- ✅ Hamburger menu works (if applicable)
- ✅ Touch targets appropriately sized
- ✅ No text cutoff
- ✅ Scrolling smooth
- ✅ Images load quickly

---

## ⚠️ Error Handling Testing

### Test 22: Network Error Simulation

**Procedure:**
1. Stop backend server
2. Try to upload image in pharmacy/dermatology
3. Observe error handling

**Expected Results:**
- ✅ Error message displays
- ✅ User informed of issue
- ✅ "Retry" option available
- ✅ No crash or blank page
- ✅ Frontend remains responsive

---

### Test 23: Timeout Handling

**Procedure:**
1. Simulate slow network (DevTools throttling)
2. Upload and scan image
3. Wait for timeout

**Expected Results:**
- ✅ Loading state displayed
- ✅ User sees processing status
- ✅ If timeout: error message
- ✅ Retry available
- ✅ Clear feedback

---

### Test 24: Invalid Session Token

**Procedure:**
1. Open DevTools → Application → LocalStorage
2. Modify JWT token (add random characters)
3. Try to access protected page
4. Observe handling

**Expected Results:**
- ✅ Redirected to login
- ✅ Error message: "Unauthorized"
- ✅ Token cleared
- ✅ Must re-login

---

## 🔄 Cross-Browser Testing

### Test 25: Chrome

**Procedure:**
1. Open in Chrome
2. Test all functionality
3. Check DevTools console

**Expected Results:**
- ✅ All features work
- ✅ No console errors
- ✅ Styling correct
- ✅ Animations smooth

---

### Test 26: Firefox

**Procedure:**
1. Open in Firefox
2. Repeat Test 25 steps

**Expected Results:**
- ✅ All features work
- ✅ No console errors
- ✅ Styling consistent
- ✅ Performance similar

---

### Test 27: Safari

**Procedure:**
1. Open in Safari
2. Repeat Test 25 steps

**Expected Results:**
- ✅ All features work
- ✅ CSS compatible
- ✅ No JavaScript issues
- ✅ Image handling correct

---

## 📊 Performance Testing

### Test 28: Page Load Time

**Procedure:**
1. DevTools → Network tab
2. Reload page (Ctrl+R)
3. Check load times

**Expected Results:**
- ✅ First contentful paint: <2s
- ✅ Page fully loaded: <3s
- ✅ Total size: <5MB
- ✅ Minimal third-party scripts

---

### Test 29: Image Processing Speed

**Procedure:**
1. Upload medicine image
2. Click scan
3. Time until results appear

**Expected Results:**
- ✅ OCR processing: 2-5 seconds
- ✅ UI responsive during processing
- ✅ Loading animation smooth
- ✅ No browser freezing

---

### Test 30: Memory Usage

**Procedure:**
1. DevTools → Performance tab
2. Record while scanning multiple images
3. Check memory usage

**Expected Results:**
- ✅ Memory stays stable
- ✅ No memory leaks
- ✅ Garbage collection working
- ✅ <200MB total usage

---

## 🔒 Security Testing

### Test 31: Session Persistence

**Procedure:**
1. Login successfully
2. Close browser
3. Reopen same URL

**Expected Results:**
- ✅ Logged in session restored
- ✅ User info appears
- ✅ Can access protected pages
- ✅ Token still valid

---

### Test 32: CORS Headers

**Procedure:**
1. DevTools → Network tab
2. Make any API call
3. Check response headers

**Expected Results:**
- ✅ CORS headers present
- ✅ Access-Control-Allow-Origin set
- ✅ No CORS errors
- ✅ Requests succeed

---

### Test 33: File Upload Security

**Procedure:**
1. Check uploaded files
2. Verify files stored securely
3. Check permissions

**Expected Results:**
- ✅ Files stored in uploads folder
- ✅ Only authorized users can access
- ✅ File names sanitized
- ✅ No execution of uploaded files

---

## 📋 Checklist Summary

### Frontend Features
- [ ] Authentication (Register/Login)
- [ ] Protected routes
- [ ] Pharmacy module fully functional
- [ ] Dermatology module fully functional
- [ ] User profile and history
- [ ] Navigation between modules
- [ ] Image uploads
- [ ] Result displays
- [ ] Error handling
- [ ] Toast notifications

### Backend Features
- [ ] User registration endpoint
- [ ] User login endpoint
- [ ] JWT authentication
- [ ] Medicine scanning endpoint
- [ ] Skin analysis endpoint
- [ ] History retrieval
- [ ] Error responses
- [ ] File handling
- [ ] OCR processing
- [ ] Image validation

### Database
- [ ] Medicines database loaded
- [ ] Skin diseases database loaded
- [ ] Data accessible
- [ ] Search working
- [ ] No corrupted entries

### Performance
- [ ] Page load time acceptable
- [ ] Image processing fast
- [ ] No memory leaks
- [ ] Smooth animations
- [ ] Responsive design

### Security
- [ ] JWT tokens working
- [ ] CORS configured
- [ ] File uploads validated
- [ ] Passwords secure
- [ ] Session handling

---

## 🆘 Test Failure Resolution

### If tests fail:

1. **Check console logs**
   - Browser F12 → Console
   - Backend terminal output

2. **Verify setup**
   - Both servers running?
   - Correct ports?
   - .env files configured?

3. **Review data**
   - Medicines.json exists?
   - Skin_diseases.json valid?
   - Upload folder writable?

4. **Check dependencies**
   - All npm packages installed?
   - All pip packages installed?
   - Tesseract installed?

5. **Restart and retry**
   - Stop both servers
   - Wait 5 seconds
   - Start backend, then frontend
   - Retry test

---

## 📈 Test Results

Record test results here:

| Test # | Name | Status | Notes |
|--------|------|--------|-------|
| 1 | Registration | PASS/FAIL | |
| 2 | Login | PASS/FAIL | |
| 3 | Invalid Creds | PASS/FAIL | |
| ... | ... | ... | |

---

## ✅ Final Verification

All tests passed? You're ready to:
- ✅ Deploy to production
- ✅ Share with users
- ✅ Collect feedback
- ✅ Plan Phase 2 features

---

**Happy Testing! 🧪**
