import duckdb
import logging
import os
import pyarrow as pa
from typing import Dict

class DuckDBManager:
    """manages DuckDB database operations"""

    def __init__(self, db_path: str = None) -> None:
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'vape_tracking.duckdb')
        
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


    def insert_setup(self, setup_dict: dict) -> bool:
        """Insert dictionary data into user_setups using Arrow"""
        try:
            logging.debug(f"Inserting setup data: {setup_dict}")

            setup_table = pa.Table.from_pylist([setup_dict])

            self.conn.execute('BEGIN TRANSACTION')

            self.conn.register("temp_arrow_data", setup_table)

            self.conn.execute("""
                INSERT OR REPLACE INTO user_setups
                SELECT * FROM temp_arrow_data
            """)

            self.conn.unregister("temp_arrow_data")
            self.conn.execute('COMMIT')

            logging.info(f"Insert successful for user {setup_dict['user_id']}")
            return True

        except Exception as e:
            logging.error(f"Insert failed: {str(e)}")
            self.conn.execute('ROLLBACK')
            raise ValueError(f"Failed to insert setup data: {str(e)}")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()