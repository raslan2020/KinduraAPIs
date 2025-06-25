from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Standard success response format
    """
    response_data = {
        "status": True,
        "result": data if data is not None else {"message": message}
    }
    return Response(response_data, status=status_code)


def error_response(error_message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standard error response format
    """
    response_data = {
        "status": False,
        "result": {"error": error_message}
    }
    return Response(response_data, status=status_code) 