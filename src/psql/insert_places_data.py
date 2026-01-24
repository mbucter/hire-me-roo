import os
from pathlib import Path

from transform.convert_places_json_tabular import ConvertPlacesJSONTabular
from psql.postgresql_controller import PostgreSQLController


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def main():
    controller = PostgreSQLController()
    google_place_json_list = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR) if file.endswith(".json")]
    for json_file in google_place_json_list:
        converter = ConvertPlacesJSONTabular(json_file)
        places_df, places_reviews_df = converter.convert_json_to_df()
        controller.insert_df_into_table(
            places_df,
            table_name='places',
            prim_key_names=['place_id'],
            schema_name='raw',
        )
        controller.insert_df_into_table(
            places_reviews_df,
            table_name='places_reviews',
            prim_key_names=['review_id'],
            schema_name='raw',
        )


if __name__ == "__main__":
    main()