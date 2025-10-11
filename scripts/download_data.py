"""
Script para download automático de dados públicos do Inside Airbnb.
Uso: python scripts/download_data.py
"""

import requests
import gzip
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs dos dados públicos (Inside Airbnb)
DATA_URLS = {
    "sao_paulo": "http://data.insideairbnb.com/brazil/sp/sao-paulo/2024-09-21/data/listings.csv.gz",
    "rio_de_janeiro": "http://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2024-09-18/data/listings.csv.gz"
}

def download_and_extract(city: str, url: str, output_dir: Path):
    """
    Download e extrai arquivo .csv.gz do Inside Airbnb.
    
    Args:
        city: Nome da cidade
        url: URL do arquivo
        output_dir: Diretório de saída
    """
    logger.info(f"Downloading data for {city}...")
    
    # Criar diretório se não existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Arquivos de saída
    gz_file = output_dir / f"{city}_listings.csv.gz"
    csv_file = output_dir / f"{city}_listings.csv"
    
    try:
        # Download
        logger.info(f"Downloading from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salvar .gz
        with open(gz_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded to {gz_file}")
        
        # Extrair
        logger.info(f"Extracting to {csv_file}")
        with gzip.open(gz_file, 'rb') as f_in:
            with open(csv_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remover .gz para economizar espaço
        gz_file.unlink()
        
        logger.info(f"✓ Successfully downloaded and extracted {city}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error downloading {city}: {e}")
        return False

def main():
    """Download dados de todas as cidades."""
    
    # Diretório de saída
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    logger.info("=" * 60)
    logger.info("DOWNLOADING INSIDE AIRBNB DATA")
    logger.info("=" * 60)
    
    success_count = 0
    
    for city, url in DATA_URLS.items():
        if download_and_extract(city, url, data_dir):
            success_count += 1
        logger.info("")
    
    logger.info("=" * 60)
    logger.info(f"COMPLETED: {success_count}/{len(DATA_URLS)} cities downloaded")
    logger.info("=" * 60)
    
    if success_count == len(DATA_URLS):
        logger.info("✓ All data downloaded successfully!")
        logger.info("Next steps:")
        logger.info("  1. Run: python main.py")
        logger.info("  2. Or run dashboard: streamlit run dashboard/globe_app.py")
    else:
        logger.warning("⚠ Some downloads failed. Check errors above.")

if __name__ == "__main__":
    main()
