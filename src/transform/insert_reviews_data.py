import uuid
import logging
import pandas as pd

from src.utils.logger import get_logger
from psql.postgresql_controller import PostgreSQLController
from openai_prompt_builder import OpenAIPrompt


logger = get_logger(__name__, level=logging.INFO)
PROMPT_TYPE = "availability_sentiment_prompt"


def process_batch_rows(batch_size=10):
    llm_run_id = str(uuid.uuid4())
    psql_controller = PostgreSQLController()
    processed_count = 0
    with psql_controller.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw.places_reviews;")
        total_row_count = cur.fetchone()[0]
    query = f"SELECT review_id, review_text FROM raw.places_reviews ORDER BY review_id;"
    with psql_controller.conn.cursor() as read_cur:
        read_cur.execute(query)

        while True:
            records = read_cur.fetchmany(batch_size)
            records_dicts = [{"idx": i, "review_id": rid, "review_text": text} for i, (rid, text) in enumerate(records)]
            idx_to_review_id = {r["idx"]: r["review_id"] for r in records_dicts}

            if not records:
                break

            review_df_data = []
            review_metadata_df_data = []

            openai_prompt = OpenAIPrompt(prompt_type=PROMPT_TYPE)
            data = openai_prompt.request(records_dicts)

            if not data:
                continue

            for result in data['results']:
                review_data_row = {}
                review_metadata_row = {}

                review_data_row['review_id'] = idx_to_review_id[result["idx"]]
                review_data_row['llm_run_id'] = llm_run_id
                review_data_row['prompt_name'] = openai_prompt.prompt_dict['name']
                review_data_row['prompt_subject_exists'] = result.get("appointment_availability_mention", False)
                review_data_row['sentiment_score'] = result.get("sentiment_score", None)
                review_data_row['evidence'] = result.get("evidence", "")
                review_df_data.append(review_data_row)

                review_metadata_row['llm_run_id'] = llm_run_id
                review_metadata_row['prompt_name'] = openai_prompt.prompt_dict['name']
                review_metadata_row['model'] = openai_prompt.prompt_dict['model']
                review_metadata_row['prompt_version'] = openai_prompt.prompt_dict['version']
                review_metadata_row['temperature'] = openai_prompt.prompt_dict['temperature']
                review_metadata_row['top_p'] = openai_prompt.prompt_dict['top_p']
                review_metadata_df_data.append(review_metadata_row)

            review_df = pd.DataFrame(review_df_data)
            review_metadata_df = pd.DataFrame(review_metadata_df_data)

            psql_controller.insert_df_into_table(
                df=review_df,
                table_name="review_sentiment",
                prim_key_names = ['review_id', 'llm_run_id', 'prompt_name'],
                schema_name="llm"
            )
            psql_controller.insert_df_into_table(
                df=review_metadata_df,
                table_name="review_sentiment_meta",
                prim_key_names=['llm_run_id', 'prompt_name'],
                schema_name="llm"
            )

            processed_count += batch_size
            logger.info(f"Processed {round(100*processed_count/total_row_count, 2)}% of rows.")



def main():
    process_batch_rows()


if __name__ == "__main__":
    main()