import requests
import logging
import streamlit as st

# Configure logging
logger = logging.getLogger(__name__)


class APIHandler:
    """
    Handles API requests and responses for the HR Agent application.
    """

    def __init__(self, api_url, bearer_token):
        """
        Initialize the APIHandler with API configuration.

        :param api_url: The URL of the API endpoint
        :param bearer_token: The bearer token for authentication
        """
        self.api_url = api_url
        self.bearer_token = bearer_token

    def make_request(self, data):
        """
        Make a request to the API.

        :param data: The data to send to the API
        :return: The API response as JSON, or None if the request failed
        """
        # Uncomment to use mock data for testing
        # return self._mock_response(data)
        #
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        try:
            with st.spinner("Processing your request..."):
                response = requests.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.info(f"API request: {data}")
            st.error(f"API Error: {str(e)}")
            return None

    def _mock_response(self, data):
        """
        Return mock response data for testing.

        :param data: The request data
        :return: Mock response data
        """
        # Example mock implementation
        import json
        with open("v2/data/response1.json", "r") as file:
            return json.load(file)