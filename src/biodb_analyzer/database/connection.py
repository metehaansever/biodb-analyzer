import os
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from pathlib import Path

class DatabaseConnection:
    """
    A class to handle connections to SQLite databases
    """
    def __init__(self, db_path: str):
        """
        Initialize the database connection
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
            
        self.engine: Optional[Engine] = None
        self._connect()

    def _connect(self) -> None:
        """
        Create a connection to the SQLite database
        """
        try:
            self.engine = create_engine(f'sqlite:///{self.db_path}')
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
            params: Optional dictionary of parameters for the query
            
        Returns:
            pandas DataFrame containing query results
        """
        if not self.engine:
            raise ConnectionError("Database connection not established")
            
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params if params else {})
                return pd.DataFrame(result.fetchall(), columns=result.keys())
        except SQLAlchemyError as e:
            raise Exception(f"Error executing query: {str(e)}")

    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database
        
        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self.execute_query(query)['name'].tolist()

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get information about table columns
        
        Args:
            table_name: Name of the table to get info about
            
        Returns:
            DataFrame with column information
        """
        query = f"PRAGMA table_info({table_name});"
        return self.execute_query(query)

    def close(self) -> None:
        """
        Close the database connection
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
