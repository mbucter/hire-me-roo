import os
import json
import pandas as pd

from utils.logger import get_logger


class ConvertPlacesJSONTabular:
    """
    Class to handle converting Google Places JSON data into tabular format.
    """
    def __init__(self, input_json):
        self.logger = get_logger(__name__)
        self.input_json = input_json
        self.json_data = self.load_json()

    def load_json(self):
        """
        Load local JSON file.
        :return: Dictionary of JSON data.
        """
        if type(self.input_json) is str and os.path.exists(self.input_json):
            with open(self.input_json, "r") as f:
                json_data = json.load(f)
            return json_data

    def convert_one_place(self, place_dict):
        """
        Convert one Google Place from dict to pandas row format.
        :param place_dict: Input dict.
        :return: Output dict (formatted for pandas).
        """
        data_row = {}
        data_row['place_id'] = place_dict.get('id', '')
        data_row['latitude'] = place_dict.get('location', {}).get('latitude', '')
        data_row['longitude'] = place_dict.get('location', {}).get('longitude', '')
        data_row['rating'] = place_dict.get('rating', '')
        data_row['website_uri'] = place_dict.get('websiteUri', '')
        data_row['business_status'] = place_dict.get('businessStatus', '')
        data_row['user_rating_count'] = place_dict.get('userRatingCount', '')
        data_row['display_name'] = place_dict.get('displayName', {}).get('text', '')
        data_row['user_review_count'] = len(place_dict.get('reviews', []))

        return data_row

    def convert_one_place_reviews(self, place_dict):
        """
        Convert one Google Place reviews from dict to pandas row format.
        :param place_dict: Input dict.
        :return: List of output dicts (formatted for pandas).
        """
        data = []
        if not "reviews" in place_dict:
            return data
        for review in place_dict.get('reviews', []):
            data_row = {}
            data_row['place_id'] = place_dict.get('id', '')
            data_row['review_id'] = review.get('name', '')
            data_row['review_rating'] = review.get('rating', None)
            data_row['review_text'] = review.get('text', {}).get('text', '')
            data_row['review_language_code'] = review.get('text', {}).get('languageCode', '')
            data_row['author_display_name'] = review.get('authorAttribution', {}).get('displayName', '')
            data_row['author_uri'] = review.get('authorAttribution', {}).get('uri', '')
            data_row['review_publish_time'] = review.get('publishTime', '')
            data.append(data_row)

        return data

    def convert_json_to_df(self):
        """
        Convert Google Place JSON data into pandas dataframe.
        :return: Two pandas dataframes for places and reviews.
        """
        places_list = self.json_data['places']
        places_data = []
        place_reviews_data = []
        for place_dict in places_list:
            places_row = self.convert_one_place(place_dict)
            if places_row:
                places_data.append(places_row)
            place_reviews_rows = self.convert_one_place_reviews(place_dict)
            if place_reviews_rows:
                place_reviews_data.extend(place_reviews_rows)

        places_df = pd.DataFrame(places_data)
        places_reviews_df = pd.DataFrame(place_reviews_data)

        return places_df, places_reviews_df


if __name__ == "__main__":
    converter = ConvertPlacesJSONTabular(input_json="/Users/mattbucter/git/hire-me-roo/data/google_place_query_output_san_jose_ca.json")
    places_df, places_reviews_df = converter.convert_json_to_df()
    places_df.to_csv("places_df.csv", index=False)
    places_reviews_df.to_csv("places_reviews_df.csv", index=False)





