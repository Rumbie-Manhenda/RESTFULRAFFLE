"""
Serializers for the Raffle, Ticket, and Winner models in the RESTful Raffle application.
"""
from rest_framework import serializers
from .models import Raffle, Ticket, Winner
from collections import OrderedDict
from .exceptions import TooManyPrizesException, NoPrizesException


class PrizeSerializer(serializers.Serializer):
    """
    Serializer for Prize data.

    This serializer is used to validate and represent prize information
    within the RaffleSerializer. It does not directly correspond to a model.
    """
    name = serializers.CharField(max_length=255)  
    amount = serializers.IntegerField(min_value=1)


class RaffleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Raffle model.

    Handles serialization and deserialization of Raffle instances,
    including nested Prize data.
    """
    prizes = PrizeSerializer(many=True)
    available_tickets = serializers.SerializerMethodField()
    winners_drawn = serializers.SerializerMethodField()

    class Meta:
        model = Raffle
        fields = ['id', 'name', 'total_tickets', 'created_at', 'prizes', 'available_tickets', 'winners_drawn']
        read_only_fields = ['id', 'created_at', 'available_tickets', 'winners_drawn']

    def get_available_tickets(self, obj):
        """
        Calculates and returns the number of tickets still available for the raffle.
        """
        return obj.tickets.filter(participant_ip=None).count()

    def get_winners_drawn(self, obj):
        """
        Checks and returns a boolean indicating if winners have been drawn for the raffle.
        """
        return Winner.objects.filter(raffle=obj).exists()

    def create(self, validated_data):
        """
        Creates a new Raffle instance and associated Prize instances.

        Handles the creation of both the raffle and its prizes from the validated data.
        """
        prizes_data = validated_data.pop('prizes')
        raffle = Raffle.objects.create(**validated_data)

        for prize_data in prizes_data:
            raffle.prizes.append(prize_data)

        raffle.save()
        return raffle

    def validate_prizes(self, prizes_data):
        """
        Validates the provided prize data.

        - Checks if at least one prize is provided.
        - Ensures the total number of prizes does not exceed the total tickets.
        """
        if not prizes_data:
            raise NoPrizesException

        total_prizes = sum(prize_data.get('amount', 1) for prize_data in prizes_data)
        if total_prizes > self.initial_data.get('total_tickets', 0):
            raise TooManyPrizesException
        return prizes_data


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ticket model.

    Handles serialization and deserialization of Ticket instances.
    Some fields are read-only as they are automatically generated.
    """
    verification_code = serializers.CharField(help_text="The verification code for the ticket e.g., 'ABC123')")
    raffle_id = serializers.UUIDField(source='raffle.id', read_only=True)
    ticket_number = serializers.IntegerField(help_text="Enter your ticket number (e.g., '3')")

    class Meta:
        model = Ticket
        fields = ['id', 'raffle_id', 'ticket_number', 'verification_code', 'participant_ip']
        read_only_fields = ['id', 'raffle_id', 'ticket_number', 'verification_code', 'participant_ip']


class WinnerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Winner model.

    Handles serialization of Winner instances, including the associated
    Ticket and Prize data.
    """
    ticket = TicketSerializer(read_only=True)
    prize = serializers.JSONField()
    raffle = serializers.CharField(source='raffle.name', read_only=True)
    ticket_number = serializers.SerializerMethodField()

    class Meta:
        model = Winner
        fields = ['id', 'ticket', 'prize', 'raffle', 'ticket_number']
        read_only_fields = ['id', 'ticket', 'prize', 'ticket_number']

    def get_ticket_number(self, obj):
        """
        Retrieves the ticket number from the associated Ticket instance.
        """
        if isinstance(obj, Winner):
            return obj.ticket.ticket_number
        elif isinstance(obj, OrderedDict):
            ticket_data = obj.get('ticket')
            if ticket_data:
                return ticket_data.get('ticket_number')
        return None
