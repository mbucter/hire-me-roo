import os
import psycopg
import yaml
import pandas as pd
from dotenv import load_dotenv


class PostgreSQLController:
    def __init__(self):
        load_dotenv()
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()

    def get_conn(self):
        return psycopg.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
        )

    def create_schema(self, schema_name):
        self.cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name};')
        self.conn.commit()

    def create_sql_table(self, schema_dict: dict):
        schema_name = schema_dict['schema']
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

        self.cursor.execute(sql)
        self.conn.commit()

    def convert_pd_col_to_psql_col(self, pd_col_name: str):
        psql_col_name = ""
        for char in pd_col_name:
            if char.isupper():
                psql_col_name += f"_{char.lower()}"
            else:
                psql_col_name += char

        return psql_col_name

    def insert_df_into_table(self, df: pd.DataFrame, table_name: str, prim_key_names: list, schema_name: str = ""):
        if schema_name:
            table_name = f"{schema_name}.{table_name}"
        df = df.where(pd.notnull(df), None)
        df = df.replace("", None)
        data = list(df.itertuples(index=False, name=None))
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
            self.cursor.executemany(sql, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise


if __name__ == "__main__":
    controller = PostgreSQLController()
    schema_path = r"/Users/mattbucter/git/hire-me-roo/src/psql/schemas/places_reviews.yaml"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    controller.create_sql_table(schema)
    print("Done.")
