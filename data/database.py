import duckdb
import logging
import os
from typing import Dict

class DuckDBManager:
    """anages DuckDB database operations"""

    def __init__(self, db_path: str = 'vape_tracking.db'):
        """Initialize database connection and tables"""
        self.db_name = 'vape_tracking.db'
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # FINISH
        self.db_path = db_path
        self.conn = duckdb.connect(database=db_path)
        self._initialise_tables()

    def _get_table_schemas(self) -> Dict[str, str]:
        """define the database schema for all tables, this will grow with time and ensures tables are created if missing"""
        return {
            'user_setups': """
            CREATE TABLE IF NOT EXISTS user_setups (
                user_id BIGINT PRIMARY KEY,
                tokes INTEGER,
                strength INTEGER,
                method VARCHAR,
                reduce_amount INTEGER,
                reduce_percent FLOAT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )"""
        }

    def _initialise_tables(self) -> None:
        """initialise all database tables in a single transaction"""
        try:
            self.conn.execute('BEGIN TRANSACTION')
            for table_name, schema in self._get_table_schemas().items():
                self.conn.execute(schema)
            self.conn.execute('COMMIT')
        except Exception as e:
            self.conn.execute('ROLLBACK')
            raise RuntimeError(f"Failed to initialise tables: {str(e)}")

    def insert_setup(self, setup_dict: dict) -> None:
        """insert into the user_setups table, expects a dict matching the table schema"""
        try:
            logging.debug(f"Inserting setup data: {setup_dict}")
            
            self.conn.execute("""
                INSERT OR REPLACE INTO user_setups 
                SELECT * FROM dict_to_table($1)
            """, [setup_dict])
            
            self.conn.commit()
            logging.info(f"Insert successful for user {setup_dict['user_id']}")

        except Exception as e:
            logging.error(f"Insert failed: {str(e)}")
            self.conn.rollback()
            raise ValueError(f"Failed to insert setup data: {str(e)}")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()