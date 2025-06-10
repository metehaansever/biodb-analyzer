import os
import json
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import numpy as np
from scipy import stats

def analyze_table(data: pd.DataFrame) -> dict:
    """Generate insights about the table data"""
    insights = {
        "row_count": int(data.shape[0]),
        "column_count": int(data.shape[1]),
        "numeric_columns": int(data.select_dtypes(include=['number']).shape[1]),
        "categorical_columns": int(data.select_dtypes(include=['object']).shape[1]),
        "missing_values": int(data.isnull().sum().sum()),
        "statistics": {},
        "correlations": []
    }
    
    # Calculate statistics for numeric columns
    numeric_cols = data.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        col_stats = {
            "mean": float(data[col].mean()),
            "median": float(data[col].median()),
            "std": float(data[col].std()),
            "min": float(data[col].min()),
            "max": float(data[col].max()),
            "skewness": float(data[col].skew()),
            "kurtosis": float(data[col].kurtosis()),
            "missing": int(data[col].isnull().sum())
        }
        insights["statistics"][col] = col_stats
        insights[f"{col}_stats"] = col_stats
    
    # Calculate outliers using Z-score
    if len(numeric_cols) > 0:
        z_scores = np.abs(stats.zscore(data[numeric_cols], nan_policy='omit'))
        # Convert numpy array to pandas DataFrame
        z_scores_df = pd.DataFrame(z_scores, columns=numeric_cols)
        outliers = (z_scores_df > 3).sum().to_dict()
        insights["outliers"] = {str(col): int(count) for col, count in outliers.items()}
    else:
        insights["outliers"] = {}
    
    return insights

def generate_correlations(data: pd.DataFrame, numeric_cols: list) -> list:
    """Generate correlation insights between numeric columns"""
    correlations = []
    corr_matrix = data[numeric_cols].corr()
    
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col1 = numeric_cols[i]
            col2 = numeric_cols[j]
            corr = corr_matrix.iloc[i, j]
            abs_corr = abs(corr)
            
            # Only include significant correlations
            if abs_corr > 0.5:
                correlations.append({
                    "columns": [col1, col2],
                    "correlation": abs_corr,  # Store absolute value
                    "strength": "Strong" if abs_corr > 0.7 else "Moderate",
                    "p_value": 2 * (1 - stats.t.cdf(abs(corr) * np.sqrt(data.shape[0] - 2), data.shape[0] - 2))
                })
    
    return correlations

def generate_overall_summary(dashboard_data: dict) -> dict:
    """Generate overall summary of the database"""
    if not dashboard_data["tables"]:
        return {
            "total_tables": 0,
            "total_rows": 0,
            "total_columns": 0,
            "numeric_columns": 0,
            "categorical_columns": 0,
            "missing_values": 0,
            "strong_correlations": 0,
            "moderate_correlations": 0,
            "tables_with_correlations": 0,
            "tables_with_skewness": 0,
            "tables_with_outliers": 0
        }
    
    summary = {
        "total_tables": len(dashboard_data["tables"]),
        "total_rows": sum(table["insights"]["row_count"] for table in dashboard_data["tables"]),
        "total_columns": sum(len(table["info"]["name"]) for table in dashboard_data["tables"]),
        "numeric_columns": sum(table["insights"]["numeric_columns"] for table in dashboard_data["tables"]),
        "categorical_columns": sum(table["insights"]["categorical_columns"] for table in dashboard_data["tables"]),
        "missing_values": sum(table["insights"]["missing_values"] for table in dashboard_data["tables"]),
        "strong_correlations": len([c for c in dashboard_data["correlations"] if abs(c["correlation"]) > 0.7]),
        "moderate_correlations": len([c for c in dashboard_data["correlations"] if abs(c["correlation"]) > 0.5]),
        "tables_with_correlations": len([t for t in dashboard_data["tables"] if t["insights"].get("correlations")]),
        "tables_with_skewness": len([t for t in dashboard_data["tables"] 
                                    for col in t["insights"].get("statistics", {}).keys() 
                                    if t["insights"].get(f"{col}_stats", {}).get("skewness", 0) > 3]),
        "tables_with_outliers": len([t for t in dashboard_data["tables"] 
                                   for col in t["insights"].get("statistics", {}).keys() 
                                   if t["insights"].get(f"{col}_stats", {}).get("outliers", 0) > 0])
    }
    
    # Add data quality metrics
    if summary["total_rows"] > 0:
        summary["missing_value_rate"] = (summary["missing_values"] / 
                                        (summary["total_rows"] * summary["total_columns"])) * 100
    else:
        summary["missing_value_rate"] = 0
    
    return summary
def generate_dashboard_html(dashboard_data: dict, output_dir: str):
    """Generate the main dashboard HTML file"""
    try:
        print("\nGenerating dashboard HTML...")
        
        env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            autoescape=True
        )
        env.filters['abs'] = lambda x: abs(x)
        env.filters['zip'] = zip
        
        # Generate findings
        findings = []
        for table in dashboard_data["tables"]:
            insights = table["insights"]
            
            # Correlation findings
            if insights.get("correlations"):
                for corr in insights["correlations"]:
                    findings.append({
                        "table": table["name"],
                        "type": "Correlation",
                        "description": f"Strong relationship between {corr['columns'][0]} and {corr['columns'][1]} (r={corr['correlation']:.2f})"
                    })
            
            # Distribution findings
            for col in insights.get("statistics", {}).keys():
                col_stats = insights.get(f"{col}_stats", {})
                
                # Skewness
                if col_stats.get("skewness", 0) > 3:
                    findings.append({
                        "table": table["name"],
                        "type": "Skewed Distribution",
                        "description": f"Column {col} shows highly skewed distribution (skew={col_stats['skewness']:.2f})"
                    })
                
                # Outliers
                if col_stats.get("outliers", 0) > 0:
                    findings.append({
                        "table": table["name"],
                        "type": "Outliers",
                        "description": f"Column {col} has {col_stats['outliers']} potential outliers"
                    })
                
                # Missing values
                if col_stats.get("missing", 0) > insights["row_count"] * 0.1:
                    findings.append({
                        "table": table["name"],
                        "type": "Missing Data",
                        "description": f"Column {col} has {col_stats['missing']} missing values ({col_stats['missing']/insights['row_count']*100:.1f}% of data)"
                    })
        
        dashboard_data["findings"] = findings
        
        template = env.get_template('dashboard.html')
        try:
            html_content = template.render(
                dashboard=dashboard_data,
                title="BioDB Analyzer Dashboard",
                version="1.0"
            )
        except Exception as e:
            print(f"\nError rendering template: {str(e)}")
            print(f"Template variables: {json.dumps(dashboard_data, indent=2)}")
            raise
        
        output_path = os.path.join(output_dir, 'dashboard.html')
        with open(output_path, 'w') as f:
            f.write(html_content)
        
    except Exception as e:
        import traceback
        print(f"\nError in generate_dashboard_html: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise