# 🧪 Step-by-Step Testing Guide

## Prerequisites
- ✅ Both frontend and backend code fixed
- ✅ `.env` file created in frontend
- ✅ Node.js and Python 3 installed
- ✅ Two terminal windows ready

---

## Step 1: Start Backend Server

**Terminal 1:**
```bash
cd /Users/goraangnayyar/firstaid-platform/backend
source venv/bin/activate
python run.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
 * WARNING: This is a development server. Do not use it in production.
```

✅ **Backend is ready!** Leave this terminal running.

---

## Step 2: Start Frontend Server

**Terminal 2:**
```bash
cd /Users/goraangnayyar/firstaid-platform/frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view firstaid in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.x.x.x:3000
```

✅ **Frontend is ready!** Browser should open automatically.

---

## Step 3: Test Registration (New User)

**Goal**: Register a brand new account and verify auto-login works

### 3.1 Navigate to Registration
1. Click **"Get Started Free"** button on homepage
   - OR go directly to: `http://localhost:3000/register`

### 3.2 Fill Registration Form
```
Full Name:        John Doe
Email:            john@example.com
Password:         John123456
Confirm Password: John123456
```

### 3.3 Submit Registration
1. Click **"Register"** button
2. **Wait 2-3 seconds** for processing

### 3.4 Verify Success
✅ **You should see:**
- Page redirects to home page
- "Welcome to FirstAid Platform" message displays
- Navigation bar shows your email (not login link)
- Can click "💊 Pharmacy" button
- Can click "🔬 Dermatology" button

❌ **If you see:**
- "Invalid email" → Email already registered, use different email
- Network error → Backend not running, check Terminal 1
- Blank page → Frontend error, check browser console (F12)

---

## Step 4: Test Login with Existing Account

**Goal**: Verify login works with a registered account

### 4.1 Logout Current Session
1. Click your email/profile in navbar
2. Click **"Logout"** button

### 4.2 Navigate to Login
1. Click **"Login"** link on page
   - OR go directly to: `http://localhost:3000/login`

### 4.3 Enter Credentials
```
Email:    test@example.com
Password: TestPassword123
```

### 4.4 Submit Login
1. Click **"Login"** button
2. **Wait 2-3 seconds** for processing

### 4.5 Verify Success
✅ **You should see:**
- Redirects to home page
- Email shows in navbar (authenticated)
- Can access pharmacy/dermatology

---

## Step 5: Test Pharmacy Module (Protected Route)

**Goal**: Verify protected routes work after login

### 5.1 Navigate to Pharmacy
1. Click **"💊 Browse Medicines"** button
   - OR click **"💊 Pharmacy"** in navbar

### 5.2 Verify Access
✅ **Should see:**
- Pharmacy page loads with upload area
- Can see: "Upload medicine image", "Search medicine"

❌ **If redirected to login:**
- Token not saved properly
- Check browser storage (F12 → Application → localStorage)
- Try clearing localStorage and logging in again

### 5.3 Try Upload (Optional)
1. Click upload area
2. Select any image file
3. Click "🔍 Scan Medicine"
4. **Wait 3-5 seconds** for OCR processing

✅ **Should display:**
- Medicine details (name, composition, dosage, etc.)

---

## Step 6: Test Dermatology Module (Protected Route)

**Goal**: Verify another protected route works

### 6.1 Navigate to Dermatology
1. Click **"🔬 Start Analysis"** button
   - OR click **"🔬 Dermatology"** in navbar

### 6.2 Verify Access
✅ **Should see:**
- Dermatology page loads with upload area
- Can see: "Upload skin image", "Select affected area"

---

## Step 7: Test User Profile

**Goal**: Verify profile page shows user data and scan history

### 7.1 Navigate to Profile
1. Click **"👤 View Profile"** button
   - OR click profile icon in navbar

### 7.2 Verify Content
✅ **Should display:**
- Your name
- Your email
- Scan history (currently empty if first login)
- Statistics

---

## 🔍 Browser Console Debugging

If anything goes wrong, check browser console:

**Open DevTools:**
1. Press `F12` or right-click → "Inspect"
2. Click **"Console"** tab

**Common messages to check:**
```javascript
// Good:
Login error: Error: ... // Shows specific error
Response: {token: "...", user: {...}}

// Bad:
Cannot POST /api/auth/login
CORS error: Access-Control-Allow-Origin
```

---

## 🔍 Network Tab Debugging

To see actual API requests:

**Open DevTools:**
1. Press `F12`
2. Click **"Network"** tab
3. Perform login/register action
4. Look for requests to `localhost:5000`

**Check each request:**
- **URL**: Should be `http://localhost:5000/api/auth/login` ✅
- **Status**: Should be 200 ✅
- **Response**: Should have `token` field ✅

---

## 📊 Test Results Summary

Create a simple table to track your testing:

| Test | Status | Notes |
|------|--------|-------|
| Backend Running | ✅/❌ | Port 5000 |
| Frontend Running | ✅/❌ | Port 3000 |
| Register New User | ✅/❌ | Auto-login? |
| Login Existing User | ✅/❌ | Token saved? |
| Access Pharmacy | ✅/❌ | Protected route? |
| Access Dermatology | ✅/❌ | Protected route? |
| View Profile | ✅/❌ | User data? |
| Logout | ✅/❌ | Redirects to home? |

---

## 🆘 Troubleshooting

### Issue: "Network request failed"
**Solution:**
- Is backend running? Check Terminal 1
- Is it on port 5000? `lsof -i :5000`
- Restart backend: `python run.py`

### Issue: "Cannot read property 'email' of undefined"
**Solution:**
- Token not being set
- Check localStorage: `F12 → Application → localStorage`
- Clear and try again: `localStorage.clear()`

### Issue: "Login form doesn't respond"
**Solution:**
- Check if `.env` file exists in frontend
- Verify `REACT_APP_API_URL=http://localhost:5000`
- Restart frontend: `npm start`

### Issue: Protected routes redirect to login
**Solution:**
- Session may have expired
- Clear localStorage and login again
- Check token is being saved: `F12 → Application → localStorage → token`

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ Can register new account without manual login
2. ✅ Can login to existing account
3. ✅ Can access protected pharmacy module
4. ✅ Can access protected dermatology module
5. ✅ Profile shows correct user information
6. ✅ No errors in browser console
7. ✅ All API requests return status 200

---

## 📝 Notes

- Users data stored in-memory (resets when backend restarts)
- For production, use actual database
- Test with different emails each time (or use same after registration)
- Clear browser cache if issues persist: `Ctrl+Shift+Delete`

---

## 🎉 All Tests Passing?

Congratulations! Your authentication system is working perfectly!

Next steps:
- Deploy to production
- Integrate with real database
- Add password hashing
- Implement refresh tokens
