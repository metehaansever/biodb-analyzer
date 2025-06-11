import click
from biodb_analyzer.database.connection import DatabaseConnection
import json
import os
import pandas as pd
import plotly.express as px
from biodb_analyzer.visualization.generate_dashboard import analyze_table, generate_correlations, generate_overall_summary, generate_dashboard_html
from biodb_analyzer.analysis.database_analyzer import DatabaseAnalyzer

@click.group()
def cli():
    """BioDB Analyzer - Tool for analyzing bioinformatics databases"""
    pass

@cli.command()
@click.argument('db_path', type=click.Path(exists=True))
def discover(db_path: str):
    """
    Discover and display available tables in the database
    
    Args:
        db_path: Path to the SQLite database file
    """
    try:
        with DatabaseConnection(db_path) as conn:
            tables = conn.get_table_names()
            click.echo("\nAvailable tables:")
            for table in tables:
                click.echo(f"\nTable: {table}")
                info = conn.get_table_info(table)
                click.echo("Columns:")
                for _, row in info.iterrows():
                    click.echo(f"- {row['name']} ({row['type']})")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--output', help='Output file for the report')
@click.option('--table', help='Specific table to analyze')
@click.option('--format', type=click.Choice(['markdown', 'json']), default='markdown', help='Output format')
def analyze(db_path: str, output: str, table: str, format: str):
    """Analyze the database and generate a comprehensive report"""
    try:
        with DatabaseConnection(db_path) as conn:
            # Get all tables if none specified
            tables = [table] if table else conn.get_table_names()
            
            reports = {}
            for table_name in tables:
                click.echo(f"\nAnalyzing table: {table_name}")
                query = f"SELECT * FROM {table_name} LIMIT 1000"
                data = conn.execute_query(query)
                
                if data.empty:
                    click.echo(f"Warning: No data found in table {table_name}", err=True)
                    continue
                
                analyzer = DatabaseAnalyzer(data, table_name)
                report = analyzer.analyze()
                reports[table_name] = report
                
                # Print narrative
                click.echo("\nAnalysis Narrative:")
                click.echo(report["narrative"])
                
                # Save report if output is specified
                if output:
                    if format == 'markdown':
                        with open(f"{output}_{table_name}.md", 'w') as f:
                            f.write(report["narrative"])
                    else:  # json
                        with open(f"{output}_{table_name}.json", 'w') as f:
                            json.dump(report, f, indent=2)
                    
                    click.echo(f"\nReport saved to {output}_{table_name}.{format}")
            
    except Exception as e:
        click.echo(f"Error analyzing database: {str(e)}", err=True)

