# After Git Clone - Complete Setup Guide

## 🎯 AFTER GIT CLONE - STEP BY STEP

### **✅ Friend Successfully Did:**
```bash
git clone https://github.com/YOUR_USERNAME/EduGuard-System.git
```

---

## 📁 STEP 1: NAVIGATE TO PROJECT FOLDER

### **Method 1: Command Prompt**
```bash
# Navigate to project folder
cd EduGuard-System

# Verify you're in correct folder (should see app.py, run.py, etc.)
dir
```

### **Method 2: File Explorer**
```
1. Go to Desktop
2. Find "EduGuard-System" folder
3. Double-click to open
4. Click in address bar
5. Type "cmd" and press Enter
```

---

## 🐍 STEP 2: CHECK PYTHON INSTALLATION

### **Verify Python is Installed**
```bash
# Check Python version
python --version

# Should show: Python 3.10.x or higher

# If not installed, download from: https://www.python.org/downloads/
```

### **If Python Not Found:**
```bash
# Try 'py' instead of 'python'
py --version

# Or add Python to PATH:
# 1. Reinstall Python with "Add to PATH" checked
# 2. Restart Command Prompt
```

---

## 📦 STEP 3: CREATE VIRTUAL ENVIRONMENT

### **Create Virtual Environment**
```bash
# Create virtual environment (isolated Python space)
python -m venv venv

# Wait for completion (should create venv folder)
```

### **Activate Virtual Environment**
```bash
# Activate virtual environment
venv\Scripts\activate

# You should see (venv) at beginning of prompt
# Example: (venv) C:\Users\User\Desktop\EduGuard-System>
```

### **Verify Activation**
```bash
# Check Python path (should point to venv folder)
where python

# Should show something like:
# C:\Users\User\Desktop\EduGuard-System\venv\Scripts\python.exe
```

---

## 📚 STEP 4: INSTALL REQUIRED PACKAGES

### **Method 1: Install Individual Packages**
```bash
# Install Flask and required packages
pip install flask
pip install flask-sqlalchemy
pip install flask-login
pip install werkzeug
pip install pandas
pip install numpy
pip install scikit-learn

# Wait for each installation to complete
```

### **Method 2: Install All at Once**
```bash
# Install all packages in one command
pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn
```

### **Method 3: Using requirements.txt (if exists)**
```bash
# Install from requirements file
pip install -r requirements.txt
```

### **Verify Installation**
```bash
# Test Flask installation
python -c "import flask; print('Flask installed successfully')"

# Test other packages
python -c "import pandas, numpy; print('Data packages OK')"
python -c "import sklearn; print('ML package OK')"
```

---

## 🗄️ STEP 5: SETUP DATABASE

### **Initialize Database with Sample Data**
```bash
# Run database seeding script
python seed_database.py

# You should see messages like:
# - Creating database tables...
# - Adding sample students...
# - Adding sample users...
# - Database seeded successfully!
```

### **Verify Database Creation**
```bash
# Check if database file was created
dir *.db

# Should see: eduguard_working.db or similar database file
```

---

## 🚀 STEP 6: RUN THE APPLICATION

### **Start the Web Application**
```bash
# Run the Flask application
python run.py

# You should see output like:
# * Serving Flask app 'app'
# * Debug mode: on
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit
```

### **Keep Command Prompt Open**
```
📝 Important:
- Don't close this Command Prompt window
- The application runs as long as this window is open
- Open a new Command Prompt for other commands if needed
```

---

## 🌐 STEP 7: ACCESS THE APPLICATION

### **Open in Browser**
```
🔗 URLs to try:
├── Main: http://127.0.0.1:5000
├── Login: http://127.0.0.1:5000/login
├── Dashboard: http://127.0.0.1:5000/dashboard
└── AI Chat: http://127.0.0.1:5000/ai/chat
```

### **Login Credentials**
```
🔑 Default Login Accounts:
├── Admin: admin@eduguard.edu / admin123
├── Faculty: dr.sharma@eduguard.edu / faculty123
├── Faculty: dr.patel@eduguard.edu / faculty123
├── Faculty: ms.iyer@eduguard.edu / faculty123
└── Counselor: counselor@eduguard.edu / counsel123
```

---

## ✅ STEP 8: VERIFICATION - TEST FEATURES

### **Test These Pages:**
```
🧪 Functionality Checklist:
├── [ ] Login page loads and works
├── [ ] Dashboard shows student data
├── [ ] Students list displays
├── [ ] Risk analysis shows charts
├── [ ] AI chat responds to messages
├── [ ] Scholarships page loads
├── [ ] Community page works
├── [ ] Intervention planning works
├── [ ] All navigation links work
└── [ ] Data displays correctly
```

### **Test AI Chatbot:**
```
🤖 AI Chat Test:
1. Go to http://127.0.0.1:5000/ai/chat
2. Type: "hello"
3. Should get AI response
4. Try: "help", "study", "stress"
```

---

## 🔧 TROUBLESHOOTING AFTER CLONE

