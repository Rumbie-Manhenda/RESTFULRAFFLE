from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import render
import logging

from .exceptions import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('raffle.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.

    Args:
        exc (Exception): The exception instance to be handled.
        context (dict): The context dictionary containing request,raffle & template_name.

    Returns:
        Response: An error response rendered in HTML or JSON.
    """
    request = context.get('request')
    raffle = context.get('raffle')
    template_name = context.get('template_name', 'raffle_list.html')

    if isinstance(exc, PermissionDeniedException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, NoAvailableTicketsException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, AlreadyParticipatedException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, WinnersNotDrawnException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, InvalidTicketNumberException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, InvalidVerificationCodeException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, MissingTicketInformationException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, WinnersAlreadyDrawnException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, AvailableTicketsException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, NotEnoughParticipantsException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, DrawWinnersNotManagerException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, NoPrizesException):
        error_message = exc.default_detail
        status_code = exc.status_code
    elif isinstance(exc, TooManyPrizesException):
        error_message = exc.default_detail
        status_code = exc.status_code
    else:
        error_message = "An unexpected error occurred."
        status_code = 500

    logger.error(f"Error response rendered: {error_message} with status code {status_code}")

    if request.accepted_renderer.format == 'html':
        return render(request, template_name, {
            'raffle': raffle,
            'error_message': error_message
        }, status=status_code)

    return Response({"detail": error_message}, status=status_code)
