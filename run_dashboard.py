"""
Script para executar o dashboard de análise de preços de aluguel.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """
    Executa o dashboard Streamlit.
    """
    print("🏠 Iniciando Rental Price Prediction Dashboard...")
    print("=" * 60)
    
    # Verificar se o arquivo existe
    dashboard_path = Path("dashboard/globe_app.py")
    if not dashboard_path.exists():
        print("❌ Erro: Arquivo dashboard/globe_app.py não encontrado!")
        return
    
    # Verificar se streamlit está instalado
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} encontrado")
    except ImportError:
        print("❌ Streamlit não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
    
    # Verificar dependências
    required_packages = ["pandas", "numpy", "plotly"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} encontrado")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
    
    # Executar dashboard
    print("\n🚀 Iniciando dashboard...")
    print("📱 O dashboard será aberto no seu navegador")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Para parar o dashboard, pressione Ctrl+C")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar dashboard: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()


