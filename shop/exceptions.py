# myapp/exceptions.py
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    # Log the error (optional but recommended)
    logger.error(f"Exception: {str(exc)} | Context: {context}")

    # If DRF already handled it, just return
    if response is not None:
        return response

    # Handle unhandled exceptions
    return Response(
        {
            "status": "error",
            "message": str(exc),
            "details": "An unexpected error occurred.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
