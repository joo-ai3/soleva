from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    Provides consistent error response format and logging
    """

    # Get the standard error response from DRF
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error for debugging
        logger.error(
            f"API Error: {exc.__class__.__name__}: {str(exc)}",
            extra={
                'view': context['view'].__class__.__name__,
                'request_method': context['request'].method,
                'request_path': context['request'].path,
                'user': getattr(context['request'].user, 'id', None) if hasattr(context['request'], 'user') else None
            }
        )

        # Customize the error response format
        custom_response_data = {
            'success': False,
            'error': {
                'type': exc.__class__.__name__,
                'message': str(exc),
                'details': response.data if hasattr(response, 'data') else None
            }
        }

        # Add request-specific information for debugging in development
        if hasattr(context['request'], 'DEBUG') and context['request'].DEBUG:
            custom_response_data['debug'] = {
                'view': context['view'].__class__.__name__,
                'method': context['request'].method,
                'path': context['request'].path,
                'user_agent': context['request'].META.get('HTTP_USER_AGENT', ''),
                'ip': context['request'].META.get('REMOTE_ADDR', ''),
            }

        response.data = custom_response_data

    else:
        # Handle unhandled exceptions
        logger.critical(
            f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
            exc_info=True,
            extra={
                'view': context.get('view', {}).__class__.__name__ if context.get('view') else 'Unknown',
                'request_method': context.get('request', {}).method if context.get('request') else 'Unknown',
                'request_path': context.get('request', {}).path if context.get('request') else 'Unknown'
            }
        )

        # Return a generic 500 error response
        custom_response_data = {
            'success': False,
            'error': {
                'type': 'InternalServerError',
                'message': 'An unexpected error occurred. Please try again later.',
            }
        }

        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
