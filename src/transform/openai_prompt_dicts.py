PROMPT_DICT = {
    "availability_sentiment_prompt":
        [
            {
                "version": "0.1.0",
                "name": "availability_sentiment_prompt",
                "temperature": 0.1,
                "top_p": 1.0,
                "model": "gpt-4.1-mini",
                "content": {
                    "task_description": "You are a sentiment analysis agent tasked with parsing whether a veterinary clinic 'review_text' mentions appointment availability and if so, the sentiment regarding appointment availability.",
                    "rules": [
                        "Analyze each 'review_text' independently.",
                        "Return only a JSON object as specified below by: 'output_schema' (types denoted in brackets {}).",
                        "'records' contains a list of dictionaries containing 'idx' (index) and 'review_text' (review text to be analyzed).",
                        "Maintain the pairing of 'idx' and 'review_text'",
                        "If 'appointment_availability_mention' is true, 'sentiment_score' should be a single integer value between 1 and 5: assessing the sentiment of appointment availability (1 being negative, 5 being positive).",
                        "If 'appointment_availability_mention' is false, 'sentiment_score' should be null.",
                        "Provide 'evidence' only if appointment_availability_mention is true (otherwise null); explains why the sentiment_score was given; limited to 100 characters."
                    ],
                    "records": [],
                    "output_schema": {
                        "results": [
                            {
                                "idx": "{integer}",
                                "review_id": "{string}",
                                "appointment_availability_mention": "{boolean}",
                                "sentiment_score": "{integer|null}",
                                "evidence": "{string|null}"
                            }
                        ]
                    }
                }
            }
        ]
}

