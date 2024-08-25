
from django.urls import reverse
from rest_framework import status
from raffle.models import Raffle, Ticket, Winner
from .conftest import unexpected_response_error
from django.contrib.auth.hashers import check_password


def test_ticket_numbers_sequential(client, default_raffle, manager_ip):
    """
    Test that the raffle tickets are generated with sequential ticket numbers starting from 1.
    Requirement: The raffle tickets should be generated with sequential ticket numbers starting from 1.
    """
    response = client.post("/raffles/", data=default_raffle, REMOTE_ADDR=manager_ip)
    assert response.status_code == 201, unexpected_response_error(response)
    
    raffle_id = response.json()['id']
    raffle = Raffle.objects.get(id=raffle_id)
    
    # Retrieve the tickets for the raffle
    raffle_tickets = raffle.tickets.order_by('ticket_number')
    
    # Check if the ticket numbers are sequential starting from 1
    expected_numbers = list(range(1, raffle.total_tickets + 1))
    actual_numbers = [ticket.ticket_number for ticket in raffle_tickets]
    assert actual_numbers == expected_numbers


def test_non_sequential_ticket_distribution(client, raffle):
    """
    Test that raffle tickets are given out to participants requesting them in a non-sequential order.
    Requirement: The raffle tickets are given out to participants requesting them in a non-sequential order.
    """
    url = reverse('raffle-participate', kwargs={'pk': raffle['id']})
    ticket_numbers = []
    for i in range(raffle['total_tickets']):
        ip_factory = f"1.0.0.{i+1}" 
        response = client.post(url, REMOTE_ADDR=ip_factory)
        assert response.status_code == status.HTTP_201_CREATED, unexpected_response_error(response)
        ticket_numbers.append(response.data['ticket_number'])
    assert ticket_numbers != sorted(ticket_numbers)


def test_verification_code_storage(client, raffle, get_ticket):
    """
    Test that the application does not save the verification codes in plaintext.
    Requirement: The application does not save the verification codes in plaintext.
    """
    ticket = get_ticket(raffle['id'])
    ticket_obj = Ticket.objects.get(ticket_number=ticket['ticket_number'])
    assert ticket['verification_code'] != ticket_obj.verification_code
    assert check_password(ticket['verification_code'],ticket_obj.verification_code)

def test_unique_ticket_numbers(client, raffle):
    """
    Test that the same ticket number is never given out to multiple participants of a raffle.
    Requirement: The same ticket number is never given out to multiple participants of a raffle.
    """
    url = reverse('raffle-participate', kwargs={'pk': raffle['id']})
    ticket_numbers = []
    for i in range(raffle['total_tickets']):
        ip_factory = f"1.0.0.{i+1}"  
        response = client.post(url, REMOTE_ADDR=ip_factory)
        assert response.status_code == status.HTTP_201_CREATED, unexpected_response_error(response)
        ticket_numbers.append(response.data['ticket_number'])
    assert len(ticket_numbers) == len(set(ticket_numbers))

def test_winners_not_predetermined(client, raffle, get_ticket,manager_ip):
    """
    Test that the winners are not pre-determined.
    Requirement: The winners must not be pre-determined.
    """
    tickets = [get_ticket(raffle['id']) for _ in range(raffle['total_tickets'])]
    
    response = client.post(f"/raffles/{raffle['id']}/winners/",REMOTE_ADDR=manager_ip)
    assert response.status_code == status.HTTP_201_CREATED, unexpected_response_error
    winners = Winner.objects.filter(raffle_id=raffle['id'])
    assert len(winners) ==sum(prize['amount'] for prize in raffle['prizes'])
    assert set(winners.values_list('ticket__ticket_number', flat=True)) != set(t['ticket_number'] for t in tickets[:len(raffle['prizes'])])

def test_one_prize_per_ticket(client, raffle, get_ticket, manager_ip):
    """
    Test that one raffle ticket can't win more than one prize.
    Requirement: One raffle ticket can't win more than one prize.
    """
    tickets = dict(
        (t['ticket_number'], t)
        for t in [get_ticket(raffle['id']) for _ in range(raffle['total_tickets'])]
    )

    response = client.post(f"/raffles/{raffle['id']}/winners/", REMOTE_ADDR=manager_ip)
    assert response.status_code == status.HTTP_201_CREATED, unexpected_response_error(response)
    winners = Winner.objects.filter(raffle_id=raffle['id'])
    #This assertion checks that the number of winners is equal to the number of unique winning ticket numbers.
    assert len(winners) == len(set(winners.values_list('ticket__ticket_number', flat=True)))

    for winner in winners:
        assert check_password(tickets[winner.ticket.ticket_number]['verification_code'], winner.ticket.verification_code)

#$env:MANAGER_IPS = "123.123.123.123,127.0.0.2"
#git checkout -b finalversion commithash






    