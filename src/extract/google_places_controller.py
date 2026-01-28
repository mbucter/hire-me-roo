import os
import json
import requests
from time import sleep

from utils.logger import get_logger
from request_constants import VET_PLACE_FIELDS, RATE_LIMIT


class GooglePlacesController:
	"""
	Controller class to handle Google Places API requests.
	"""
	def __init__(self):
		self.logger = get_logger(__name__)
		self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
		self.api_url = "https://places.googleapis.com/v1/places:searchText"

	def build_request_headers(self, field_mask_tup: tuple[str]):
		"""
		Build Google Places API request headers.

		:param field_mask_tup: Tuple of strings to dictate response values.
		:return: Header dict.
		"""

		field_mask_str = ",".join(field_mask_tup)
		headers = {
			"Content-Type": "application/json",
			"X-Goog-Api-Key": self.api_key,
			"X-Goog-FieldMask": field_mask_str,
		}

		return headers

	def build_google_places_request(self, field_mask: tuple[str], text_query: str):
		"""
		Build Google Places API request.

		:param field_mask: Tuple of strings to dictate response values.
		:param text_query: String of query to send to Google Places API.
		:return: Dict formatted response.
		"""

		payload = {"textQuery": text_query}
		self.logger.debug(f"Google Places API payload: {payload}")
		headers = self.build_request_headers(field_mask)
		self.logger.debug(f"Google Places API headers: {headers}")
		self.logger.info(f"Sending request to {self.api_url}")
		response = requests.post(
			self.api_url,
			headers=headers,
			json=payload,
		)
		data = response.json()
		self.logger.debug(f"Google Places API response: {data}")

		return data

	def save_output_as_json(self, data: dict, output_path: str):
		"""
		Save Google Places API response to local JSON.
		:param data: Dict formatted response.
		:param output_path: String path to save JSON response.
		:return:
		"""
		with open(output_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
			self.logger.info(f"Saved JSON output to {output_path}")


if __name__ == "__main__":
	controller = GooglePlacesController()
	city_list = [
		"Sacramento, CA",
	]
	for city in city_list:
		data = controller.build_google_places_request(VET_PLACE_FIELDS, f"veterinary clinics in {city}")
		city_str = city.replace(" ", "_").replace(",","").lower()
		controller.save_output_as_json(data, output_path=f"google_place_query_output_{city_str}.json")
		sleep(RATE_LIMIT)
