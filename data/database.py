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
        """Insert or update data in user_setups using Arrow and CTE logic"""
        try:
            logging.debug(f"Inserting setup data: {setup_dict}")

            # Convert dictionary to Arrow table
            setup_table = pa.Table.from_pydict({k: [v] for k, v in setup_dict.items()})
            self.conn.execute('BEGIN TRANSACTION')
            self.conn.register("temp_setup_arrow", setup_table)

            self.conn.execute("""
            WITH existing AS (
                SELECT user_id FROM user_setups WHERE user_id IN (SELECT user_id FROM temp_setup_arrow)
            )
            INSERT INTO user_setups (user_id, tokes, strength, method, reduce_amount, reduce_percent, created_at, updated_at)
            SELECT
                source.user_id,
                source.tokes,
                source.strength,
                source.method,
                source.reduce_amount,
                source.reduce_percent,
                source.created_at,
                source.updated_at
            FROM temp_setup_arrow AS source
            WHERE source.user_id NOT IN (SELECT user_id FROM existing);

            UPDATE user_setups
            SET
                tokes = source.tokes,
                strength = source.strength,
                method = source.method,
                reduce_amount = source.reduce_amount,
                reduce_percent = source.reduce_percent,
                updated_at = source.updated_at
            FROM temp_setup_arrow AS source
            WHERE user_setups.user_id = source.user_id;
            """)

            self.conn.unregister("temp_setup_arrow")
            self.conn.execute('COMMIT')

            logging.info(f"Insert/update successful for user {setup_dict['user_id']}")
            return True

        except Exception as e:
            logging.error(f"Insert failed: {str(e)}")
            self.conn.execute('ROLLBACK')
            raise ValueError(f"Failed to insert setup data: {str(e)}")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()