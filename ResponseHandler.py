class ResponseHandler:
    """
    Processes the server response with focus on handling flattened_approval_info array.

    This simplified handler focuses on processing the flattened_approval_info array
    for tool call approvals, without the complexity of nested continuations.
    """

    def __init__(self, response):
        """
        Initialize the ResponseHandler with a server response.
        :param response: dict or list representing the server response.
        """
        # Handle different response formats
        if isinstance(response, list) and len(response) > 0:
            self.response = response[0]
        else:
            self.response = response

        self.flattened_approval_info = None
        if isinstance(self.response, dict) and "flattened_approval_info" in self.response:
            self.flattened_approval_info = self.response["flattened_approval_info"]

    def has_flattened_approval_info(self):
        """
        Check if the response has flattened approval info.
        :return: True if there are items in flattened_approval_info, False otherwise.
        """
        return bool(self.flattened_approval_info)

    def is_continuation_finished(self):
        """
        Check if the continuation is null or has a 'finished' status.
        :return: True if continuation is null or status is 'finished', False otherwise.
        """
        if not isinstance(self.response, dict):
            return True

        continuation = self.response.get("continuation")
        if continuation is None:
            return True

        if isinstance(continuation, dict):
            return continuation.get("status") == "finished"

        return False

    def update_approval_info(self, index, approve=True, metadata=None):
        """
        Update the approval status and metadata for an item in the flattened_approval_info array.

        :param index: The index of the item in the flattened_approval_info array
        :param approve: Boolean indicating approval status
        :param metadata: Optional metadata dictionary to add to the item
        """
        if self.flattened_approval_info and index < len(self.flattened_approval_info):
            self.flattened_approval_info[index]["approved"] = approve
            if metadata:
                self.flattened_approval_info[index]["metadata"] = metadata

    def prepare_for_submission(self):
        """
        Prepare the response for submission back to the API.
        :return: Updated response dict ready for submission.
        """
        return self.response
