# BioDB Analyzer

BioDB Analyzer is a powerful tool for analyzing bioinformatics databases. It provides a command-line interface for data analysis and visualization, making it easier for early career scientists to work with omics data.

## Installation

### For macOS

#### Using Homebrew
```bash
# Install Python 3.10
brew install python@3.10

# Create and activate virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install the package
pip install biodb-analyzer


### For Linux

# Install Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv

# Create and activate virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install the package
pip install biodb-analyzer

## Commands

# Discover database structure
biodb-analyzer discover /path/to/your/database.db

# Analyze database contents
biodb-analyzer analyze /path/to/your/database.db

# Generate visualizations

```bash
# Generate a comprehensive dashboard
biodb-analyzer visualize /path/to/database.db --output-dir visualizations

# Open the dashboard in your browser
open visualizations/dashboard.html

# Generate analysis plan
biodb-analyzer plan /path/to/your/database.db --question "Your research question"

# Analyze specific tables
biodb-analyzer analyze /path/to/your/database.db --tables "table1 table2"

# Export analysis results
biodb-analyzer analyze /path/to/your/database.db --export results.csv

# Generate multiple visualizations
biodb-analyzer visualize /path/to/your/database.db --tables "table1 table2" --output-dir visualizations/

## Install development dependencies:

pip install -r requirements.txt
pip install -r dev-requirements.txt

## Install in development mode:

pip install -e .

## TEST

# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py

# Run with coverage
pip install pytest-cov
pytest --cov=biodb_analyzer tests/

