import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from sqlalchemy import create_engine, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SchemaValidator:
    """
    Validates database schema and provides schema information for analysis
    """
    def __init__(self, db_path: str):
        """
        Initialize the schema validator
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = Path(db_path)
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.inspector = inspect(self.engine)
        self.schema = self._load_schema()
        self._validate_database_size()

    def _load_schema(self) -> Dict[str, Any]:
        """
        Load and validate the database schema
        
        Returns:
            Dictionary containing schema information
        """
        schema = {
            'tables': {},
            'relationships': {},
            'primary_keys': {},
            'foreign_keys': {}
        }

        # Get all tables
        tables = self.inspector.get_table_names()
        
        for table in tables:
            # Get columns for each table
            columns = self.inspector.get_columns(table)
            schema['tables'][table] = {
                'columns': {col['name']: col['type'].__name__ for col in columns},
                'primary_key': self.inspector.get_pk_constraint(table)['constrained_columns']
            }
            
            # Get foreign keys
            fks = self.inspector.get_foreign_keys(table)
            if fks:
                schema['foreign_keys'][table] = fks

        return schema

    def _validate_database_size(self) -> None:
        """
        Validate database size and provide warnings if too large
        """
        try:
            # Get database size in bytes
            size = self.db_path.stat().st_size
            size_mb = size / (1024 * 1024)
            
            if size_mb > 1000:  # Warning threshold
                logger.warning(f"Database size is {size_mb:.2f}MB. Large database may affect analysis performance.")
                
            if size_mb > 2000:  # Critical threshold
                logger.warning(f"Database size is {size_mb:.2f}MB. Analysis may be slow. Consider using sampling.")
                
        except Exception as e:
            logger.error(f"Error checking database size: {str(e)}")

    def validate_analysis(self, analysis: str) -> bool:
        """
        Validate if the analysis is supported by the schema
        
        Args:
            analysis: Analysis query or prompt
            
        Returns:
            True if analysis is valid, False otherwise
        """
        # Basic validation - check if tables mentioned in analysis exist
        tables = self._extract_tables_from_analysis(analysis)
        for table in tables:
            if table not in self.schema['tables']:
                logger.warning(f"Table '{table}' mentioned in analysis does not exist in database")
                return False
        
        return True

    def _extract_tables_from_analysis(self, analysis: str) -> List[str]:
        """
        Extract table names from biodb_analyzer.analysis text
        
        Args:
            analysis: Analysis query or prompt
            
        Returns:
            List of table names mentioned in analysis
        """
        # Simple implementation - can be made more sophisticated
        words = analysis.lower().split()
        return [word for word in words if word in self.schema['tables']]

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information for prompts
        
        Returns:
            Dictionary containing schema information
        """
        return {
            'tables': self.schema['tables'],
            'relationships': self.schema['foreign_keys'],
            'primary_keys': self.schema['primary_keys']
        }

    def get_table_size(self, table_name: str) -> int:
        """
        Get approximate size of a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                return result.scalar()
        except Exception as e:
            logger.error(f"Error getting table size: {str(e)}")
            return 0

    def get_sample_size(self, table_name: str, confidence: float = 0.99, margin_error: float = 0.01) -> int:
        """
        Calculate sample size based on table size and statistical requirements
        
        Args:
            table_name: Name of the table
            confidence: Confidence level (default: 0.99)
            margin_error: Margin of error (default: 0.01)
            
        Returns:
            Number of rows to sample
        """
        table_size = self.get_table_size(table_name)
        if table_size == 0:
            return 0
            
        # Using simplified formula for large populations
        z = 2.576  # Z-score for 99% confidence
        p = 0.5    # Most conservative estimate
        
        numerator = z**2 * p * (1 - p)
        denominator = margin_error**2 / table_size
        
        sample_size = numerator / denominator
        
        # Ensure we don't sample more than 10% of large tables
        max_sample = min(table_size * 0.1, 10000)
        
        return min(int(sample_size), max_sample)
