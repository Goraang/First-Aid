#!/bin/bash

echo "================================"
echo "FirstAid Platform - Setup Verify"
echo "================================"
echo ""

# Check directory structure
echo "📁 Checking directory structure..."
echo ""

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - MISSING"
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - MISSING"
    fi
}

echo "Backend:"
check_dir "backend/app"
check_dir "backend/app/routes"
check_dir "backend/app/services"
check_file "backend/requirements.txt"
check_file "backend/run.py"
check_file "backend/.env.example"

echo ""
echo "Frontend:"
check_dir "frontend/src"
check_dir "frontend/src/components"
check_dir "frontend/src/pages"
check_dir "frontend/src/services"
check_dir "frontend/src/styles"
check_file "frontend/package.json"
check_file "frontend/.env.example"

echo ""
echo "Database:"
check_file "database/medicines.json"
check_file "database/skin_diseases.json"

echo ""
echo "Documentation:"
check_file "README.md"
check_file "QUICK_START.md"
check_file "INSTALLATION.md"
check_file "API_DOCUMENTATION.md"
check_file "PROJECT_OVERVIEW.md"
check_file "TESTING_GUIDE.md"
check_file "DEPLOYMENT_GUIDE.md"
check_file "FILE_MANIFEST.md"
check_file "INDEX.md"
check_file "GETTING_STARTED.md"

echo ""
echo "================================"
echo "Checking dependencies..."
echo "================================"
echo ""

echo "Python:"
python3 --version 2>/dev/null && echo "✅ Python installed" || echo "❌ Python not found"

echo ""
echo "Node.js:"
node --version 2>/dev/null && echo "✅ Node.js installed" || echo "❌ Node.js not found"

echo ""
echo "npm:"
npm --version 2>/dev/null && echo "✅ npm installed" || echo "❌ npm not found"

echo ""
echo "Tesseract:"
tesseract --version 2>/dev/null | head -1 && echo "✅ Tesseract installed" || echo "⚠️  Tesseract not installed (needed for OCR)"

echo ""
echo "================================"
echo "Verification Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Read QUICK_START.md for 5-minute setup"
echo "2. Or read INSTALLATION.md for complete guide"
echo ""
echo "Start the platform:"
echo "  Backend: python backend/run.py"
echo "  Frontend: npm start (in frontend/)"
echo ""
