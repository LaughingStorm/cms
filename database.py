from sqlalchemy import create_engine, text

class Database:
    def __init__(self, url):
        # sqlite:///portfolio.db
        self.engine = create_engine(url, connect_args={"check_same_thread": False})
    
    def execute(self, query, *args):
        """Execute a query, mimicking cs50.SQL behavior"""
        with self.engine.begin() as connection:
            # Replace ? placeholders with :1, :2, etc for SQLAlchemy
            params = {str(i): arg for i, arg in enumerate(args)}
            prepared = query
            for i in range(len(args)):
                prepared = prepared.replace("?", f":{i}", 1)
            
            result = connection.execute(text(prepared), params)
            
            # SELECT: Return list of dicts
            if result.returns_rows:
                return [dict(row._mapping) for row in result.all()]
            
            # INSERT: Return last inserted ID
            query_upper = query.strip().upper()
            if query_upper.startswith("INSERT"):
                res = connection.execute(text("SELECT last_insert_rowid()"))
                return res.scalar()
            
            # UPDATE/DELETE: Return rows affected
            return result.rowcount