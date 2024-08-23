# Django imports
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.db import transaction

from django.core.cache import cache
from django.conf import settings


# Django REST Framework imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .exceptions import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

# Project-specific imports
from .models import Raffle, Ticket, Winner

from .permissions import is_manager_ip
from .logging_utils import custom_exception_handler
from .serializers import RaffleSerializer, TicketSerializer, WinnerSerializer
from .logging_utils import logger
from .filters import RaffleFilter, WinnerFilter
from .forms import RaffleForm

# Python standard library imports
import random
import uuid


class RaffleListCreateView(generics.ListCreateAPIView, ListView):
    """
    API view to list and create raffles.

    - GET: Returns a paginated list of all raffles, ordered by creation date (latest first).
          Supports filtering by 'name', 'total_tickets', 'created_at', and 'winners_drawn' using query parameters.
    - POST: Creates a new raffle. Only accessible by manager IPs defined in settings.
    """

    serializer_class = RaffleSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RaffleFilter
    pagination_class = PageNumberPagination
    template_name = 'raffle_list.html'
    context_object_name = 'raffles'



    def get_queryset(self):
        """
        Get the queryset for the raffle list view.
        """
        queryset = Raffle.objects.all()
        name = self.request.query_params.get('name',None)
        filter_mapping = {
            'total_tickets': lambda value: queryset.filter(total_tickets=value).distinct(),
            'created_at': lambda value: queryset.filter(created_at__date=value).distinct()  if value else queryset,
            'winners_drawn': lambda value: queryset.filter(winner__isnull=not (value.lower() == 'true')).distinct(),
        }

        if name:
            queryset = queryset.filter(name__icontains=name)

        for param, value in self.request.query_params.items():
            if param in filter_mapping:
                queryset = filter_mapping[param](value)

        return queryset.order_by('-created_at')


    def get_context_data(self, **kwargs):
        """
        Get the context data for the raffle list view.
        """
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.get_queryset()
        context['is_manager'] = is_manager_ip(self.request)
        if context['is_manager']:
            context['raffle_form'] = RaffleForm()
        return context
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the raffle list view.
        """
        if not getattr(settings, 'DISABLE_TEST_CACHING', False):
            key = 'raffle_list'
            response = cache.get(key)
            if response is None:
                is_manager = is_manager_ip(request)
                if request.accepted_renderer.format == 'html':
                    self.object_list = self.get_queryset()
                    context = self.get_context_data()
                    context['is_manager'] = is_manager
                    if is_manager:
                        context['raffle_form'] = RaffleForm()
                    response = self.render_to_response(context)
                    cache.set(key, response, 60 * 15)  # Cache for 15 minutes
                else:
                    response = super().get(request, *args, **kwargs)
                    cache.set(key, response, 60 * 15)  # Cache for 15 minutes
            return response
        else:
            is_manager = is_manager_ip(request)
            if request.accepted_renderer.format == 'html':
                self.object_list = self.get_queryset()
                context = self.get_context_data()
                context['is_manager'] = is_manager
                if is_manager:
                    context['raffle_form'] = RaffleForm()
                return self.render_to_response(context)
            return super().get(request, *args, **kwargs)


    def handle_unauthorized_request(self, request):
        """
        Handle unauthorized requests for creating a raffle.
        """
        context = {'request': request, 'raffle': None, 'template_name': 'raffle_list.html'}
        return custom_exception_handler(PermissionDeniedException(), context)   
        
        
    def perform_create(self, serializer):
        """
        Handles the creation of a new raffle instance.

        - Checks if the request originates from a manager IP.
        - Raises PermissionDenied if not a manager IP.
        - Saves the new raffle instance if a manager IP.
        """
        if not is_manager_ip(self.request):
            return self.handle_unauthorized_request(self.request)
        serializer.save()

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for creating a new raffle.
        """
        if not is_manager_ip(request):
            return self.handle_unauthorized_request(request)

        form = RaffleForm(request.POST)
        if form.is_valid():
            form.save()
            self.object_list = self.get_queryset()
            if request.accepted_renderer.format == 'html':
                logger.info(f'Raffle created successfully by IP: {request.META.get("REMOTE_ADDR")}')
                return render(request, self.template_name, {'success_message': 'Raffle created successfully.'}, status=201)
            return Response({"detail": "Raffle created successfully."}, status=status.HTTP_201_CREATED)

        self.object_list = self.get_queryset()
        return super().post(request, *args, **kwargs)



