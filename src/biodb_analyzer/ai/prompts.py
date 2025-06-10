from typing import Dict, Any

# Base system prompt for bioinformatics analysis
BASE_PROMPT = """You are a bioinformatics database analyst. Your role is to analyze scientific databases and provide insights.
Focus on biological and genomic data patterns, relationships, and potential research questions.
Provide clear, structured responses with scientific context."""

# Database analysis prompt template
DATABASE_ANALYSIS_PROMPT = """Please analyze this database:

Database: {db_path}

Tables:
{tables}

Sample Data:
{sample_data}

Please provide:
1. A summary of the database structure and its potential biological significance
2. Potential relationships between tables and their biological implications
3. Suggested analyses that could be performed based on the data structure
4. Any patterns or insights you notice in the data that could be biologically relevant
5. Potential research questions that could be explored based on this data

Format your response in markdown with clear sections."""

# Visualization suggestions prompt template
VISUALIZATION_PROMPT = """You are a bioinformatics visualization expert. Please suggest visualizations for this data:

Table: {table_name}

Sample Data:
{sample_data}

Please provide:
1. Recommended visualization types (e.g., scatter plot, heatmap, etc.)
2. Key variables to plot
3. Biological insights that could be gained from these visualizations
4. Any data preprocessing needed before visualization

Format your response in markdown with clear sections."""

# Analysis plan prompt template
ANALYSIS_PLAN_PROMPT = """You are a bioinformatics researcher. Please create an analysis plan for this research question:

Research Question: {research_question}

Available Data:
Tables: {tables}

Sample Data:
{sample_data}

Please provide:
1. Required data preprocessing steps
2. Statistical methods to use
3. Expected results and interpretations
4. Potential challenges and solutions
5. Next steps for the analysis

Format your response in markdown with clear sections."""

# Table relationship analysis prompt template
RELATIONSHIP_ANALYSIS_PROMPT = """Please analyze the relationships between these tables:

Tables:
{tables}

Sample Data:
{sample_data}

Please provide:
1. Potential relationships between tables
2. Biological significance of these relationships
3. Suggested joins and queries to explore these relationships
4. Potential research questions based on these relationships

Format your response in markdown with clear sections."""

# Data quality analysis prompt template
DATA_QUALITY_PROMPT = """Please analyze the data quality:

Table: {table_name}

Sample Data:
{sample_data}

Please provide:
1. Data completeness analysis
2. Potential data quality issues
3. Recommendations for data cleaning
4. Impact of data quality on analysis

Format your response in markdown with clear sections."""

# Research question generation prompt template
RESEARCH_QUESTION_PROMPT = """Based on this database structure and sample data:

Tables:
{tables}

Sample Data:
{sample_data}

Please generate potential research questions that could be explored with this data.
Focus on questions that have biological significance and research value.

Format your response as a numbered list of research questions."""

# Prompt templates dictionary
PROMPT_TEMPLATES = {
    'database_analysis': DATABASE_ANALYSIS_PROMPT,
    'visualization': VISUALIZATION_PROMPT,
    'analysis_plan': ANALYSIS_PLAN_PROMPT,
    'relationship_analysis': RELATIONSHIP_ANALYSIS_PROMPT,
    'data_quality': DATA_QUALITY_PROMPT,
    'research_question': RESEARCH_QUESTION_PROMPT
}

# Helper function to format prompts
def format_prompt(template: str, **kwargs) -> str:
    """
    Format a prompt template with the provided arguments
    
    Args:
        template: The prompt template to format
        kwargs: Arguments to format into the template
        
    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required argument: {str(e)}")
