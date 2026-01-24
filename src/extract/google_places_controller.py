import os
import json
import requests
from time import sleep

from request_constants import VET_PLACE_FIELDS, RATE_LIMIT


class GooglePlacesController(object):
	def __init__(self):
		self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
		self.api_url = "https://places.googleapis.com/v1/places:searchText"

	def build_request_headers(self, field_mask_tup: tuple[str]):
		field_mask_str = ",".join(field_mask_tup)
		headers = {
			"Content-Type": "application/json",
			"X-Goog-Api-Key": self.api_key,
			"X-Goog-FieldMask": field_mask_str,
		}

		return headers

	def build_google_places_request(self, field_mask: tuple[str], text_query: str):
		payload = {"textQuery": text_query}
		headers = self.build_request_headers(field_mask)
		response = requests.post(
			self.api_url,
			headers=headers,
			json=payload,
		)
		data = response.json()

		return data

	def save_output_as_json(self, data: dict, output_path: str):
		with open(output_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
	controller = GooglePlacesController()
	city_list = [
		"San Jose, CA",
		"San Francisco, CA",
		"Oakland, CA",
		"Los Angeles, CA",
		"Chicago, IL",
		"Austin, TX",
		"New York City, NY",
		"Portland, OR",
		"Tampa, FL"
	]
	for city in city_list:
		data = controller.build_google_places_request(VET_PLACE_FIELDS, f"veterinary clinics in {city}")
		city_str = city.replace(" ", "_").replace(",","").lower()
		controller.save_output_as_json(data, output_path=f"google_place_query_output_{city_str}.json")
		sleep(RATE_LIMIT)