class RaffleDetailView(generics.RetrieveAPIView, ListView):
    """
    API view to retrieve details of a specific raffle.

    - GET: Returns the details of the specified raffle.
    """

    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer
    permission_classes = [AllowAny]
    template_name = 'raffle_detail.html'
    context_object_name = 'raffle'
     
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the raffle detail view.
        """
        if request.accepted_renderer.format == 'html':
            return ListView.get(self, request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Add additional context to the serializer for dynamic fields.

        Returns:
            dict: The serializer context with additional fields:
                - 'available_tickets': Number of tickets still available for the raffle.
                - 'winners_drawn': Boolean indicating if winners have been drawn for the raffle.
        """
        context = super().get_serializer_context()
        raffle= self.get_object()
        serializer= RaffleSerializer(raffle)
        context['available_tickets'] =serializer.data.get('available_tickets')
        context['winners_drawn'] = serializer.data.get('winners_drawn')
        return context


    def get_context_data(self, **kwargs):
        """
        Get the context data for the raffle detail view.
        """
        context = super().get_context_data(**kwargs)
        raffle = self.get_object()
        serializer = RaffleSerializer(raffle)
        context['raffle'] = raffle
        context['available_tickets'] = serializer.data.get('available_tickets')
        context['winners_drawn'] = serializer.data.get('winners_drawn')
        return context


class ParticipateView(generics.CreateAPIView):
    """
    API view to participate in a raffle by claiming a ticket.

    - GET: Returns instructions for the POST request.
    - POST: Allows a user to participate in the raffle by claiming a ticket.
    """

    serializer_class = TicketSerializer
    permission_classes = [AllowAny]
    template_name = 'participate.html'
    context_object_name = 'ticket'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests by providing instructions for the POST request.
        """
        return Response({
            "message": "Just press the post button without any content to participate",
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests by allowing a user to participate in the raffle.
        The user is identified by their IP address and can claim one ticket per raffle.
        """
        raffle = self.get_raffle() # get_object_or_404(Raffle, pk=self.kwargs['pk'])
        participant_ip = self.get_participant_ip(request)#request.META.get('REMOTE_ADDR')


        # Check if there are available tickets
        if not self.has_available_tickets(raffle):
            context = {'request': request, 'raffle': raffle, 'template_name': 'participate.html'}
            return custom_exception_handler(NoAvailableTicketsException(), context)
            

        # Check if the participant has already claimed a ticket
        if self.has_already_participated(raffle, participant_ip):
             context = {'request': request, 'raffle': raffle, 'template_name': 'participate.html'}
             return custom_exception_handler(AlreadyParticipatedException(), context)
                

        # Try to claim a ticket for the participant
        return self.attempt_ticket_claim(request, raffle, participant_ip)

    def get_raffle(self):
        """
        Retrieve the raffle instance for the current request.

        Returns:
            Raffle: The raffle instance.
        """
        return get_object_or_404(Raffle, pk=self.kwargs['pk'])

    def get_participant_ip(self, request):
        """
        Extract the participant's IP address from the request.

        Args:
            request (Request): The current request object.

        Returns:
            str: The participant's IP address.
        """
        return request.META.get('REMOTE_ADDR')

    def has_available_tickets(self, raffle):
        """
        Check if there are any available tickets for the raffle.

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            bool: True if tickets are available, False otherwise.
        """
        return raffle.tickets.filter(participant_ip=None).exists()
         

    def has_already_participated(self, raffle, participant_ip):
        """
        Check if the participant has already claimed a ticket in the raffle.

        Args:
            raffle (Raffle): The raffle instance.
            participant_ip (str): The participant's IP address.

        Returns:
            bool: True if the participant has already claimed a ticket, False otherwise.
        """
        return raffle.tickets.filter(participant_ip=participant_ip).exists()

       

    def attempt_ticket_claim(self, request, raffle, participant_ip):
        """
        Attempt to claim a ticket for the participant.

        Args:
            request (Request): The current request object.
            raffle (Raffle): The raffle instance.
            participant_ip (str): The participant's IP address.

        Returns:
            Response: A success response with the ticket information, or an error response if no tickets are available.
        """
        try:
            ticket = raffle.get_random_ticket(participant_ip)
            #ticket = raffle.tickets.filter(participant_ip__isnull=True).select_for_update().first()
            if ticket:
                verification_code = str(uuid.uuid4())
                ticket.set_verification_code(verification_code)
                #ticket.participant_ip = participant_ip
                ticket.save()
                return self.handle_successful_participation(request, raffle, ticket, verification_code)             
        except AlreadyParticipatedException() as e:
            context = {'request': request, 'raffle': raffle, 'template_name': 'participate.html'}
            return custom_exception_handler(e, context)
    
        except NoAvailableTicketsException() as e:
             context = {'request': request, 'raffle': raffle, 'template_name': 'participate.html'}
             return custom_exception_handler(e, context)
        except Exception as e:
             context = {'request': request, 'raffle': raffle, 'template_name': 'participate.html'}
             return custom_exception_handler(e, context)
           

    def handle_successful_participation(self, request, raffle, ticket, verification_code):
        """
        Handle the successful participation in the raffle.

        Args:
            request (Request): The current request object.
            raffle (Raffle): The raffle instance.
            ticket (Ticket): The ticket instance that was claimed.
            verification_code (str): The verification code for the ticket.

        Returns:
            Response: A success response rendered in HTML or JSON.
        """
        serializer = self.get_serializer(ticket)
        data = serializer.data
        data['verification_code'] = verification_code

        if request.accepted_renderer.format == 'html':
            logger.info(f'IP {ticket.participant_ip} successfully participated in raffle {raffle.pk}')
            return render(request, self.template_name, {
                'raffle': raffle,
                'success_message': "You have successfully participated in the raffle!",
                'ticket_verification_code': verification_code,
                'ticket_number': ticket.ticket_number
            }, status=status.HTTP_201_CREATED)

        return Response(data, status=status.HTTP_201_CREATED)
        


