# Common Red Errors & Solutions - EduGuard Setup

## 🔴 RED ERRORS & QUICK FIXES

### **ERROR 1: Python Not Recognized**
```
❌ Error: 'python' is not recognized as an internal or external command...
✅ SOLUTION:
1. Install Python from https://www.python.org/downloads/
2. IMPORTANT: Check "Add Python to PATH" during installation
3. Restart Command Prompt
4. Try 'py' instead of 'python'
```

### **ERROR 2: Virtual Environment Failed**
```
❌ Error: 'venv\Scripts\activate' is not recognized...
✅ SOLUTION:
1. Run Command Prompt as Administrator
2. Use full path: cd c:\Desktop\Minor-project-1
3. Create new venv: python -m venv venv
4. Activate: venv\Scripts\activate
```

### **ERROR 3: Pip Install Failed**
```
❌ Error: Could not install packages due to EnvironmentError...
✅ SOLUTION:
1. Update pip: python -m pip install --upgrade pip
2. Use --user flag: pip install --user flask
3. Try different mirror: pip install -i https://pypi.org/simple/ flask
4. Install one by one: pip install flask, then pip install sqlalchemy
```

### **ERROR 4: ModuleNotFoundError**
```
❌ Error: ModuleNotFoundError: No module named 'flask'...
✅ SOLUTION:
1. Make sure virtual environment is activated (should see (venv))
2. Install packages: pip install -r requirements.txt
3. Check installed packages: pip list
4. Restart Command Prompt after installation
```

### **ERROR 5: Database Connection Failed**
```
❌ Error: sqlite3.OperationalError: unable to open database file...
✅ SOLUTION:
1. Delete existing database: del *.db
2. Run: python seed_database.py
3. Check permissions on folder
4. Make sure you're in correct directory: cd c:\Desktop\Minor-project-1
```

### **ERROR 6: Port Already in Use**
```
❌ Error: OSError: [WinError 10048] Address already in use...
✅ SOLUTION:
1. Close other applications using port 5000
2. Kill processes: taskkill /F /IM python.exe
3. Restart computer
4. Use different port: python run.py --port 5001
```

### **ERROR 7: Flask Application Error**
```
❌ Error: AttributeError: 'Flask' object has no attribute 'run'...
✅ SOLUTION:
1. Check if run.py file exists: dir run.py
2. Check app.py content: type app.py
3. Try running: python app.py instead of python run.py
4. Check Flask installation: python -c "import flask; print('OK')"
```

### **ERROR 8: Import Errors**
```
❌ Error: ImportError: cannot import name 'db' from 'app'...
✅ SOLUTION:
1. Check if models.py exists: dir models.py
2. Check if app.py imports models: type app.py | findstr models
3. Run database setup: python seed_database.py
4. Check file structure: dir /b
```

### **ERROR 9: Permission Denied**
```
❌ Error: PermissionError: [Errno 13] Permission denied...
✅ SOLUTION:
1. Run Command Prompt as Administrator
2. Close antivirus temporarily
3. Check if files are not read-only: attrib -r *.*
4. Change folder permissions: icacls . /grant Everyone:F
```

### **ERROR 10: Git Clone Failed**
```
❌ Error: fatal: unable to access 'https://github.com/...'...
✅ SOLUTION:
1. Check internet connection
2. Use GitHub Desktop instead of git commands
3. Download ZIP file instead: https://github.com/USER/REPO/archive/refs/heads/main.zip
4. Check repository URL spelling
```

---

## 🛠️ STEP-BY-STEP DEBUGGING

### **Step 1: Check Environment**
```bash
# Check Python version
python --version

# Check current directory
cd
dir

# Check if virtual environment exists
dir venv

# Check virtual environment activation
echo %VIRTUAL_ENV%
```

### **Step 2: Verify Installation**
```bash
# Test Flask
python -c "import flask; print('Flask:', flask.__version__)"

# Test Pandas
python -c "import pandas; print('Pandas:', pandas.__version__)"

# Test Scikit-learn
python -c "import sklearn; print('Sklearn:', sklearn.__version__)"

# Test SQLAlchemy
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
```

### **Step 3: Check Project Files**
```bash
# List all Python files
dir *.py

# Check essential files
dir app.py models.py run.py seed_database.py requirements.txt

# Check templates folder
dir templates\*.html

# Check database
dir *.db
```

---

## 🚨 SPECIFIC ERROR MESSAGES & FIXES

### **Flask Template Error**
```
❌ Error: jinja2.exceptions.TemplateNotFound: login.html
✅ SOLUTION:
1. Check templates folder exists: dir templates
2. Check login.html exists: dir templates\login.html
3. Check template path in app.py: type app.py | findstr templates
4. Restart Flask application
```

### **Database Table Error**
```
❌ Error: sqlalchemy.exc.OperationalError: no such table: users
✅ SOLUTION:
1. Delete database: del *.db
2. Run seed script: python seed_database.py
3. Check models.py for table definitions
4. Verify SQLAlchemy configuration in app.py
```

### **Login Session Error**
```
❌ Error: werkzeug.exceptions.BadRequestKeyError: 400 Bad Request
✅ SOLUTION:
1. Check form fields in login.html
2. Check request.form in routes.py
3. Verify form method is POST
4. Check CSRF token if using Flask-WTF
```

### **Static File Error**
```
❌ Error: 404 Not Found for /static/css/style.css
✅ SOLUTION:
1. Check static folder exists: dir static
2. Check CSS file exists: dir static\css\style.css
3. Check static folder configuration in app.py
4. Restart Flask application
```

---

## 🔧 AUTO-FIX SCRIPTS

### **Complete Setup Script**
```batch
@echo off
echo EduGuard Auto-Fix Starting...
cd /d %~dp0

echo Checking Python...
python --version
if errorlevel 1 goto install_python

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 goto venv_error

echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 goto activate_error

echo Installing packages...
pip install -r requirements.txt
if errorlevel 1 goto install_error

echo Setting up database...
python seed_database.py
if errorlevel 1 goto database_error

echo Starting application...
python run.py
goto end

:install_python
echo Python not found. Please install from https://www.python.org/downloads/
pause
exit

:venv_error
echo Failed to create virtual environment. Trying alternative...
python -m venv myenv
call myenv\Scripts\activate
pip install -r requirements.txt
python seed_database.py
python run.py
goto end

:activate_error
echo Failed to activate virtual environment. Please run as Administrator.
pause
exit

:install_error
echo Package installation failed. Trying manual install...
pip install flask flask-sqlalchemy flask-login werkzeug pandas numpy scikit-learn
python seed_database.py
python run.py
goto end

:database_error
echo Database setup failed. Please check models.py and seed_database.py
pause
exit

:end
echo Setup completed!
pause
```

### **Quick Test Script**
```batch
@echo off
echo Testing EduGuard Setup...
cd /d %~dp0
call venv\Scripts\activate

echo Testing Python...
python --version

echo Testing Flask...
python -c "import flask; print('Flask OK')"

echo Testing Database...
python -c "from app import create_app; print('App OK')"

echo Testing Files...
if exist app.py (echo app.py: OK) else (echo app.py: MISSING)
if exist models.py (echo models.py: OK) else (echo models.py: MISSING)
if exist run.py (echo run.py: OK) else (echo run.py: MISSING)

echo Starting test run...
python run.py
pause
```

---

## 📱 GETTING HELP

### **If You See Red Errors:**
```
🆘 Quick Help:
1. Take screenshot of error message
2. Note which step failed (installation, database, startup)
3. Check this guide for specific error
4. Try auto-fix script above
5. Contact for remote assistance
```

### **Debug Commands to Run:**
```bash
# Check all installations
pip list | findstr flask
pip list | findstr pandas
pip list | findstr sklearn

# Test application components
python -c "from app import create_app; from models import *; print('All imports OK')"

# Check database
python -c "from app import create_app; app = create_app(); with app.app_context(): print('DB OK')"
```

---

## 🎯 SUCCESS INDICATORS

### **No Red Errors When:**
```
✅ Success Checklist:
├── [ ] Python version shows correctly
├── [ ] Virtual environment activates (venv prefix)
├── [ ] All packages install without errors
├── [ ] Database seeding completes successfully
├── [ ] Flask starts without red error messages
├── [ ] Browser shows login page
├── [ ] Login works with credentials
├── [ ] Dashboard loads with data
└── [ ] All pages navigate correctly
```

---

## 📞 EMERGENCY HELP

### **Last Resort Options:**
```
🆘 If Nothing Works:
1. Use TeamViewer for remote help
2. Share screen on WhatsApp/Zoom
3. Send complete error logs
4. Try fresh installation in new folder
5. Use alternative setup (GitHub Desktop + ZIP download)
```

---

*Created for troubleshooting EduGuard setup issues*  
*Covers all common red errors and their solutions*  
*Last Updated: March 2026*
