import requests
from biodb_analyzer.ai.config import OllamaConfig
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging
from biodb_analyzer.ai.prompts import PROMPT_TEMPLATES, format_prompt
from biodb_analyzer.ai.schema_validator import SchemaValidator
from biodb_analyzer.ai.cache import AnalysisCache
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OllamaAnalyzer:
    """
    Integrates with Ollama for database analysis using Mistral or Llama 2
    
    Args:
        db_path: Path to the database file
        config: Configuration dictionary with model settings
    """
    def __init__(self, db_path: str, config: Dict[str, Any] = None):
        """
        Initialize the Ollama analyzer
        
        Args:
            db_path: Path to the database file
            config: Configuration dictionary with model settings
        """
        self.config = config or {}
        self.ollama_config = OllamaConfig()
        self.db_path = Path(db_path)
        
        # Initialize schema validator and cache
        self.schema_validator = SchemaValidator(str(self.db_path))
        cache_config = self.ollama_config.get_cache_config()
        self.cache = AnalysisCache(
            max_size_mb=cache_config.get('max_size_mb', 500),
            max_age_seconds=cache_config.get('max_age_seconds', 86400),
            confidence_threshold=cache_config.get('confidence_threshold', 0.95)
        )
        
        # Load model configuration
        self.model = self.config.get('model', self.ollama_config.get_model())
        self.api_url = self.config.get('api_url', self.ollama_config.get_api_url())
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2000)
        
        # Initialize sampling configuration
        sampling_config = self.ollama_config.get_sampling_config()
        self.min_sample_size = sampling_config.get('min_sample_size', 100)
        self.max_sample_size = sampling_config.get('max_sample_size', 10000)
        self.confidence_level = sampling_config.get('confidence_level', 0.99)
        self.margin_error = sampling_config.get('margin_error', 0.01)

    def analyze_database(self, tables: List[str], sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the database using Ollama with caching and validation
        
        Args:
            tables: List of table names
            sample_data: Sample data from tables
            
        Returns:
            Analysis results with confidence score
        """
        try:
            # Check if result is in cache
            cache_key = f"analyze_database_{self.db_path.stem}"
            cached_result = self.cache.get(cache_key, 'database_analysis', self.schema_validator)
            
            if cached_result and cached_result['confidence'] >= 0.95:
                return cached_result
                
            # Prepare prompt with schema information
            prompt = self._prepare_prompt(
                'database_analysis',
                db_path=str(self.db_path),
                tables=', '.join(tables),
                sample_data=json.dumps(sample_data, indent=2)
            )
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Store in cache
            self.cache.store(cache_key, 'database_analysis', response, self.schema_validator)
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing database: {str(e)}")
            raise

    def analyze_relationships(self, tables: List[str], sample_data: Dict[str, Any]) -> str:
        """
        Analyze relationships between tables
        
        Args:
            tables: List of table names
            sample_data: Sample data from relevant tables
            
        Returns:
            Analysis of table relationships
        """
        try:
            prompt = format_prompt(
                PROMPT_TEMPLATES['relationship_analysis'],
                tables=', '.join(tables),
                sample_data=json.dumps(sample_data, indent=2)
            )
            return self._generate_response(prompt)
        except Exception as e:
            logger.error(f"Error analyzing relationships: {str(e)}")
            raise

    def generate_visualization_suggestions(self, table_name: str, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visualization suggestions for a specific table with validation
        
        Args:
            table_name: Name of the table to analyze
            sample_data: Sample data from the table
            
        Returns:
            Visualization suggestions with confidence score
        """
        try:
            # Prepare prompt with schema information
            prompt = self._prepare_prompt(
                'visualization',
                table_name=table_name,
                sample_data=json.dumps(sample_data, indent=2)
            )
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Validate visualizations against schema
            visualizations = self._extract_visualizations(response['response'])
            valid_visualizations = []
            
            for viz in visualizations:
                if self.schema_validator.validate_analysis(viz):
                    valid_visualizations.append(viz)
                    
            response['visualizations'] = valid_visualizations
            response['confidence'] = self._calculate_confidence(response['response'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating visualization suggestions: {str(e)}")
            raise

    def _extract_visualizations(self, text: str) -> List[str]:
        """
        Extract visualization suggestions from response
        """
        visualizations = []
        lines = text.split('\n')
        
        for line in lines:
            if any(viz_type in line.lower() for viz_type in ['plot', 'chart', 'graph']):
                visualizations.append(line.strip())
                
        return visualizations

    def generate_analysis_plan(self, research_question: str, tables: List[str], sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an analysis plan with validation and confidence scoring
        
        Args:
            research_question: The research question to analyze
            tables: List of relevant tables
            sample_data: Sample data from tables
            
        Returns:
            Analysis plan with confidence score
        """
        try:
            # Prepare prompt with schema information
            prompt = self._prepare_prompt(
                'analysis_plan',
                research_question=research_question,
                tables=', '.join(tables),
                sample_data=json.dumps(sample_data, indent=2)
            )
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Validate analysis steps against schema
            steps = self._extract_analysis_steps(response['response'])
            valid_steps = []
            
            for step in steps:
                if self.schema_validator.validate_analysis(step):
                    valid_steps.append(step)
                    
            response['analysis_steps'] = valid_steps
            response['confidence'] = self._calculate_confidence(response['response'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating analysis plan: {str(e)}")
            raise

    def _extract_analysis_steps(self, text: str) -> List[str]:
        """
        Extract analysis steps from response
        """
        steps = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['step', 'analysis', 'procedure']):
                steps.append(line.strip())
                
        return steps

    def analyze_data_quality(self, table_name: str, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data quality with statistical validation
        
        Args:
            table_name: Name of the table to analyze
            sample_data: Sample data from the table
            
        Returns:
            Data quality analysis with confidence score
        """
        try:
            # Get table size for sampling
            table_size = self.schema_validator.get_table_size(table_name)
            sample_size = self.schema_validator.get_sample_size(
                table_name,
                confidence=self.confidence_level,
                margin_error=self.margin_error
            )
            
            # Prepare prompt with schema information and sample details
            prompt = self._prepare_prompt(
                'data_quality',
                table_name=table_name,
                sample_data=json.dumps(sample_data, indent=2),
                sample_size=sample_size,
                table_size=table_size
            )
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Validate quality metrics against schema
            metrics = self._extract_quality_metrics(response['response'])
            valid_metrics = []
            
            for metric in metrics:
                if self.schema_validator.validate_analysis(metric):
                    valid_metrics.append(metric)
                    
            response['quality_metrics'] = valid_metrics
            response['confidence'] = self._calculate_confidence(response['response'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {str(e)}")
            raise

    def _extract_quality_metrics(self, text: str) -> List[str]:
        """
        Extract quality metrics from response
        """
        metrics = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['metric', 'quality', 'issue']):
                metrics.append(line.strip())
                
        return metrics

    def generate_research_questions(self, tables: List[str], sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate research questions with schema validation
        
        Args:
            tables: List of tables to analyze
            sample_data: Sample data from tables
            
        Returns:
            List of research questions with confidence scores
        """
        try:
            # Prepare prompt with schema information
            prompt = self._prepare_prompt(
                'research_question',
                tables=', '.join(tables),
                sample_data=json.dumps(sample_data, indent=2)
            )
            
            # Generate response
            response = self._generate_response(prompt)
            
            # Extract and validate questions
            questions = self._extract_questions(response['response'])
            valid_questions = []
            
            for question in questions:
                if self.schema_validator.validate_analysis(question):
                    valid_questions.append(question)
                    
            response['research_questions'] = valid_questions
            response['confidence'] = self._calculate_confidence(response['response'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating research questions: {str(e)}")
            raise

    def _extract_questions(self, text: str) -> List[str]:
        """
        Extract research questions from response
        """
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            if line.strip().startswith('- '):  # Markdown list format
                questions.append(line.strip()[2:])
                
        return questions

    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate confidence score based on schema validation and response quality
        
        Args:
            response: Ollama's response
            
        Returns:
            Confidence score between 0 and 1
        """
        # Basic confidence calculation - can be made more sophisticated
        validation_config = self.ollama_config.get_validation_config()
        strict_mode = validation_config.get('strict_mode', True)
        
        # Check if response contains schema references
        schema_references = self._count_schema_references(response)
        
        # Calculate confidence based on schema references and strictness
        confidence = min(1.0, schema_references / 10)  # Normalize to 0-1 range
        
        if strict_mode:
            confidence *= 0.9  # Reduce confidence in strict mode
            
        return max(0.0, confidence)

    def _count_schema_references(self, response: str) -> int:
        """
        Count references to schema elements in response
        
        Args:
            response: Ollama's response
            
        Returns:
            Number of schema references found
        """
        schema_info = self.schema_validator.get_schema_info()
        count = 0
        
        # Check for table references
        for table in schema_info['tables']:
            if table.lower() in response.lower():
                count += 1
                
        # Check for column references
        for table, columns in schema_info['tables'].items():
            for column in columns['columns']:
                if f"{table}.{column}".lower() in response.lower():
                    count += 1
                    
        return count

    def _generate_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response using Ollama API with confidence scoring
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            Response dictionary with confidence score
        """
        url = f"{self.api_url}/api/generate"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Add confidence scoring based on schema validation
            confidence = self._calculate_confidence(result['response'])
            
            return {
                'response': result['response'],
                'confidence': confidence,
                'schema_valid': True,
                'timestamp': time.time()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise

    def _calculate_confidence(self, response: str) -> float:
        """
        Generate visualization suggestions for a specific table
        
        Args:
            table_name: Name of the table to analyze
            sample_data: Sample data from the table
            
        Returns:
            Visualization suggestions
        """
        prompt = f"""You are a bioinformatics visualization expert. Please suggest visualizations for this data:
        
        Table: {table_name}
        
        Sample Data:
        {json.dumps(sample_data, indent=2)}
        
        Please provide:
        1. Recommended visualization types (e.g., scatter plot, heatmap, etc.)
        2. Key variables to plot
        3. Biological insights that could be gained from these visualizations
        4. Any data preprocessing needed before visualization
        
        Format your response in markdown with clear sections."""
        
        return self._generate_response(prompt)

    def generate_analysis_plan(self, research_question: str, tables: List[str], sample_data: Dict[str, Any]) -> str:
        """
        Generate an analysis plan for a specific research question
        
        Args:
            research_question: The research question to address
            tables: List of available tables
            sample_data: Sample data from relevant tables
            
        Returns:
            Analysis plan
        """
        prompt = f"""You are a bioinformatics researcher. Please create an analysis plan for this research question:
        
        Research Question: {research_question}
        
        Available Data:
        Tables: {', '.join(tables)}
        
        Sample Data:
        {json.dumps(sample_data, indent=2)}
        
        Please provide:
        1. Required data preprocessing steps
        2. Statistical methods to use
        3. Expected results and interpretations
        4. Potential challenges and solutions
        5. Next steps for the analysis
        
        Format your response in markdown with clear sections."""
        
        return self._generate_response(prompt)
