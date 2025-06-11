# BioDB Analyzer

BioDB Analyzer is a powerful tool for analyzing bioinformatics databases. It provides both command-line and web-based interfaces for data analysis and visualization, making it easier for early career scientists to work with omics data.

![BioDB Analyzer Dashboard](docs/images/dashboard-screenshot.png)

## Installation

### System Requirements
- Python 3.10 or higher
- Minimum 4GB RAM recommended
- Supported operating systems: macOS, Linux
- Web browser (for dashboard visualization)

### macOS Installation

#### Using Homebrew (Recommended)
```bash
# Install Python 3.10
brew install python@3.10

# Create and activate virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install the package
pip install biodb-analyzer
```

#### Manual Installation
```bash
# Install Python 3.10 from python.org
# Create virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Install Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv

# Create and activate virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install the package
pip install biodb-analyzer
```

#### Red Hat/CentOS
```bash
# Install Python 3.10
sudo yum install python310 python310-venv

# Create and activate virtual environment
python3.10 -m venv biodb-env
source biodb-env/bin/activate

# Install the package
pip install biodb-analyzer
```

## Getting Started

### Basic Usage
```bash
# Discover database structure
biodb-analyzer discover /path/to/your/database.db

# Analyze database contents
biodb-analyzer analyze /path/to/your/database.db

# Generate visualizations
biodb-analyzer visualize /path/to/database.db --output-dir visualizations
```

### Advanced Features

#### Data Visualization
```bash
# Generate a comprehensive dashboard
biodb-analyzer visualize /path/to/database.db --output-dir visualizations

# Open the dashboard in your browser
open visualizations/dashboard.html
```

#### Analysis Planning
```bash
# Generate analysis plan
biodb-analyzer plan /path/to/your/database.db --question "Your research question"
```

#### Table-Specific Analysis
```bash
# Analyze specific tables
biodb-analyzer analyze /path/to/your/database.db --tables "table1 table2"
```

#### Exporting Results
```bash
# Export analysis results
biodb-analyzer analyze /path/to/your/database.db --export results.csv
```

## Story-Based Data Analysis

BioDB Analyzer introduces a story-based approach to data analysis, guiding users through their data exploration journey. The dashboard is organized into thematic sections that tell the story of your data:


## Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## Features

- Database Structure Discovery
- Automated Data Analysis
- Interactive Visualizations
- Analysis Planning Assistant
- Table-Specific Analysis
- Result Exporting
- Web-based Dashboard Interface
- Story-Based Data Exploration
- Automated Insights Generation

## Support

For support, please:
- Check the documentation
- Open an issue on GitHub

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details