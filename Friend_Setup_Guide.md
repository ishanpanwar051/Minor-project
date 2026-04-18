# EduGuard - Complete Setup & Installation Guide

## 🚀 QUICK SETUP FOR FRIEND'S PC

### **Method 1: Direct Folder Copy (Easiest)**

#### **Step 1: Copy Project Files**
```
📁 Copy this entire folder to friend's PC:
c:\Desktop\Minor-project-1\
```

#### **Step 2: Install Required Software**
```
💻 Install these on friend's PC:
1. Python 3.10+ (https://www.python.org/downloads/)
2. Git (https://git-scm.com/download/win)
3. VS Code (Optional - https://code.visualstudio.com/)
```

#### **Step 3: Setup Commands**
```bash
# Open Command Prompt as Administrator
cd c:\Desktop\Minor-project-1

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Initialize database
python seed_database.py

# Run the application
python run.py
```

---

## 📦 COMPLETE PACKAGE FOR FRIEND

### **Create Setup Package:**
<tool_call>write_to_file
<arg_key>CodeContent</arg_key>
<arg_value># EduGuard - Friend Setup Package

## 🎯 WHAT TO SEND TO FRIEND

### **Option 1: ZIP File (Recommended)**
```
📦 Send this ZIP file:
├── Minor-project-1.zip (Complete project)
├── Setup_Instructions.txt (This file)
└── Quick_Start_Guide.pdf (Optional)
```

### **Option 2: Google Drive/USB**
```
💾 Transfer Methods:
├── Google Drive Upload
├── USB Pen Drive
├── WhatsApp (Small files only)
└── Email Attachment (Split if needed)
```

---

## 💻 SYSTEM REQUIREMENTS

### **Minimum Requirements:**
```
🔧 Hardware Specs:
├── RAM: 4GB (8GB Recommended)
├── Storage: 2GB Free Space
├── Processor: Dual Core 2GHz+
└── OS: Windows 10/11

📦 Software Requirements:
├── Python 3.10 or higher
├── Internet Connection (For Bootstrap/CDN)
├── Command Prompt/PowerShell
└── Web Browser (Chrome/Firefox/Edge)
```

### **Recommended Requirements:**
```
🚀 Better Performance:
├── RAM: 8GB+
├── Storage: 5GB Free Space
├── Processor: Quad Core 3GHz+
└── SSD Storage (Faster loading)
```

---

## 🛠️ DETAILED INSTALLATION STEPS

### **Step 1: Python Installation**
```
🐍 Install Python 3.10+:
1. Go to: https://www.python.org/downloads/
2. Download Python 3.10 or higher
3. Run installer
4. IMPORTANT: Check "Add Python to PATH"
5. Click "Install Now"
6. Verify installation: Open CMD → type "python --version"
```

### **Step 2: Project Setup**
```bash
# Open Command Prompt (Search "cmd" in Windows)
# Navigate to project folder
cd Desktop\Minor-project-1

# Create virtual environment (isolated Python environment)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) at the beginning of your prompt
```

### **Step 3: Install Dependencies**
```bash
# Install all required packages
pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn

# Alternative: If requirements.txt exists
pip install -r requirements.txt
```

### **Step 4: Database Setup**
```bash
# Initialize the database with sample data
python seed_database.py

# You should see "Database seeded successfully!" message
```

### **Step 5: Run Application**
```bash
# Start the web application
python run.py

# Look for this message:
# * Running on http://127.0.0.1:5000/
# * Debug mode: on
```

---

## 🌐 ACCESSING THE APPLICATION

### **Open in Browser:**
```
🔗 URLs to Access:
├── Main App: http://127.0.0.1:5000
├── Login: http://127.0.0.1:5000/login
├── Dashboard: http://127.0.0.1:5000/dashboard
└── AI Chat: http://127.0.0.1:5000/ai/chat
```

### **Login Credentials:**
```
🔑 Default Login:
├── Admin: admin@eduguard.edu / admin123
├── Faculty: dr.sharma@eduguard.edu / faculty123
├── Counselor: counselor@eduguard.edu / counsel123
└── Students: Check database or use seed data
```

---

## 🔧 TROUBLESHOOTING GUIDE

### **Common Issues & Solutions:**

#### **Issue 1: Python not recognized**
```
❌ Error: 'python' is not recognized...
✅ Solution: 
1. Reinstall Python with "Add to PATH" checked
2. Or use 'py' instead of 'python' in commands
3. Restart Command Prompt after installation
```

#### **Issue 2: venv activation fails**
```
❌ Error: 'venv\Scripts\activate' not found...
✅ Solution:
1. Use full path: Desktop\Minor-project-1\venv\Scripts\activate
2. Or create new venv: python -m venv venv
3. Run as Administrator
```

#### **Issue 3: Package installation fails**
```
❌ Error: pip install fails...
✅ Solution:
1. Update pip: python -m pip install --upgrade pip
2. Use --user flag: pip install --user flask
3. Try different mirror: pip install -i https://pypi.org/simple/ flask
```

