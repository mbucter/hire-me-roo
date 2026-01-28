import os
import argparse
import yaml
from pathlib import Path

from psql.postgresql_controller import PostgreSQLController


BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_DIR = BASE_DIR / "src/psql/schemas"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema",
        type=str,
        required=True,
        help="Schema name.",
    )

    return parser.parse_args()

def main():
    args = parse_args()
    controller = PostgreSQLController()
    schema_path = os.path.join(SCHEMA_DIR, f"{args.schema}.yaml")
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    controller.create_sql_table(schema)

if __name__ == "__main__":
    main()