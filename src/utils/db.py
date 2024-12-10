import pandas as pd
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class MSSql:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def __enter__(self):
        session.Session = sessionmaker()
        engine = create_engine(self.connection_string.strip(), fast_executemany = True)
        session.Session.configure(bind = engine)
        self.session, self.engine = session.Session(), engine
        return self

    def __exit__(self, _type, value, traceback):
        self.session.commit()
        self.session.close()

class DB:
    @staticmethod
    def statement_call(connection_string: str, query: str):
        with MSSql(connection_string) as db:
            try:
                db.session.connection()
                db.session.execute(text(query))
            except Exception as e:
                raise e

    @staticMethod
    def query_with_return_df(connection_string: str, query: str):
        with MSSql(connection_string) as db:
            try:
                connection = db.session.connection()
                return pd.read_sql_query(query, connection)
            except Exception as e:
                raise e