@cli.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--output-dir', default='visualizations', help='Directory to save visualizations')
@click.option('--tables', multiple=True, help='Specific tables to visualize')
def visualize(db_path: str, output_dir: str, tables: tuple):
    """
    Generate a comprehensive data visualization dashboard
    
    Args:
        db_path: Path to the SQLite database file
        output_dir: Directory to save visualizations
        tables: Specific tables to visualize (optional)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        with DatabaseConnection(db_path) as conn:
            all_tables = conn.get_table_names()
            
            if tables:
                tables_to_process = tables
            else:
                tables_to_process = all_tables
            
            # Create a dictionary to store all data and insights
            dashboard_data = {
                "tables": [],
                "correlations": [],
                "insights": [],
                "summary": {}
            }
            
            for table in tables_to_process:
                if table not in all_tables:
                    click.echo(f"Warning: Table {table} not found in database", err=True)
                    continue
                
                click.echo(f"\nProcessing table: {table}")
                
                # Get data
                sample_query = f"SELECT * FROM {table} LIMIT 1000"
                sample_data = conn.execute_query(sample_query)
                
                if sample_data.empty:
                    click.echo(f"Warning: No data found in table {table}", err=True)
                    continue
                
                # Generate insights
                table_insights = analyze_table(sample_data)
                if table_insights["row_count"] == 0:
                    click.echo(f"Warning: Empty table {table}", err=True)
                    continue
                
                dashboard_data["tables"].append({
                    "name": table,
                    "insights": table_insights,
                    "info": conn.get_table_info(table).to_dict()
                })
                
                # Generate visualizations
                numeric_cols = sample_data.select_dtypes(include=['number']).columns
                
                # Create a dictionary to store plots
                plots = {
                    "histograms": [],
                    "box_plots": [],
                    "correlation": None
                }
                
                # Only generate plots if there are numeric columns
                if len(numeric_cols) > 0:
                    # Generate histograms
                    for col in numeric_cols:
                        fig = px.histogram(sample_data, x=col, title=f'Histogram of {col} in {table}')
                        plots["histograms"].append({
                            "column": col,
                            "plot": fig.to_html(full_html=False)
                        })
                    
                    # Generate box plots
                    for col in numeric_cols:
                        fig = px.box(sample_data, y=col, title=f'Box Plot of {col} in {table}')
                        plots["box_plots"].append({
                            "column": col,
                            "plot": fig.to_html(full_html=False)
                        })
                    
                    # Generate correlation matrix if multiple numeric columns
                    if len(numeric_cols) > 1:
                        corr_matrix = sample_data[numeric_cols].corr()
                        fig = px.imshow(corr_matrix, title=f'Correlation Matrix for {table}')
                        plots["correlation"] = fig.to_html(full_html=False)
                
                # Add plots to dashboard data
                dashboard_data["tables"][-1]["plots"] = plots
                
                # Generate correlations for the dashboard
                if len(numeric_cols) > 1:
                    correlations = generate_correlations(sample_data, numeric_cols)
                    dashboard_data["correlations"].extend(correlations)
            
            # Generate overall summary and insights
            dashboard_data["summary"] = generate_overall_summary(dashboard_data)
            
            # Generate the main dashboard HTML
            generate_dashboard_html(dashboard_data, output_dir)
            
            click.echo(f"Dashboard generated at {os.path.join(output_dir, 'dashboard.html')}")
            
    except Exception as e:
        click.echo(f"Error generating visualizations: {str(e)}", err=True)

@cli.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--question', required=True, help='Research question to generate analysis plan for')
@click.option('--output', help='File to save analysis plan')
def plan(db_path: str, question: str, output: str):
    """
    Generate an analysis plan for a research question
    
    Args:
        db_path: Path to the SQLite database file
        question: Research question to analyze
        output: File to save the analysis plan
    """
    try:
        with DatabaseConnection(db_path) as conn:
            tables = conn.get_table_names()
            
            click.echo("\nGenerating analysis plan...")
            
            # Generate basic analysis plan
            plan = {
                "research_question": question,
                "database_structure": {
                    "tables": tables,
                    "total_tables": len(tables)
                },
                "analysis_steps": [
                    {
                        "step": "Data Exploration",
                        "description": "Initial exploration of relevant tables and columns"
                    },
                    {
                        "step": "Data Cleaning",
                        "description": "Identify and handle missing values, outliers, and inconsistencies"
                    },
                    {
                        "step": "Statistical Analysis",
                        "description": "Perform appropriate statistical tests based on research question"
                    },
                    {
                        "step": "Visualization",
                        "description": "Create visualizations to support findings"
                    }
                ]
            }
            
            # Print plan
            click.echo("\nAnalysis Plan:")
            click.echo(json.dumps(plan, indent=2))
            
            # Save to file if output specified
            if output:
                with open(output, 'w') as f:
                    json.dump(plan, f, indent=2)
                click.echo(f"\nAnalysis plan saved to {output}")
                
    except Exception as e:
        click.echo(f"Error generating analysis plan: {str(e)}", err=True)

@cli.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.option('--output', required=True, help='File to export analysis results to')
@click.option('--format', type=click.Choice(['csv', 'json', 'excel']), default='csv', help='Output format')
@click.option('--tables', multiple=True, help='Specific tables to export')
def export(db_path: str, output: str, format: str, tables: tuple):
    """
    Export database analysis results
    
    Args:
        db_path: Path to the SQLite database file
        output: File to save the exported data
        format: Output format (csv, json, or excel)
        tables: Specific tables to export
    """
    try:
        with DatabaseConnection(db_path) as conn:
            all_tables = conn.get_table_names()
            
            # If specific tables are provided, use those
            if tables:
                tables_to_export = tables
            else:
                tables_to_export = all_tables
            
            # Create a dictionary to store all data
            all_data = {}
            
            for table in tables_to_export:
                if table not in all_tables:
                    click.echo(f"Warning: Table {table} not found in database", err=True)
                    continue
                
                click.echo(f"\nExporting table: {table}")
                
                # Get all data from table
                query = f"SELECT * FROM {table}"
                data = conn.execute_query(query)
                
                all_data[table] = {
                    "data": data,
                    "info": conn.get_table_info(table)
                }
            
            # Export based on format
            if format == 'csv':
                # Export each table to separate CSV file
                base_name = os.path.splitext(output)[0]
                for table, data in all_data.items():
                    data['data'].to_csv(f"{base_name}_{table}.csv", index=False)
                click.echo("Data exported to CSV files")
                
            elif format == 'json':
                # Convert DataFrames to dictionaries and save as JSON
                for table in all_data:
                    all_data[table]['data'] = all_data[table]['data'].to_dict(orient='records')
                with open(output, 'w') as f:
                    json.dump(all_data, f, indent=2)
                click.echo(f"Data exported to {output}")
                
            elif format == 'excel':
                # Create Excel writer
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for table, data in all_data.items():
                        data['data'].to_excel(writer, sheet_name=table, index=False)
                click.echo(f"Data exported to {output}")
                
    except Exception as e:
        click.echo(f"Error exporting data: {str(e)}", err=True)

if __name__ == '__main__':
    cli()