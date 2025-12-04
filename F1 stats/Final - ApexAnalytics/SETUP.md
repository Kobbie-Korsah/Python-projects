# 🏎️ F1 Analytics Suite - Complete Setup Guide

## 📋 **Prerequisites**

- Python 3.9 or higher
- pip package manager
- 500MB free disk space (for cache)
- Internet connection (for API calls)

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Create Project Structure**

```bash
# Create main directory
mkdir final_f1_dashboard
cd final_f1_dashboard

# Create subdirectories
mkdir core modules utils assets
mkdir assets/logos assets/logos/drivers assets/logos/teams
mkdir fastf1_cache cache
```

### **Step 2: Copy All Files**

Copy all the Python files into their respective directories:

```
final_f1_dashboard/
├── main.py
├── ui_main.py
├── styles.qss
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── data_cache.py
│   ├── threading.py
│   └── enums.py
├── modules/
│   ├── __init__.py
│   ├── driver_hub.py
│   ├── team_hub.py
│   ├── telemetry.py
│   ├── comparison.py
│   ├── analytics.py
│   └── ml_predictor.py
├── utils/
│   ├── __init__.py
│   ├── fastf1_utils.py
│   ├── api_utils.py
│   ├── plot_utils.py
│   └── ui_helpers.py
└── assets/
    └── logos/
        ├── drivers/  (place driver photos here)
        └── teams/    (place team logos here)
```

### **Step 3: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt

# OR install individually:
pip install PyQt6 fastf1 matplotlib pandas numpy requests scikit-learn scipy pillow
```

### **Step 4: Add Driver Photos & Team Logos**

Place your photos in the assets folder:

**Driver Photos** (`assets/logos/drivers/`):

- Name format: `VER.png`, `HAM.png`, `LEC.png`, etc.
- Recommended size: 200x200 pixels
- Format: PNG, JPG

**Team Logos** (`assets/logos/teams/`):

- Name format: `ferrari.png`, `red_bull_racing.png`, `mercedes.png`
- Recommended size: 300x150 pixels
- Format: PNG

### **Step 5: Run the Application**

```bash
python main.py
```

---

## 🎯 **Detailed Setup**

### **Virtual Environment (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Package Verification**

```bash
# Check if packages installed correctly
python -c "import PyQt6; print('PyQt6:', PyQt6.__version__)"
python -c "import fastf1; print('FastF1:', fastf1.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
```

---

## 📸 **Getting Driver Photos & Team Logos**

### **Option 1: Manual Download**

1. **Driver Photos**: Search for official F1 driver headshots
2. **Team Logos**: Download from official team websites
3. Resize to recommended dimensions
4. Save with correct naming convention

### **Option 2: Use Existing Assets**

If you already have photos in `assets/logos/`, ensure they follow this naming:

**Drivers:**

- VER.png (Max Verstappen)
- HAM.png (Lewis Hamilton)
- LEC.png (Charles Leclerc)
- SAI.png (Carlos Sainz)
- PER.png (Sergio Perez)
- RUS.png (George Russell)
- NOR.png (Lando Norris)
- PIA.png (Oscar Piastri)
- etc.

**Teams:**

- ferrari.png
- mercedes.png
- red_bull_racing.png
- mclaren.png
- aston_martin.png
- alpine.png
- williams.png
- alphatauri.png
- alfa_romeo.png
- haas.png

---

## ⚙️ **Configuration**

### **API Settings**

The Jolpica F1 API is free and doesn't require a key. If you want to use a different API, edit `core/enums.py`:

```python
JOLPICA_BASE_URL = "https://api.jolpi.ca/ergast/f1"
```

### **Cache Settings**

Adjust cache settings in `core/enums.py`:

```python
CACHE_EXPIRY_HOURS = 24          # How long to keep cache
MAX_CACHE_SIZE_MB = 500          # Maximum cache size
```

### **Theme Customization**

Edit `styles.qss` to customize colors:

```css
/* Change F1 Red accent color */
#E10600  /* Default F1 Red */

/* Change to custom color */
#YOUR_COLOR_HERE
```

---

## 🧪 **Testing the Application**

### **Test 1: Driver Hub**

1. Launch application
2. Ensure "Driver Mode" is active
3. Go to "Driver Hub" tab
4. Select "Max Verstappen" from dropdown
5. Set year range: 2020-2024
6. Click "Load Driver Data"
7. Verify:
   - ✅ Photo loads
   - ✅ Stats populate
   - ✅ Charts render

### **Test 2: Telemetry**

1. Go to "Telemetry" tab
2. Select driver: VER
3. Select race: Bahrain 2024
4. Click "Load Telemetry"
5. Verify speed and throttle/brake charts load

### **Test 3: Comparison**

1. Go to "Comparison" tab
2. Select 2 drivers (e.g., VER, HAM)
3. Click "Compare Drivers"
4. Verify comparison charts appear

---

## 🐛 **Troubleshooting**

### **Issue: "No module named 'PyQt6'"**

**Solution:**

```bash
pip install PyQt6
```

### **Issue: "FastF1 session load failed"**

**Solution:**

- Check internet connection
- Verify race name spelling
- Try different season/race
- Clear FastF1 cache: `rm -rf fastf1_cache/*`

### **Issue: "Driver photo not loading"**

**Solution:**

- Check file exists: `assets/logos/drivers/VER.png`
- Check file format (PNG/JPG)
- Check file permissions
- Verify naming matches driver code exactly

### **Issue: "Application crashes on startup"**

**Solution:**

```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip uninstall -y PyQt6 fastf1 matplotlib pandas
pip install -r requirements.txt

# Check for errors
python main.py 2>&1 | grep -i error
```

### **Issue: "Charts not rendering"**

**Solution:**

- Matplotlib backend issue
- Try: `export QT_QPA_PLATFORM=offscreen` (Linux/Mac)
- Or: `set QT_QPA_PLATFORM=offscreen` (Windows)

---

## 📊 **Performance Optimization**

### **Speed Up Data Loading**

1. **Use Cache**: Data is automatically cached for 24 hours
2. **Limit Year Range**: Use smaller ranges (e.g., 2022-2024 instead of 2010-2024)
3. **Clear Old Cache**: Delete `cache/` and `fastf1_cache/` folders periodically

### **Reduce Memory Usage**

```python
# In data_cache.py, reduce max_memory_items:
self.max_memory_items = 25  # Default is 50
```

---

## 🚀 **Running in Production**

### **Create Standalone Executable (Optional)**

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --add-data "assets:assets" --add-data "styles.qss:." main.py

# Executable will be in dist/ folder
```

### **Deploy on Server**

```bash
# For remote access (use with caution)
python main.py --host 0.0.0.0 --port 8080
```

---

## 📝 **Next Steps**

1. ✅ Application running
2. ✅ Add your driver photos
3. ✅ Test all modules
4. 📄 Customize styling
5. 🎨 Add more features
6. 🚀 Share on GitHub

---

## 🆘 **Getting Help**

- **FastF1 Docs**: https://docs.fastf1.dev
- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Jolpica API**: https://jolpi.ca/ergast/f1/

---

**Built with ❤️ for F1 fans**
