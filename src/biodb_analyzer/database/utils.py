import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_query(query: str) -> bool:
    """
    Basic SQL query validation
    
    Args:
        query: SQL query string
        
    Returns:
        True if query appears valid, False otherwise
    """
    # Basic validation - this is not comprehensive but helps catch obvious issues
    query = query.strip()
    if not query:
        return False
    
    if not query.lower().startswith(('select', 'from', 'where')):
        logger.warning("Query doesn't start with SELECT/FROM/WHERE")
        return False
    
    return True

def format_query_results(results: Dict[str, Any]) -> str:
    """
    Format query results for display
    
    Args:
        results: Dictionary containing query results
        
    Returns:
        Formatted string representation of results
    """
    if not results:
        return "No results found"
    
    formatted = []
    for key, value in results.items():
        formatted.append(f"{key}: {value}")
    
    return "\n".join(formatted)

def get_database_type(db_path: str) -> Optional[str]:
    """
    Get the type of database based on its tables
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Database type string if recognized, None otherwise
    """
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Common bioinformatics database patterns
        if any(table in tables for table in ['contigs', 'genes', 'genomes']):
            return "Bioinformatics database"
        if any(table in tables for table in ['samples', 'measurements', 'experiments']):
            return "Experimental database"
        
        conn.close()
        return "SQLite database"
        
    except Exception as e:
        logger.error(f"Error checking database type: {str(e)}")
        return None
