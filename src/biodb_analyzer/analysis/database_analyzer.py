from typing import Dict, List, Any
import pandas as pd
import numpy as np
from scipy import stats
import json

class DatabaseAnalyzer:
    def __init__(self, data: pd.DataFrame, table_name: str):
        self.data = data
        self.table_name = table_name
        self.insights = {}
        self.narrative = ""
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the database and generate insights"""
        self._analyze_structure()
        self._analyze_data_quality()
        self._analyze_relationships()
        self._analyze_distributions()
        self._generate_narrative()
        return {
            "structured_insights": self.insights,
            "narrative": self.narrative
        }
    
    def _analyze_structure(self):
        """Analyze database structure"""
        self.insights["structure"] = {
            "table_name": self.table_name,
            "table_size": {
                "rows": len(self.data),
                "columns": len(self.data.columns)
            },
            "data_types": {
                "numeric": len(self.data.select_dtypes(include=['number']).columns),
                "categorical": len(self.data.select_dtypes(include=['object']).columns),
                "datetime": len(self.data.select_dtypes(include=['datetime']).columns)
            }
        }
    
    def _analyze_data_quality(self):
        """Analyze data quality metrics"""
        self.insights["data_quality"] = {
            "missing_values": {
                "total": int(self.data.isnull().sum().sum()),
                "percentage": float(self.data.isnull().mean().mean() * 100),
                "by_column": self.data.isnull().sum().to_dict()
            },
            "duplicates": {
                "total": int(self.data.duplicated().sum()),
                "percentage": float(self.data.duplicated().mean() * 100)
            }
        }
    
    def _analyze_relationships(self):
        """Analyze relationships between columns"""
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            try:
                corr_matrix = self.data[numeric_cols].corr()
                self.insights["correlations"] = {
                    "strong": [],
                    "moderate": []
                }
                for i in range(len(numeric_cols)):
                    for j in range(i + 1, len(numeric_cols)):
                        col1 = numeric_cols[i]
                        col2 = numeric_cols[j]
                        corr = float(corr_matrix.iloc[i, j])
                        if abs(corr) > 0.7:
                            self.insights["correlations"]["strong"].append({
                                "columns": [col1, col2],
                                "correlation": abs(corr)
                            })
                        elif abs(corr) > 0.5:
                            self.insights["correlations"]["moderate"].append({
                                "columns": [col1, col2],
                                "correlation": abs(corr)
                            })
            except Exception as e:
                self.insights["correlations"] = {
                    "error": str(e),
                    "strong": [],
                    "moderate": []
                }
    
    def _analyze_distributions(self):
        """Analyze distributions of numeric variables"""
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        self.insights["distributions"] = {}
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            if len(col_data) > 0:
                stats = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std_dev": float(col_data.std()),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis())
                }
                self.insights["distributions"][col] = stats
    
    def _generate_narrative(self):
        """Generate a natural language narrative about the database"""
        self.narrative = f"""# Analysis Report for Table: {self.table_name}

## Overview
This table contains {self.insights['structure']['table_size']['rows']:,} records and 
{self.insights['structure']['table_size']['columns']} columns. The data includes:
- Numeric columns: {self.insights['structure']['data_types']['numeric']}
- Categorical columns: {self.insights['structure']['data_types']['categorical']}
- Datetime columns: {self.insights['structure']['data_types']['datetime']}

## Data Quality
The data quality analysis reveals:
- Missing values: {self.insights['data_quality']['missing_values']['total']:,} ({self.insights['data_quality']['missing_values']['percentage']:.1f}%)
- Duplicate records: {self.insights['data_quality']['duplicates']['total']:,} ({self.insights['data_quality']['duplicates']['percentage']:.1f}%)

### Columns with Missing Data
"""
        for col, missing in self.insights['data_quality']['missing_values']['by_column'].items():
            if missing > 0:
                self.narrative += f"- {col}: {missing} missing values ({missing/len(self.data)*100:.1f}%)\n"
        
        self.narrative += "\n## Relationships\n"
        
        if "correlations" in self.insights:
            if "error" in self.insights["correlations"]:
                self.narrative += f"\n### Correlation Analysis Error\n{self.insights['correlations']['error']}\n"
            else:
                if self.insights["correlations"]["strong"]:
                    self.narrative += "\n### Strong Relationships (r > 0.7)\n"
                    for corr in self.insights["correlations"]["strong"]:
                        self.narrative += f"- {corr['columns'][0]} and {corr['columns'][1]} have a strong relationship (r={corr['correlation']:.2f})\n"
                
                if self.insights["correlations"]["moderate"]:
                    self.narrative += "\n### Moderate Relationships (r > 0.5)\n"
                    for corr in self.insights["correlations"]["moderate"]:
                        self.narrative += f"- {corr['columns'][0]} and {corr['columns'][1]} have a moderate relationship (r={corr['correlation']:.2f})\n"
        else:
            self.narrative += "\n### No Correlation Analysis Available\nNot enough numeric columns for correlation analysis.\n"
        
        self.narrative += "\n## Distribution Analysis\n"
        for col, stats in self.insights["distributions"].items():
            self.narrative += f"""\n### {col}
- Mean: {stats['mean']:.2f}
- Median: {stats['median']:.2f}
- Standard Deviation: {stats['std_dev']:.2f}
- Skewness: {stats['skewness']:.2f} ({'Right-skewed' if stats['skewness'] > 0 else 'Left-skewed' if stats['skewness'] < 0 else 'Symmetric'})
- Kurtosis: {stats['kurtosis']:.2f} ({'Heavy-tailed' if stats['kurtosis'] > 3 else 'Light-tailed' if stats['kurtosis'] < 3 else 'Normal'})
"""