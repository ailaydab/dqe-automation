import pandas as pd
import psycopg2

class PostgresConnectorContextManager:
    def __init__(self, db_host: "localhost", db_name: "mydatabase",db_user: "myuser", db_password: "ilayda-ada", db_port: 5432):
        self.db_host = db_host
        self.db_name = db_name
        self.user = db_user
        self.password = db_password
        self.port = db_port
        self.conn = None

    def __enter__(self):
        # create conn
        self.conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def __exit__(self):
        # close conn
        if self.conn:
            self.conn.close()

    def get_data_sql(self, sql):
        # exec query, result = pandas df
        df = pd.read_sql(sql, self.conn)
        return df

