"""
Cria amostra pequena dos dados para demo e incluir no GitHub.
Uso: python scripts/prepare_sample.py
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample(input_file: Path, output_file: Path, n_samples: int = 1000):
    """
    Cria amostra estratificada dos dados.
    
    Args:
        input_file: Arquivo CSV completo
        output_file: Arquivo de saída (amostra)
        n_samples: Número de amostras
    """
    logger.info(f"Loading data from {input_file}")
    
    try:
        # Carregar dados completos
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} records")
        
        # Amostra estratificada por cidade e faixa de preço
        if 'city' in df.columns and 'price' in df.columns:
            # Criar estratos
            df['price_bin'] = pd.qcut(df['price'], q=5, labels=['very_low', 'low', 'medium', 'high', 'very_high'], duplicates='drop')
            
            # Amostra estratificada
            sample = df.groupby(['city', 'price_bin'], group_keys=False).apply(
                lambda x: x.sample(min(len(x), n_samples // 10))
            )
            
            # Remover coluna temporária
            sample = sample.drop('price_bin', axis=1)
        else:
            # Amostra aleatória simples
            sample = df.sample(min(n_samples, len(df)))
        
        logger.info(f"Created sample with {len(sample)} records")
        
        # Salvar
        output_file.parent.mkdir(parents=True, exist_ok=True)
        sample.to_csv(output_file, index=False)
        
        logger.info(f"✓ Sample saved to {output_file}")
        logger.info(f"File size: {output_file.stat().st_size / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error creating sample: {e}")
        return False

def main():
    """Criar amostras para demo."""
    
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    logger.info("=" * 60)
    logger.info("CREATING DEMO SAMPLES")
    logger.info("=" * 60)
    
    # Processar cada cidade
    cities = ["sao_paulo", "rio_de_janeiro"]
    
    for city in cities:
        input_file = raw_dir / f"{city}_listings.csv"
        output_file = processed_dir / f"{city}_sample.csv"
        
        if input_file.exists():
            logger.info(f"\nProcessing {city}...")
            create_sample(input_file, output_file, n_samples=500)
        else:
            logger.warning(f"⚠ {input_file} not found. Run download_data.py first.")
    
    # Combinar amostras
    logger.info("\n" + "=" * 60)
    logger.info("Combining samples...")
    
    combined_samples = []
    for city in cities:
        sample_file = processed_dir / f"{city}_sample.csv"
        if sample_file.exists():
            df = pd.read_csv(sample_file)
            combined_samples.append(df)
    
    if combined_samples:
        combined_df = pd.concat(combined_samples, ignore_index=True)
        output_file = processed_dir / "sample_data.csv"
        combined_df.to_csv(output_file, index=False)
        
        logger.info(f"✓ Combined sample saved: {len(combined_df)} records")
        logger.info(f"File: {output_file}")
        logger.info(f"Size: {output_file.stat().st_size / 1024:.2f} KB")
    
    logger.info("=" * 60)
    logger.info("✓ SAMPLES CREATED SUCCESSFULLY")
    logger.info("These samples will be included in GitHub for demo purposes")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
