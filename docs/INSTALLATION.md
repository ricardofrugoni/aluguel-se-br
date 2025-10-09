# Installation Guide

This guide provides step-by-step instructions for installing and setting up the
rental price prediction system.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

- **Python**: 3.8 or higher

- **Memory**: 8GB RAM minimum (16GB recommended)

- **Storage**: 5GB free space minimum

- **Internet**: Required for downloading data and POIs

### Required Software

- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)

- **Git**: Download from [git-scm.com](https://git-scm.com/downloads)

- **Code Editor**: VS Code, PyCharm, or any Python-compatible editor

## Installation Methods

### Method 1: Using pip (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rental-price-sudeste
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows

   venv\Scripts\activate

   # On macOS/Linux

   source venv/bin/activate
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies (optional)**
   ```bash
   pip install -e ".[dev]"
   ```

### Method 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rental-price-sudeste
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up directories**
   ```bash
   python -c "from config import *; print('Directories created')"
   ```

### Method 3: Using conda

1. **Create conda environment**
   ```bash
   conda create -n rental-prediction python=3.9
   conda activate rental-prediction
   ```

2. **Install dependencies**
   ```bash
   conda install pandas numpy scikit-learn matplotlib seaborn
   pip install -r requirements.txt
   ```text

## Configuration

### 1. Environment Variables (Optional)

Set the following environment variables for custom configuration:

```bash

# On Windows

set RENTAL_DATA_DIR=C:\path\to\data
set RENTAL_MODELS_DIR=C:\path\to\models
set RENTAL_REPORTS_DIR=C:\path\to\reports
set RENTAL_LOG_LEVEL=INFO

# On macOS/Linux

export RENTAL_DATA_DIR=/path/to/data
export RENTAL_MODELS_DIR=/path/to/models
export RENTAL_REPORTS_DIR=/path/to/reports
export RENTAL_LOG_LEVEL=INFO

```text

### 2. Configuration File

Create a custom configuration file:

```bash
cp config_example.json my_config.json

# Edit my_config.json with your settings

```

### 3. Logging Configuration

The system automatically creates log files in the `logs/` directory. To
customize logging:

```python
from logging_config import setup_logging
setup_logging(level=logging.DEBUG)  # Change log level

```text

## Verification

### 1. Test Installation

Run the following command to test the installation:

```bash
python -c "import src; print('Installation successful!')"

```text

### 2. Run Tests

```bash
pytest tests/ -v

```text

### 3. Run Example

```bash
python example_usage.py

```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're in the project directory and virtual environment is activated:

```bash
cd rental-price-sudeste
source venv/bin/activate  # On Windows: venv\Scripts\activate

```text

#### 2. OSMnx Installation Issues

**Problem**: OSMnx installation fails

**Solution**: Install OSMnx dependencies first:

```bash

# On Windows

conda install -c conda-forge osmnx

# On macOS/Linux

pip install osmnx

```text

#### 3. Memory Issues

**Problem**: Out of memory errors during POI extraction

**Solution**: Reduce the area of interest or increase system memory:

```python

# In config.py, reduce city bounds

city_bounds = {
    'sao_paulo': (-23.4, -23.8, -46.4, -46.8),  # Smaller area

    'rio_de_janeiro': (-22.8, -23.0, -43.2, -43.4)
}

```text

#### 4. Network Issues

**Problem**: Cannot download data or extract POIs

**Solution**: Check internet connection and try again:

```bash

# Test internet connection

ping google.com

# Try downloading data manually

python -c "from src.data.data_loader import DataLoader;
DataLoader().download_data(['sao_paulo'])"

```

### Platform-Specific Issues

#### Windows

1. **PowerShell Execution Policy**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Long Path Names**
   ```bash
   git config --global core.longpaths true
   ```

#### macOS

1. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Homebrew Dependencies**
   ```bash
   brew install geos proj
   ```

#### Linux

1. **System Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip build-essential
   sudo apt-get install libgeos-dev libproj-dev
   ```text

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"

```text

### 2. Set up Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install

```

### 3. Configure IDE

#### VS Code

1. Install Python extension

2. Set Python interpreter to virtual environment

3. Configure settings:
   ```json
   {
     "python.defaultInterpreterPath": "./venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black"
   }
   ```text

#### PyCharm

1. Open project in PyCharm

2. Configure Python interpreter to virtual environment

3. Enable code inspection and formatting

## Performance Optimization

### 1. Memory Optimization

```python

# In config.py

import os
os.environ['OMP_NUM_THREADS'] = '4'  # Limit OpenMP threads

```text

### 2. Parallel Processing

```python

# In config.py

N_JOBS = 4  # Number of parallel jobs

```text

### 3. Caching

```python

# Enable OSMnx caching

import osmnx as ox
ox.config(use_cache=True, cache_dir='cache/')

```text

## Uninstallation

### 1. Remove Virtual Environment

```bash
deactivate
rm -rf venv  # On Windows: rmdir /s venv

```text

### 2. Remove Project Directory

```bash
cd ..
rm -rf rental-price-sudeste

```text

### 3. Remove Global Dependencies (if installed)

```bash
pip uninstall rental-price-prediction

```

## Support

### Getting Help

1. **Documentation**: Check README.md and docs/ directory

2. **Issues**: Open an issue on GitHub

3. **Discussions**: Use GitHub Discussions for questions

4. **Email**: Contact the development team

### Reporting Issues

When reporting issues, please include:

1. Operating system and version

2. Python version

3. Error messages and stack traces

4. Steps to reproduce the issue

5. Configuration files (if relevant)

### Contributing

1. Fork the repository

2. Create a feature branch

3. Make your changes

4. Add tests for new functionality

5. Run the test suite

6. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Note**: This installation guide assumes basic familiarity with Python and command-line tools. For beginners, consider taking a Python tutorial first.
