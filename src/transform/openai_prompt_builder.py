import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from openai_prompt_dicts import PROMPT_DICT
from src.utils.logger import get_logger


class OpenAIPrompt:
    """
    Class to handle OpenAI prompts.
    """
    def __init__(self, prompt_type, version=None):
        self.logger = get_logger(__name__)
        load_dotenv()
        self.prompt_type = prompt_type
        self.version = version
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger.info(f"OpenAIPrompt initialized -- prompt_type: {self.prompt_type}; version: {self.version}")

        self.prompt_dict = self.get_prompt_from_version()

    def get_prompt_from_version(self):
        """
        Get prompt dict from version or latest version if not passed..
        :return: Prompt dict.
        """
        prompt_list = PROMPT_DICT[self.prompt_type]
        if not self.version:
            prompt_dict = max(prompt_list, key=lambda x: x["version"])

        else:
            prompt_dict = next((d for d in prompt_list if d["version"] == self.version), None)

        return prompt_dict

    def parse_json_output(self, text: str) -> dict:
        text = text.strip()
        return json.loads(text)

    def request(self, records):
        """
        Method to handle OpenAI prompts.
        :param records: List of dicts; records pulled from SQL table.
        :return: Response from OpenAI.
        """
        self.prompt_dict['content']['records'] = records
        temperature = self.prompt_dict['temperature']
        top_p = self.prompt_dict['top_p']
        model = self.prompt_dict['model']
        content = json.dumps(self.prompt_dict['content'])
        input_list = [
            {
                "role": "system",
                "content": "You output only valid JSON that matches the output_schema."
            },
            {
                "role": "user",
                "content": content
            }
        ]

        self.logger.info(f"Sending request OpenAI request...")
        response = self.client.responses.create(
            model=model,
            input=input_list,
            temperature=temperature,
            top_p=top_p,
        )

        output_text = response.output_text
        try:
            data = self.parse_json_output(output_text)
            self.logger.info(f"OpenAIPrompt result received successfully.")
        except Exception as e:
            self.logger.error(f"OpenAIPrompt request failed with exception: {e}")
            data = {}

        return data