#### **Issue 4: Port already in use**
```
❌ Error: Port 5000 is already in use...
✅ Solution:
1. Close other applications using port 5000
2. Or change port: python run.py --port 5001
3. Kill process: netstat -ano | findstr :5000
```

#### **Issue 5: Database errors**
```
❌ Error: Database connection failed...
✅ Solution:
1. Delete app.db file (if exists)
2. Run: python seed_database.py
3. Check file permissions
```

---

## 📱 ALTERNATIVE SETUP METHODS

### **Method 2: Portable Python (No Installation)**
```
🎒 Portable Setup:
1. Download Portable Python
2. Extract to USB/Folder
3. Run portable python.exe
4. Follow same setup steps
```

### **Method 3: Docker (Advanced)**
```
🐳 Docker Setup:
1. Install Docker Desktop
2. Create Dockerfile
3. Build image: docker build -t eduguard .
4. Run container: docker run -p 5000:5000 eduguard
```

### **Method 4: Online Setup (GitHub)**
```
🌐 GitHub Method:
1. Upload project to GitHub
2. Friend clones: git clone [repository-url]
3. Follow same setup steps
4. Easy updates with git pull
```

---

## 📋 PRE-SETUP CHECKLIST

### **Before Starting:**
```
✅ Checklist:
├── [ ] Windows 10/11 PC
├── [ ] Internet connection
├── [ ] Admin rights on PC
├── [ ] 2GB+ free disk space
├── [ ] Antivirus temporarily disabled
└── [ ] Command Prompt access
```

### **After Setup:**
```
✅ Verification:
├── [ ] Python installed (python --version)
├── [ ] Virtual environment created
├── [ ] All packages installed
├── [ ] Database seeded
├── [ ] Application runs without errors
└── [ ] Login page accessible
```

---

## 🚀 QUICK START SCRIPT

### **Create setup.bat file for friend:**
```batch
@echo off
echo EduGuard Setup Starting...
echo.

cd /d %~dp0

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing packages...
pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn

echo Setting up database...
python seed_database.py

echo Starting application...
python run.py

pause
```

### **How to use:**
```
📝 Setup Script:
1. Save above code as "setup.bat"
2. Place in project folder
3. Friend just double-clicks setup.bat
4. Everything installs automatically
```

---

## 📞 SUPPORT & HELP

### **If Friend Faces Issues:**
```
🆘 Help Resources:
├── Call/Video call for live help
├── TeamViewer for remote assistance
├── Share screen on WhatsApp/Zoom
├── Send screenshots of errors
└── Check this troubleshooting guide first
```

### **Quick Debug Commands:**
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check virtual environment
where python

# Test Flask installation
python -c "import flask; print('Flask OK')"

# Check database
python -c "from app import create_app; print('App OK')"
```

---

## 🎯 SUCCESS INDICATORS

### **Setup Successful When:**
```
✅ Success Signs:
├── Command prompt shows (venv) prefix
├── No error messages during installation
├── Database seeding completes successfully
├── Application starts with "Running on http://127.0.0.1:5000/"
├── Browser shows login page at http://127.0.0.1:5000/login
├── Login works with admin credentials
└── Dashboard loads without errors
```

---

## 📁 FILES TO SEND

### **Complete Package:**
```
📦 Send these files/folders:
├── 📁 Minor-project-1/ (Complete project)
├── 📄 setup.bat (Auto-setup script)
├── 📄 requirements.txt (Dependencies list)
├── 📄 README.md (This guide)
└── 📄 Troubleshooting.txt (Common issues)
```

### **Minimum Required Files:**
```
🎯 Essential Files Only:
├── 📄 app.py (Main application)
├── 📄 run.py (Startup script)
├── 📄 models.py (Database models)
├── 📄 routes.py (Web routes)
├── 📄 seed_database.py (Database setup)
├── 📁 templates/ (HTML files)
├── 📁 static/ (CSS/JS files)
└── 📄 requirements.txt (Dependencies)
```

---

## 🎉 FINAL VERIFICATION

### **Test These Features:**
```
🧪 Functionality Tests:
├── [ ] Login page loads
├── [ ] Admin login works
├── [ ] Dashboard shows data
├── [ ] Students list loads
├── [ ] Risk analysis works
├── [ ] AI chat responds
├── [ ] Scholarships page loads
├── [ ] Community page works
├── [ ] Intervention planning works
└── [ ] All navigation links work
```

---

## 📈 PERFORMANCE TIPS

### **For Better Performance:**
```
⚡ Optimization Tips:
├── Close other browser tabs
├── Use Chrome/Firefox for best compatibility
├── Ensure 4GB+ RAM available
├── Use SSD if possible
├── Keep antivirus exceptions for project folder
└── Restart PC if running slow
```

---

*Created for easy project sharing and setup*  
*Compatible with Windows 10/11*  
*Last Updated: March 2026*
