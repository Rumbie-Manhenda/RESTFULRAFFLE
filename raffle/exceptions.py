from rest_framework.exceptions import APIException

class PermissionDeniedException(APIException):
    status_code = 403
    default_detail = 'Only managers can create raffles.'
    default_code = 'permission_denied'

class NoAvailableTicketsException(APIException):
    status_code = 410
    default_detail = "Tickets to this raffle are no longer available."
    default_code = 'no_available_tickets'

class AlreadyParticipatedException(APIException):
    status_code = 403
    default_detail = "Your IP address has already participated in this raffle."
    default_code = 'already_participated'

class WinnersNotDrawnException(APIException):
    status_code = 400
    default_detail = "Winners for the raffle have not been drawn yet."
    default_code = 'winners_not_drawn'

class InvalidTicketNumberException(APIException):
    status_code = 400
    default_detail = "Invalid ticket number."
    default_code = 'invalid_ticket_number'

class InvalidVerificationCodeException(APIException):
    status_code = 400
    default_detail = "Invalid verification code."
    default_code = 'invalid_verification_code'

class MissingTicketInformationException(APIException):
    status_code = 400
    default_detail = "Missing ticket information."
    default_code = 'missing_ticket_information'

class WinnersAlreadyDrawnException(APIException):
    status_code = 403
    default_detail = "Winners for the raffle have already been drawn."
    default_code = 'winners_already_drawn'

class AvailableTicketsException(APIException):
    status_code = 403
    default_detail = "Winners can't be drawn when tickets are still available."
    default_code = 'available_tickets'

class NotEnoughParticipantsException(APIException):
    status_code = 400
    default_detail = "Not enough participants to determine winners."
    default_code = 'not_enough_participants'
    
class DrawWinnersNotManagerException(APIException):
    status_code = 403
    default_detail= "Permission denied. You are not authorized to perform this action.Only managers can draw winners"
    default_code= 'permission_denied'
class NoPrizesException(APIException):
    status_code=400
    default_detail= "At least one prize is required for a raffle."
    default_code= 'raffle_has_no_prizes'
class TooManyPrizesException(APIException):
    status_code=400
    default_detail= "Too many prizes, the total number of prizes cannot exceed the total number of tickets."
    default_code= 'more_prizes_than_tickets'