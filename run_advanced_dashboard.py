#!/usr/bin/env python3
"""
Script para executar o dashboard avançado com análise histórica de preços
"""

import subprocess
import sys
import os

def check_dependencies():
    """
    Verifica se as dependências estão instaladas
    """
    required_packages = ['streamlit', 'pandas', 'numpy', 'plotly']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} encontrado")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} não encontrado")
    
    if missing_packages:
        print(f"\n📦 Instalando dependências faltantes: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("✅ Dependências instaladas com sucesso!")
    
    return len(missing_packages) == 0

def main():
    """
    Executa o dashboard avançado
    """
    print("🏠 Iniciando Dashboard Avançado - Análise Histórica de Preços")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Erro ao instalar dependências")
        return
    
    print("\n🚀 Iniciando dashboard avançado...")
    print("📱 O dashboard será aberto no seu navegador")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Para parar o dashboard, pressione Ctrl+C")
    print("=" * 60)
    
    # Executar o dashboard
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'dashboard/advanced_globe_app.py',
            '--server.port=8501',
            '--server.address=localhost'
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar dashboard: {e}")

if __name__ == "__main__":
    main()
