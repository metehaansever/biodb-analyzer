import os
import pytest
import sqlite3
from biodb_analyzer.database.connection import DatabaseConnection

def create_test_db(db_path):
    """Create a test SQLite database with sample data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table1 (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table2 (
            id INTEGER PRIMARY KEY,
            table1_id INTEGER,
            description TEXT,
            FOREIGN KEY (table1_id) REFERENCES test_table1(id)
        )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT INTO test_table1 (name, value) VALUES ('test1', 100)")
    cursor.execute("INSERT INTO test_table1 (name, value) VALUES ('test2', 200)")
    cursor.execute("INSERT INTO test_table2 (table1_id, description) VALUES (1, 'description1')")
    cursor.execute("INSERT INTO test_table2 (table1_id, description) VALUES (2, 'description2')")
    
    conn.commit()
    conn.close()

def remove_test_db(db_path):
    """Remove the test database file"""
    if os.path.exists(db_path):
        os.remove(db_path)

def test_connection():
    """Test database connection"""
    test_db = "test_database.db"
    create_test_db(test_db)
    
    try:
        with DatabaseConnection(test_db) as conn:
            assert conn is not None
            assert isinstance(conn, DatabaseConnection)
            
            # Test getting table names
            tables = conn.get_table_names()
            assert len(tables) == 2
            assert 'test_table1' in tables
            assert 'test_table2' in tables
            
            # Test getting table info
            info = conn.get_table_info('test_table1')
            assert not info.empty
            assert 'id' in info['name'].values
            assert 'name' in info['name'].values
            
            # Test executing query
            result = conn.execute_query("SELECT * FROM test_table1")
            assert not result.empty
            assert len(result) == 2
    finally:
        remove_test_db(test_db)

def test_invalid_connection():
    """Test connection with invalid database path"""
    with pytest.raises(Exception):
        DatabaseConnection("nonexistent.db")

if __name__ == "__main__":
    pytest.main([__file__])
