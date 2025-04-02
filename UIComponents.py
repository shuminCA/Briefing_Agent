import streamlit as st
import datetime


class UIComponents:
    """
    UI components for the HR Agent application.
    Contains functions for rendering various UI elements.
    """

    @staticmethod
    def sidebar_login():
        # Initialize show_login_form in session state if it doesn't exist
        if "show_login_form" not in st.session_state:
            st.session_state.show_login_form = False

        # Display login status and user info
        if st.session_state.logged_in:
            st.sidebar.markdown(f"### 👤 {st.session_state.reviewer_id}")
            if st.sidebar.button("Logout", key="sidebar_logout"):
                st.session_state.reviewer_id = ""
                st.session_state.logged_in = False
                st.rerun()
        else:
            # Login button to toggle form visibility
            if st.sidebar.button("👤 Login", key="show_login_button"):
                st.session_state.show_login_form = not st.session_state.show_login_form
                st.rerun()

            # Show login form only if show_login_form is True
            if st.session_state.show_login_form:
                with st.sidebar.container():
                    # Use a form for login
                    with st.form(key="sidebar_login_form", clear_on_submit=False):
                        username = st.text_input("", placeholder="Enter username", key="sidebar_login_username")
                        col1, col2 = st.columns(2)

                        with col1:
                            login_button = st.form_submit_button("Login", use_container_width=True)

                        with col2:
                            cancel_button = st.form_submit_button("Cancel", use_container_width=True)

                    # Handle form submission
                    if login_button and username:
                        st.session_state.reviewer_id = username
                        st.session_state.logged_in = True
                        st.session_state.show_login_form = False
                        st.rerun()
                    elif cancel_button:
                        st.session_state.show_login_form = False
                        st.rerun()

    @staticmethod
    def display_welcome():
        """Display welcome message in the chat area when no messages exist"""
        with open("data/briefing_agent.md", "r", encoding="utf-8") as file:
            welcome_md = file.read()
            st.markdown(welcome_md)

        if st.button("Let's Get Started!", type="primary"):
            st.session_state.show_welcome = False
            st.rerun()

    @staticmethod
    def display_tool_call(tool_call, index=None):
        tool_call_id = tool_call.get("id", f"unknown_{index if index is not None else ''}")
        function = tool_call.get("function", {})
        function_name = function.get("name", "Unknown Function")
        json_args = function.get("json_arguments", {})
        if function_name == "search":
            query = json_args.get("query")
            st.write("🔍 The Briefing Agent wants to perform an online search using the following query:")
            st.write(f"**{query}**")
        if function_name == "send_email":
            email_address = json_args.get("email_address")
            subject = json_args.get("subject")
            email_content = json_args.get("email_content")
            st.write("📧 The Briefing Agent wants to send an email on your behalf with the following details:")
            st.write(f"**Recipient:** {email_address}")
            st.write(f"**Subject:** {subject}")
            st.write("**Content:**")
            st.write(email_content, unsafe_allow_html=True)
        return tool_call_id, function_name

    @staticmethod
    def display_approval_checkboxes(approval_info):
        """
        Display checkboxes for approving tool calls.

        :param approval_info: List of approval info items
        :return: Tuple of (any_selected, selected_approvals, approval_metadata)
        """
        # Initialize approve_all in session state if it doesn't exist
        if "approve_all" not in st.session_state:
            st.session_state.approve_all = False

        approval_metadata = {}
        status_info = [
            f"**{item.get('status_info', 'No status information available')}**"
            for item in approval_info if item.get("tool_call") is None
        ]
        for status in status_info:
            st.markdown(status)
        if len(status_info) == len(approval_info):
            return True, None

        st.write("**Would you like to review and approve the pending requests to proceed?**")

        for i, item in enumerate(approval_info):
            tool_call = item.get("tool_call", {})
            if tool_call is not None:
                tool_call_id, function_name = UIComponents.display_tool_call(tool_call, i)
                metadata = st.text_input(f"Additional metadata (optional):", key=f"metadata_{tool_call_id}")
                approval_metadata[i] = metadata

        return False, approval_metadata

    @staticmethod
    def process_approvals(handler, approval_info, approval_metadata, make_api_request):
        """
        Process approved tool calls and send to API.

        :param handler: ResponseHandler instance
        :param approval_info: List of approval info items (only items with tool_call)
        :param approval_metadata: Dictionary of approval metadata
        :param make_api_request: Function to make API requests
        :return: New response from API if successful, None otherwise
        """
        # Find the original indices in the flattened_approval_info array
        all_approval_info = handler.flattened_approval_info
        approval_indices = {}

        # Map the indices from the filtered list back to the original list
        for i, item in enumerate(approval_info):
            for j, original_item in enumerate(all_approval_info):
                if original_item.get("tool_call") is not None and item == original_item:
                    approval_indices[i] = j
                    break

        # Process all selected approvals
        for i in range(len(approval_info)):
            metadata_text = None
            metadata = None
            if approval_metadata is not None and i in approval_metadata and approval_metadata[i]:
                metadata_text = approval_metadata[i]
                metadata = {"metadata": metadata_text}

            # Get the original index in the handler's flattened_approval_info
            original_index = approval_indices.get(i, i)

            # Update the approval info in the handler using the original index
            handler.update_approval_info(original_index, True, metadata)

            # Get tool call details
            item = approval_info[i]
            path = " -> ".join(item.get("paths", []))
            tool_call = item.get("tool_call", {})
            if tool_call is None:
                history_item = {
                    "status_info": item.get('status_info', 'No status information available')
                }
                st.session_state.request_history.append(history_item)
                continue
            tool_call_id = tool_call.get("id", f"unknown_{i}")
            function = tool_call.get("function", {})
            function_name = function.get("name", "Unknown Function")
            function_args = function.get("arguments", "{}")
            json_args = function.get("json_arguments", {})

            # Add to processed requests set
            st.session_state.processed_requests.add(tool_call_id)

            # Add to request history with all relevant information
            history_item = {
                "req_id": tool_call_id,
                "path": path,
                "function_name": function_name,
                "function_args": function_args,
                "json_args": json_args,
                "approved": True,
                "reviewer_id": st.session_state.reviewer_id if st.session_state.logged_in else "",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tool_call": tool_call
            }

            if metadata_text:
                history_item["message"] = metadata_text

            st.session_state.request_history.append(history_item)

        # Prepare response for submission
        updated_response = handler.prepare_for_submission()

        # Send updated response back to API
        new_response = make_api_request(updated_response)

        # Reset selected approvals and metadata
        st.session_state.selected_approvals = {}
        st.session_state.approval_metadata = {}
        st.session_state.approve_all = False

        return new_response

    @staticmethod
    def handle_new_response(new_response):
        """
        Handle the new response from the API after processing approvals.

        :param new_response: New response from API
        :return: Response content if available, None otherwise
        """
        if not new_response:
            return None

        # Check if the new response has more requests to approve
        has_more_requests = False
        if "flattened_approval_info" in new_response[0] and new_response[0]["flattened_approval_info"]:
            # Check if there are any items with tool_call not null
            for item in new_response[0]["flattened_approval_info"]:
                if item is not None:
                    has_more_requests = True
                    break

        # Store the new response
        st.session_state.current_response = new_response

        if has_more_requests:
            # If there are more requests, we'll process them in the next cycle
            # Don't change showing_resume_request to allow the new requests to be displayed
            # Create a new handler for the new response
            from ResponseHandler import ResponseHandler
            st.session_state.current_handler = ResponseHandler(new_response)
            return None
        else:
            # If no more requests, mark that we're no longer showing resume requests
            st.session_state.showing_resume_request = False

            # Extract content from the last assistant message for display
            response_content = None
            if "messages" in new_response[0] and new_response[0]["messages"]:
                for msg in reversed(new_response[0]["messages"]):
                    if msg.get("role") == "assistant" and "content" in msg and msg["content"] is not None:
                        response_content = msg["content"]
                        break

            # If no content was found in the messages, check if there's a direct content in the response
            if not response_content and "content" in new_response[0] and new_response[0]["content"] is not None:
                response_content = new_response[0]["content"]

            # If still no content, use a default message
            if not response_content:
                response_content = "Request processed successfully."

            # Add to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_content
            })

            return response_content

    @staticmethod
    def display_resume_request_interface(handler, make_api_request):
        """
        Display the tool call approval interface with checkboxes for each item.

        :param handler: ResponseHandler instance containing the flattened_approval_info
        :param make_api_request: Function to make API requests
        :return: Updated response if sent, None otherwise
        """
        approval_info = handler.flattened_approval_info

        if not approval_info:
            return None

        # Initialize session state for selected approvals if not exists
        if "selected_approvals" not in st.session_state:
            st.session_state.selected_approvals = {}

        # Initialize session state for approval metadata if not exists
        if "approval_metadata" not in st.session_state:
            st.session_state.approval_metadata = {}

        approval_metadata = {}

        # Show message with avatar at the top
        with st.chat_message("assistant"):
            if approval_info:
                # Display tool calls
                no_approval_request, approval_metadata = UIComponents.display_approval_checkboxes(approval_info)

                st.session_state.approval_metadata = approval_metadata

            # Show submit button if any checkbox is selected
            if no_approval_request:
                # Process approvals and get new response
                new_response = UIComponents.process_approvals(
                    handler,
                    approval_info,
                    approval_metadata,
                    make_api_request
                )

                # Handle the new response
                UIComponents.handle_new_response(new_response)
                st.rerun()
            elif st.button("Approve", key="approve"):
                new_response = UIComponents.process_approvals(
                    handler,
                    approval_info,
                    approval_metadata,
                    make_api_request
                )

                # Handle the new response
                UIComponents.handle_new_response(new_response)
                st.rerun()
            elif st.button("Disapprove", key="disapprove"):
                st.session_state.showing_resume_request = False
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "You have declined the request, so the briefing agent will not proceed. If you wish to continue later, please start a new conversation."
                })
                st.rerun()

    @staticmethod
    def display_history_item(history_item, index):
        """
        Display a history item in the sidebar.

        :param history_item: The history item to display
        :param index: The index of the history item
        """
        if "tool_call" in history_item:
            with st.expander(f"Approval: {history_item['function_name']}", expanded=False):
                # Use the helper function to display tool call information
                st.markdown(f"**Path:** {history_item['path']}")
                st.markdown(f"**Parameters:**")
                st.json(f"{history_item['json_args']}")
                st.markdown(f"**Status:** {'✅ Approved' if history_item['approved'] else '❌ Disapproved'}")
                if history_item.get('message'):
                    st.markdown(f"**Metadata:** {history_item['message']}")
                st.markdown(f"**Timestamp:** {history_item['timestamp']}")
                st.markdown(f"**Reviewer:** {history_item['reviewer_id'] or 'Anonymous'}")
        elif "status_info" in history_item:
            st.markdown(f"""
            <div style="
                border: 1px solid rgba(49, 51, 63, 0.2); 
                border-radius: 6px; 
                padding: 0.75rem 1rem; 
                margin-bottom: 15px; 
                background-color: rgba(240, 242, 246, 0.8);
                font-weight: 400;
                font-size: 14px;
                font-family: "Source Sans Pro", sans-serif;
                color: rgb(49, 51, 63);">
                <p style="margin: 0px;">
                     Status Update: {history_item['status_info']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # st.markdown(f"Status {index+1}: {history_item['status_info']}")

    @staticmethod
    def display_request_history():
        """
        Display the request history in the sidebar.
        """
        if st.session_state.request_history:
            st.header("Approval & Status Update History")
            for i, history_item in enumerate(st.session_state.request_history):
                UIComponents.display_history_item(history_item, i)