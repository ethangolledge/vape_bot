import duckdb
import pandas as pd
from bot.models import SetupManager

class DuckDBManager:
    def __init__(self, db_path: str = "vape_tracking.db"):
        self.conn = duckdb.connect(database=db_path)
        self._initialise_tables()

    def _initialise_tables(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_setups (
                user_id INTEGER PRIMARY KEY,
                tokes INTEGER,
                strength INTEGER,
                method VARCHAR,
                reduce_amount INTEGER,
                reduce_percent FLOAT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def insert_setup(self, user_id: int, setup: SetupManager) -> None:
        """insert setup data into user_setups table"""
        try:
            df = pd.DataFrame([setup.to_dict(user_id)])
            self.conn.execute("""
                INSERT OR REPLACE INTO user_setups 
                SELECT * FROM df
            """)
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to insert setup data: {str(e)}")