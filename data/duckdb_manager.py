import duckdb

class DuckDBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path)
    
    def create_table(self, table_name: str, schema:str):
        if self.connection is None:
            self.connect()

        create_user_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({schema})'
        print(f"Executing query: {create_user_table_query}")
        self.connection.execute(create_user_table_query)
        #  probs have a commit here

    def insert_data(self, table_name: str, data: dict):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])

        insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        print(f"Executing query: {insert_query}")
        self.connection.execute(insert_query, tuple(data.values()))
        # probs have a commit here

    def query(self, query: str):
        if self.connection is None:
            self.connect()

        print(f"Executing query: {query}")
        result = self.connection.execute(query).fetchall()
        return result

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            print("Connection closed.")

import duckdb

class DuckDBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path)
    
    def create_table(self, table_name: str, schema:str):
        if self.connection is None:
            self.connect()

        create_user_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({schema})'
        print(f"Executing query: {create_user_table_query}")
        self.connection.execute(create_user_table_query)
        #  probs have a commit here

    def insert_data(self, table_name: str, data: dict):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])

        insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        print(f"Executing query: {insert_query}")
        self.connection.execute(insert_query, tuple(data.values()))
        # probs have a commit here

    def query(self, query: str):
        if self.connection is None:
            self.connect()

        print(f"Executing query: {query}")
        result = self.connection.execute(query).fetchall()
        return result

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            print("Connection closed.")

if __name__ == "__main__":
    db_manager = DuckDBManager(r"/home/ethan/code/venv/vape_bot/data/database.duckdb")
    
    select_statement = "SELECT * FROM user_setup"
    result = db_manager.query(select_statement)
    
    print(f"Query result: {result}")  # <-- ADD THIS LINE!
    print(f"Number of rows: {len(result)}")  # <-- AND THIS ONE!
    
    db_manager.close()