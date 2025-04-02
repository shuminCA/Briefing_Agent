import streamlit as st
import json
import copy
import logging
from pyarrow import null
import os
from dotenv import load_dotenv

from ResponseHandler import ResponseHandler
from UIComponents import UIComponents
from APIHandler import APIHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API configuration from environment variables
API_URL = os.getenv("API_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not API_URL or not BEARER_TOKEN:
    logger.error(".env file not found or missing required variables. Please create it from .env.example")
    st.error("Environment configuration missing. Please create .env file from .env.example")

# Initialize API handler
api_handler = APIHandler(API_URL, BEARER_TOKEN)


def initialize_session_state():
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = True
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_response" not in st.session_state:
        st.session_state.current_response = None
    if "current_handler" not in st.session_state:
        st.session_state.current_handler = None
    if "showing_resume_request" not in st.session_state:
        st.session_state.showing_resume_request = False
    if "selected_approvals" not in st.session_state:
        st.session_state.selected_approvals = {}
    if "approval_metadata" not in st.session_state:
        st.session_state.approval_metadata = {}
    if "reviewer_id" not in st.session_state:
        st.session_state.reviewer_id = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "show_login" not in st.session_state:
        st.session_state.show_login = False
    if "show_login_form" not in st.session_state:
        st.session_state.show_login_form = False
    if "request_history" not in st.session_state:
        st.session_state.request_history = []
    if "processed_requests" not in st.session_state:
        st.session_state.processed_requests = set()


def make_api_request(data):
    """
    Make a request to the API using the APIHandler.

    :param data: The data to send to the API
    :return: The API response as JSON, or None if the request failed
    """
    return api_handler.make_request(data)


def process_response(api_response):
    """
    Process the API response and handle flattened_approval_info.

    :param api_response: Response from the API
    :return: Processed response content for display
    """
    if not api_response:
        return None

    # Create response handler
    handler = ResponseHandler(api_response)
    st.session_state.current_handler = handler
    st.session_state.current_response = api_response

    # Check if flattened_approval_info exists and is not empty
    if "flattened_approval_info" in api_response[0] and api_response[0]["flattened_approval_info"]:
        # Check if there are any items with tool_call not null or status_info not null
        has_items_to_display = False
        for item in api_response[0]["flattened_approval_info"]:
            if item.get("tool_call") is not None or item.get("status_info"):
                has_items_to_display = True
                break

        if has_items_to_display:
            st.session_state.showing_resume_request = True
            st.rerun()

    # If flattened_approval_info is empty or doesn't exist, display the last message content
    st.session_state.showing_resume_request = False

    # Extract content from the last assistant message
    response_content = "Process completed successfully."
    if "messages" in api_response[0] and api_response[0]["messages"]:
        for msg in reversed(api_response[0]["messages"]):
            if msg.get("role") == "assistant" and "content" in msg and msg["content"] is not None:
                response_content = msg["content"]
                break

    return response_content


def display_chat_messages():
    """
    Display chat messages or welcome message.
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def display_sidebar_content():
    """
    Display sidebar content including login and request history.
    """
    with st.sidebar:
        # Display login in the sidebar
        UIComponents.sidebar_login()

        # Add a separator
        st.markdown("---")

        # Display request history in the sidebar
        UIComponents.display_request_history()


def handle_resume_requests():
    """
    Handle resume requests if in resume request mode.
    """
    if st.session_state.showing_resume_request and st.session_state.current_handler:
        UIComponents.display_resume_request_interface(st.session_state.current_handler, make_api_request)


def handle_chat_input():
    """
    Handle chat input from the user.
    """
    if prompt := st.chat_input("What's on your mind?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Format the request with messages array
        request_data = {"prompt": prompt}

        api_response = make_api_request(request_data)

        if api_response:
            # Process and display the response
            processed_response = process_response(api_response)

            # Only add to chat history if there's a response message and not showing resume request
            if processed_response and not st.session_state.showing_resume_request:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": processed_response
                })

                # Display assistant response
                with st.chat_message("assistant"):
                    st.write(processed_response)


def main():
    """
    Main function to run the HR Agent application.
    """
    st.title("🎯 Welcome to BriefMe Brilliantly!")

    initialize_session_state()

    # Display sidebar content
    display_sidebar_content()

    # Display welcome message
    if st.session_state["show_welcome"]:
        UIComponents.display_welcome()
        return
    # Display chat message
    display_chat_messages()
    # Handle resume requests
    handle_resume_requests()
    # Handle chat input
    handle_chat_input()


if __name__ == "__main__":
    main()