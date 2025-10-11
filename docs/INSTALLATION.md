# 🚀 Installation Guide

## Quick Start (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/ricardofrugoni/aluguel-se-br.git
cd aluguel-se-br
```

### 2. Automated Setup
```bash
# Linux/Mac
chmod +x scripts/setup_demo.sh
./scripts/setup_demo.sh

# Windows
scripts\setup_demo.bat
```

### 3. Launch Dashboard
```bash
streamlit run dashboard/globe_app.py
```

## Manual Installation

### 1. Create Virtual Environment
```bash
python -m venv venv

# Activate
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Download Data
```bash
python scripts/download_data.py
```

### 4. Create Demo Samples
```bash
python scripts/prepare_sample.py
```

### 5. Run Full Pipeline (Optional)
```bash
python main.py
```

## Requirements

- Python 3.8+
- 4GB RAM minimum
- 2GB disk space

## Troubleshooting

### Common Issues

**1. Permission Error on Windows**
```bash
# Run as Administrator or use:
python -m pip install --user -r requirements.txt
```

**2. Download Fails**
```bash
# Check internet connection
# Try manual download from Inside Airbnb
```

**3. Memory Error**
```bash
# Use sample data only:
streamlit run dashboard/globe_app.py
```

## Data Sources

- **Inside Airbnb**: Public Airbnb data
- **OpenStreetMap**: POI data via Overpass API
- **Sample Data**: Included for demo purposes

## Support

- 📧 Email: ricardo@example.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: [Documentation](docs/)