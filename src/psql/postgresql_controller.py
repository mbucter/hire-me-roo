import os
import psycopg
import pandas as pd
from dotenv import load_dotenv

from src.utils.logger import get_logger


class PostgreSQLController:
    """
    Controller class to handle input/output from PostgreSQL DB.
    """
    def __init__(self):
        load_dotenv()
        self.logger = get_logger(__name__)
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()
        self.logger.info(f"PostgreSQL controller initialized.")

    def get_conn(self):
        """
        Get DB connection object from local .env file.
        :return:
        """
        return psycopg.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
        )

    def create_schema(self, schema_name):
        """
        Create schema in PostgreSQL DB.
        :param schema_name: String of schema name.
        :return:
        """
        create_schema_cmd = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        self.logger.info(f"Running command: {create_schema_cmd}")
        self.cursor.execute(create_schema_cmd)
        self.conn.commit()

    def create_sql_table(self, schema_dict: dict):
        """
        Create table in PostgreSQL DB.
        :param schema_dict: Dictionary containing schema info.
        :return:
        """
        schema_name = schema_dict['schema']
        self.create_schema(schema_name)
        table_name = schema_dict['table_name']
        columns = schema_dict['columns']
        primary_key = schema_dict.get('primary_key', [])

        col_defs = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if "default" in col:
                col_def += f" DEFAULT {col['default']}"
            col_defs.append(col_def)

        if primary_key:
            pk = ",".join(primary_key)
            col_defs.append(f"PRIMARY KEY({pk})")

        sql = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
        {', '.join(col_defs)}
        );
        """

        self.logger.info(f"Running command: {sql}")
        self.cursor.execute(sql)
        self.conn.commit()

    def convert_pd_col_to_psql_col(self, pd_col_name: str):
        """
        Helper function to convert pandas column name to psql column name.
        :param pd_col_name: String of pandas column name.
        :return: String of psql column name.
        """
        psql_col_name = ""
        for char in pd_col_name:
            if char.isupper():
                psql_col_name += f"_{char.lower()}"
            else:
                psql_col_name += char

        return psql_col_name

    def insert_df_into_table(self, df: pd.DataFrame, table_name: str, prim_key_names: list, schema_name: str = ""):
        """
        Insert pandas dataframe into table in PostgreSQL DB.
        :param df: Pandas dataframe.
        :param table_name: String of table name.
        :param prim_key_names: List of primary key column names.
        :param schema_name: String of schema name.
        :return:
        """
        if schema_name:
            table_name = f"{schema_name}.{table_name}"
        df = df.astype(object).where(pd.notnull(df), None)
        df = df.replace("", None)
        data = df.values.tolist()
        df_col_list = list(df.columns)
        psql_col_list = [self.convert_pd_col_to_psql_col(col) for col in df_col_list]
        psql_col_names = ", ".join(psql_col_list)
        values_reg = ", ".join(['%s']*len(psql_col_list))
        prim_key_tup_str = ", ".join(prim_key_names)

        sql = f"""
        INSERT INTO {table_name} ({psql_col_names})
        VALUES ({values_reg})
        ON CONFLICT ({prim_key_tup_str}) DO NOTHING;
        """
        try:
            self.logger.info(f"Running command: {sql}")
            self.cursor.executemany(sql, data)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error while running command ({sql}): {e}")
            self.conn.rollback()
            raise
