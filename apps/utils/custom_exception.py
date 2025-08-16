# project/custom_exception.py
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    # Get default DRF response
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Extract status code
        status_code = response.status_code

        # Extract error details
        error_data = extract_error_details(response.data)

        # Build final response
        response.data = {
            "status": status_code,
            "success": False,
            "message": error_data["message"],
            "field": error_data["field"],
        }

    return response


def extract_error_details(data):
    # Default values
    result = {"field": "validation_error", "message": "An error occurred"}

    if isinstance(data, dict):
        # Handle field errors
        for field, messages in data.items():
            if field == "detail":  # Non-field errors
                result["message"] = messages
                break
            elif isinstance(messages, list) and messages:
                result["field"] = field
                result["message"] = messages[0]
                break
            elif isinstance(messages, str):
                result["field"] = field
                result["message"] = messages
                break

    elif isinstance(data, list) and data:
        result["message"] = str(data[0])

    return result