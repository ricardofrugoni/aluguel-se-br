#!/bin/bash

echo "=================================================="
echo "RENTAL PRICE PREDICTION - DEMO SETUP"
echo "=================================================="
echo ""

# Criar ambiente virtual
echo "📦 Creating virtual environment..."
python -m venv venv

# Ativar ambiente
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependências
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download dados
echo "📥 Downloading Airbnb data..."
python scripts/download_data.py

# Criar amostras
echo "✂️ Creating demo samples..."
python scripts/prepare_sample.py

echo ""
echo "=================================================="
echo "✓ SETUP COMPLETED SUCCESSFULLY!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run full pipeline: python main.py"
echo "  2. Launch dashboard: streamlit run dashboard/globe_app.py"
echo ""
echo "For demo with sample data:"
echo "  streamlit run dashboard/globe_app.py"
echo ""