class RaffleWinnersView(APIView):
    """
    API view to handle listing and drawing raffle winners.

    - GET: Lists all winners for the specified raffle.
    - POST: Draws winners for the specified raffle (Manager only).
    """
    permission_classes = [AllowAny]
    serializer_class = WinnerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WinnerFilter
    template_names = ['winners.html', 'draw_winners.html']
    context_object_name = 'winners'

   

    def get(self, request, pk):
        """
        Handle GET requests to list all winners for the specified raffle.

        Args:
            request (Request): The current request.
            pk (str): The primary key of the raffle.

        Returns:
            Response: A list of winners for the specified raffle.
        """
        raffle = get_object_or_404(Raffle, pk=pk)
        winners = Winner.objects.filter(raffle=raffle)
        is_manager = is_manager_ip(request)

        if request.accepted_renderer.format == 'html':
            return render(request, self.template_names[0], {
                'raffle': raffle,
                'winners': winners,
                'is_manager': is_manager
            })

        serializer = WinnerSerializer(winners, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        """
        Handle POST requests to draw winners for the specified raffle (Manager only).

        Args:
            request (Request): The current request.
            pk (str): The primary key of the raffle.

        Returns:
            Response: A list of drawn winners or an error message.
        """
        is_manager = is_manager_ip(request)
        if not is_manager:
            return self.handle_unauthorized_request(request)

        raffle = get_object_or_404(Raffle, pk=pk)

        if self.has_available_tickets(raffle):
             context = {'request': request, 'raffle': raffle, 'template_name': 'draw_winners.html'}
             return custom_exception_handler(AvailableTicketsException(), context)

        if self.winners_already_drawn(raffle):
            context = {'request': request, 'raffle': raffle, 'template_name': 'draw_winners.html'}
            return custom_exception_handler(WinnersAlreadyDrawnException(), context)

        if not self.has_enough_participants(raffle):
            context = {'request': request, 'raffle': raffle, 'template_name': 'draw_winners.html'}
            return custom_exception_handler(NotEnoughParticipantsException(), context)
            
        winners = self.draw_winners(raffle)
        return self.handle_successful_draw(request, raffle, winners)

    def handle_unauthorized_request(self, request):
        """
        Handle unauthorized requests for drawing winners.

        Args:
            request (Request): The current request.

        Returns:
            Response: An error message indicating permission denied.
        """
        context = {'request': request, 'raffle': None, 'template_name': 'draw_winners.html'}
        return custom_exception_handler(DrawWinnersNotManagerException(), context)
       
       
    
    def has_available_tickets(self, raffle):
        """
        Check if there are available tickets for the given raffle.

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            bool: True if there are available tickets, False otherwise.
        """
        return raffle.tickets.filter(participant_ip__isnull=True).exists()

    
    def winners_already_drawn(self, raffle):
        """
        Check if winners have already been drawn for the given raffle.

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            bool: True if winners have already been drawn, False otherwise.
        """
        return Winner.objects.filter(raffle=raffle).exists()

    
    def has_enough_participants(self, raffle):
        """
        Check if there are enough participants to determine winners for the given raffle.

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            bool: True if there are enough participants, False otherwise.
        """
        eligible_tickets = raffle.tickets.filter(participant_ip__isnull=False, is_winner=False)
        total_prizes =sum(prize.get('amount', 0) for prize in raffle.prizes)
        return len(eligible_tickets) >= total_prizes

    
    def draw_winners(self, raffle):
        """
        Draw winners for the given raffle.
        
        This method selects the winners for the raffle based on the available prizes and eligible tickets.
        It ensures that the number of winners drawn matches the total number of prizes to be awarded.
        The winners are randomly selected from the pool of eligible tickets (tickets that have been claimed
        and are not already winners).

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            list: A list of drawn winners.
        """
        eligible_tickets = list(raffle.tickets.filter(participant_ip__isnull=False, is_winner=False))
        total_prizes = sum(prize['amount'] for prize in raffle.prizes)
        winning_tickets = random.sample(eligible_tickets, total_prizes)
        winners = []
        prizes_awarded = {prize_data['name']: 0 for prize_data in raffle.prizes}  # Initialize count for each prize

        for i in range(total_prizes):
            if winning_tickets:
                ticket = winning_tickets.pop()

                # Find the next available prize to award
                for prize_data in raffle.prizes:
                    prize_name = prize_data['name']
                    if prizes_awarded[prize_name] < prize_data['amount']:
                        prize_to_award = prize_name
                        prizes_awarded[prize_name] += 1
                        break

                winner = Winner.objects.create(
                    raffle=raffle,
                    ticket=ticket,
                    prize=prize_to_award
                )
                ticket.is_winner = True
                ticket.save()
                winners.append(winner)

        return winners

    def handle_successful_draw(self, request, raffle, winners):
        """
        Handle the case when winners are successfully drawn for the raffle.

        Args:
            request (Request): The current request.
            raffle (Raffle): The raffle instance.
            winners (list): A list of drawn winners.

        Returns:
            Response: A list of drawn winners with their ticket numbers.
        """
        serializer = WinnerSerializer(winners, many=True)
        data = serializer.data
        for item in data:
            item['ticket_number'] = Winner.objects.get(id=item['id']).ticket.ticket_number

        if request.accepted_renderer.format == 'html':
            return render(request, self.template_names[1], {
                'data': data,
                'raffle': raffle,
                'winners': winners,
                'success_message': 'Winners drawn successfully.',
                'status': status.HTTP_201_CREATED
            })
        return Response(data, status=status.HTTP_201_CREATED)




#ticket number is 15 , code: 703d3217-53fe-49e4-82a8-6f5864846ee8



class VerifyTicketView(APIView):
    """
    API view to verify a raffle ticket.

    - POST: Verifies a raffle ticket and returns its winning status.
    """
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]
    template_name = 'verify_ticket.html'
    context_object_name = 'ticket'

    def post(self, request, pk):
        """
        Handle POST requests to verify a raffle ticket.

        Args:
            request (Request): The current request.
            pk (str): The primary key of the raffle.

        Returns:
            Response: The winning status of the ticket or an error message.
        """
        ticket_number = request.data.get('ticket_number')
        verification_code = request.data.get('verification_code')

        if not self.has_ticket_information(ticket_number, verification_code):
            return self.handle_missing_ticket_information(request, pk)

        raffle = self.get_raffle(pk)

        if not self.winners_drawn(raffle):
            context = {'request': request, 'raffle': raffle, 'template_name': 'verify_ticket.html'}
            return custom_exception_handler(WinnersNotDrawnException(), context)
            
        ticket = self.get_ticket(raffle, ticket_number)
        if not ticket:
            context = {'request': request, 'raffle': raffle, 'template_name': 'verify_ticket.html'}
            return custom_exception_handler(InvalidTicketNumberException(), context)
           

        if not self.verify_ticket(ticket, verification_code):
            context = {'request': request, 'raffle': raffle, 'template_name': 'verify_ticket.html'}
            return custom_exception_handler(InvalidVerificationCodeException(), context)
            
        winner = self.get_winner(ticket)
        return self.handle_ticket_verification(request, raffle, winner)

    def has_ticket_information(self, ticket_number, verification_code):
        """
        Check if the required ticket information is provided.

        Args:
            ticket_number (str): The ticket number.
            verification_code (str): The verification code.

        Returns:
            bool: True if both ticket number and verification code are provided, False otherwise.
        """
        return ticket_number and verification_code
    
    def handle_missing_ticket_information(self, request, pk):
        raffle = self.get_raffle(pk)
        context = {'request': request, 'raffle': raffle, 'template_name': 'verify_ticket.html'}
        return custom_exception_handler(MissingTicketInformationException(), context)
       

    
    def get_raffle(self, pk):
        """
        Get the raffle instance for the given primary key.

        Args:
            pk (str): The primary key of the raffle.

        Returns:
            Raffle: The raffle instance.
        """
        return get_object_or_404(Raffle, pk=pk)

    def winners_drawn(self, raffle):
        """
        Check if winners have been drawn for the given raffle.

        Args:
            raffle (Raffle): The raffle instance.

        Returns:
            bool: True if winners have been drawn, False otherwise.
        """
        #return Winner.objects.filter(raffle=raffle).exists()
        return RaffleSerializer(raffle).data.get('winners_drawn')
        

   
    def get_ticket(self, raffle, ticket_number):
        """
        Get the ticket instance for the given raffle and ticket number.

        Args:
            raffle (Raffle): The raffle instance.
            ticket_number (str): The ticket number.

        Returns:
            Ticket: The ticket instance, or None if not found.
        """
        try:
            return Ticket.objects.get(raffle=raffle, ticket_number=ticket_number)
        except Ticket.DoesNotExist:
            return None

    
    def verify_ticket(self, ticket, verification_code):
        """
        Verify the provided verification code against the stored hashed code for the ticket.

        Args:
            ticket (Ticket): The ticket instance.
            verification_code (str): The verification code.

        Returns:
            bool: True if the verification code is valid, False otherwise.
        """
        return ticket.check_verification_code(verification_code)

   
    def get_winner(self, ticket):
        """
        Get the winner instance for the given ticket.

        Args:
            ticket (Ticket): The ticket instance.

        Returns:
            Winner: The winner instance, or None if the ticket is not a winner.
        """
        try:
            return Winner.objects.get(ticket=ticket)
        except Winner.DoesNotExist:
            return None

    def render_response(self, request, raffle, success_message, has_won, prize):
        """
        Helper function to render the response for ticket verification.

        Args:
            request (Request): The current request.
            raffle (Raffle): The raffle instance.
            success_message (str): The success message to display.
            has_won (bool): Whether the ticket is a winner or not.
            prize (str): The prize won, if applicable.

        Returns:
            Response: The rendered response.
        """
        if request.accepted_renderer.format == 'html':
            return render(request, self.template_name, {
                'raffle': raffle,
                'success_message': success_message,
                'has_won': has_won,
                'prize': prize
            }, status=status.HTTP_200_OK)
        return Response({
            'detail': success_message,
            'has_won': has_won,
            'prize': prize
        }, status=status.HTTP_200_OK)

    def handle_ticket_verification(self, request, raffle, winner):
        """
        Handle the ticket verification and return the winning status.

        Args:
            request (Request): The current request.
            raffle (Raffle): The raffle instance.
            winner (Winner): The winner instance, or None if the ticket is not a winner.

        Returns:
            Response: The winning status of the ticket.
        """
        if winner:
            success_message = "Congratulations! Your ticket is a winner!"
            has_won = True
            prize = winner.prize
        else:
            success_message = "Your ticket is valid but not a winner."
            has_won = False
            prize = None

        return self.render_response(request, raffle, success_message, has_won, prize)


#3 c05928d6-8e3e-451f-8eab-2984e654708f