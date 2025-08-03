
import sys
from pathlib import Path

# Add the vape_bot directory to Python path
project_root = Path(__file__).parent.parent  # Goes up to vape_bot directory
sys.path.insert(0, str(project_root))

from data.duckdb_manager import DuckDBManager

class DataTransfer:
    def __init__(self, pk: str, data: dict):
        self.data = data
        self.pk = pk  # This is the user_id (session.uid)
        self.db_path = r"/home/ethan/code/venv/vape_bot/data/database.duckdb"
        self.db_manager = DuckDBManager(self.db_path)

    def convert_types(self, row: dict) -> dict:
        """Convert string values to proper types"""
        converted = row.copy()
        
        # Convert integers
        for field in ['user_id', 'tokes', 'goal']:
            if field in converted:
                converted[field] = int(converted[field])
        
        # Convert datetime strings
        for field in ['created_at', 'updated_at']:
            if field in converted:
                # Remove the 'T' and microseconds for DuckDB
                datetime_str = converted[field]
                if 'T' in datetime_str:
                    converted[field] = datetime_str.replace('T', ' ').split('.')[0]
        
        return converted

    def parse_JSON(self): 
        """Yield (key, value) pairs from nested JSON."""
        try:
            for key, value in self.data.items():
                yield key, value
        except Exception as e:
            print(f"Error parsing JSON: {e}")

    def row_generator(self):
        """Yield flattened rows with primary key injected."""
        try:
            if self.data:
                row = {"user_id": self.pk}
                row.update(self.data)
                
                # Convert types before yielding
                converted_row = self.convert_types(row)
                yield converted_row
            else:
                print("No data to generate rows from.")
        except Exception as e:
            print(f"Error generating rows: {e}")

    def transfer_data(self, table_name: str):
        """Transfer data to the DuckDB table."""
        try:
            self.db_manager.connect()
            for row in self.row_generator():
                if row:
                    print(f"Inserting row: {row}")
                    self.db_manager.insert_data(table_name, row)
                else:
                    print("Empty row, skipping insertion.")
            self.db_manager.close()

        except Exception as e:
            print(f"Error transferring data: {e}")
            self.db_manager.close()