### **Common Issues & Solutions:**

#### **Issue 1: "python not recognized"**
```bash
❌ Error: 'python' is not recognized...
✅ Solutions:
1. Install Python from https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Restart Command Prompt
4. Try 'py' instead of 'python'
```

#### **Issue 2: venv activation fails**
```bash
❌ Error: 'venv\Scripts\activate' not found
✅ Solutions:
1. Run as Administrator
2. Use full path: EduGuard-System\venv\Scripts\activate
3. Create new venv: python -m venv venv
4. Check if venv folder exists: dir venv
```

#### **Issue 3: pip install fails**
```bash
❌ Error: Could not install packages...
✅ Solutions:
1. Update pip: python -m pip install --upgrade pip
2. Use --user flag: pip install --user flask
3. Try different mirror: pip install -i https://pypi.org/simple/ flask
4. Install one by one instead of all at once
```

#### **Issue 4: Database seeding fails**
```bash
❌ Error: Database creation failed...
✅ Solutions:
1. Delete any existing .db files: del *.db
2. Run: python seed_database.py
3. Check if app.py exists: dir app.py
4. Try: python -c "from app import create_app; print('App OK')"
```

#### **Issue 5: Application doesn't start**
```bash
❌ Error: Flask app failed to start...
✅ Solutions:
1. Check if run.py exists: dir run.py
2. Check Flask installation: python -c "import flask"
3. Try: python app.py instead of python run.py
4. Check for syntax errors in code
```

#### **Issue 6: Port 5000 already in use**
```bash
❌ Error: Port 5000 is already in use...
✅ Solutions:
1. Close other applications using port 5000
2. Restart computer
3. Kill process: taskkill /F /IM python.exe
4. Try different port: python run.py --port 5001
```

---

## 📱 ALTERNATIVE SETUP METHODS

### **Method 1: Auto-Setup Script**
```batch
@echo off
echo EduGuard Auto Setup Starting...
cd /d %~dp0
python -m venv venv
call venv\Scripts\activate
pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn
python seed_database.py
python run.py
pause
```
*Save as setup.bat and double-click*

### **Method 2: Step-by-Step Commands**
```bash
# Complete setup in one go
cd EduGuard-System && python -m venv venv && venv\Scripts\activate && pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn && python seed_database.py && python run.py
```

---

## 🎯 SUCCESS INDICATORS

### **Setup Successful When:**
```
✅ Success Checklist:
├── [ ] Command Prompt shows (venv) prefix
├── [ ] No red error messages during installation
├── [ ] Database seeding completes successfully
├── [ ] Flask application starts without errors
├── [ ] Browser shows login page at http://127.0.0.1:5000
├── [ ] Login works with admin credentials
├── [ ] Dashboard loads with student data
├── [ ] All pages load without errors
└── [ ] AI chatbot responds to messages
```

---

## 📞 GETTING HELP

### **If Setup Fails:**
```
🆘 Help Steps:
1. Take screenshot of error message
2. Note which step failed
3. Check this troubleshooting guide
4. Call/video chat for live help
5. Use TeamViewer for remote assistance
```

### **Useful Debug Commands:**
```bash
# Check Python version and location
python --version && where python

# Check installed packages
pip list

# Test Flask
python -c "import flask; print('Flask:', flask.__version__)"

# Test database connection
python -c "from app import create_app; print('App connection OK')"

# Check project files
dir /b *.py
```

---

## 🚀 NEXT STEPS AFTER SUCCESS

### **Explore the Application:**
```
🎓 Things to Try:
├── Login as different users (admin, faculty, counselor)
├── View student risk profiles
├── Test AI chatbot with different questions
├── Explore scholarship and community pages
├── Try intervention planning features
├── Check all navigation menus
└── Test responsive design on mobile
```

### **Customization Options:**
```
🔧 Possible Modifications:
├── Add new students to database
├── Modify risk calculation rules
├── Add new intervention types
├── Customize AI chatbot responses
├── Add new scholarship schemes
├── Modify color schemes and UI
└── Add new reports and analytics
```

---

## 📈 PERFORMANCE TIPS

### **For Better Performance:**
```
⚡ Optimization Tips:
├── Close other browser tabs
├── Use Chrome or Firefox browser
├── Ensure 4GB+ RAM available
├── Don't run too many programs simultaneously
├── Keep antivirus exceptions for project folder
├── Restart if running slow
└── Use SSD storage if available
```

---

## 🎉 CONCLUSION

**Congratulations!** 🎯

Your friend now has a fully functional EduGuard system running on their PC. They can:

- ✅ Login and explore all features
- ✅ Test ML predictions and risk analysis
- ✅ Use AI chatbot for student assistance
- ✅ Explore scholarship and community resources
- ✅ View intervention planning tools
- ✅ Experience complete student dropout prevention system

For any issues, refer to the troubleshooting guide or contact you for assistance!

---

*Setup Guide for EduGuard Project*  
*Compatible with Windows 10/11*  
*Last Updated: March 2026*
