import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(f"API Error: {exc} | Context: {context.get('view', '')} | Status: {response.status_code}")
        if isinstance(response.data, dict):
            response.data = {
                'success': False,
                'error': response.data,
                'status_code': response.status_code,
            }
        elif isinstance(response.data, list):
            response.data = {
                'success': False,
                'error': response.data,
                'status_code': response.status_code,
            }
    else:
        logger.exception(f"Unhandled exception: {exc}")
        response = Response(
            {
                'success': False,
                'error': 'Internal server error.',
                'status_code': 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
