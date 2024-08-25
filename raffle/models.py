"""
Models for the RESTful Raffle application.

The `Raffle` model represents a single raffle event, defining its properties and methods.
The `Ticket` model represents a single ticket in a raffle, with unique ticket number and verification code.
The `Winner` model represents a participant who has won a prize in a raffle.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
import random
import uuid
from django.db import transaction


class Raffle(models.Model):
    """Represents a single raffle event."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=False)
    total_tickets = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prizes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        """Validate the raffle instance before being saved to the database.
           Serves as a safeguard to ensure data integrity for the data being stored
        """
        super().clean()
        self.validate_prizes()

    def validate_prizes(self):
        """Validate the prizes for the raffle."""
        if not isinstance(self.prizes, list):
            raise ValidationError("Prizes must be a list.")

        for prize in self.prizes:
            if not isinstance(prize, dict):
                raise ValidationError("Each prize must be a dictionary.")

            if "name" not in prize or "amount" not in prize:
                raise ValidationError("Each prize must have a 'name' and 'amount' key.")

            if not isinstance(prize["name"], str):
                raise ValidationError("The 'name' key of each prize must be a string.")

            if not isinstance(prize["amount"], int) or prize["amount"] <= 0:
                raise ValidationError("The 'amount' key of each prize must be a positive integer.")

    def save(self, *args, **kwargs):
        """Generate tickets after raffle creation."""
        super().save(*args, **kwargs)
        if not self.tickets.exists():
            self.generate_tickets()

    def generate_tickets(self):
        """Generate and shuffle tickets for the raffle."""
        max_ticket_number = min(self.total_tickets, 2**31 - 1)  # Limiting to 2^31 - 1 for SQLite compatibility

        tickets = []
        for i in range(self.total_tickets):
            ticket_number = (i % max_ticket_number) + 1
            ticket = Ticket(raffle=self, ticket_number=ticket_number)
            #ticket.set_verification_code(uuid.uuid4())  # Generating a unique verification code
            tickets.append(ticket)

        random.shuffle(tickets)

        # Creating tickets in bulk to optimize database operations   
        Ticket.objects.bulk_create(tickets)

    def get_random_ticket(self, participant_ip):
        """Get a random available ticket for the given participant IP."""
        with transaction.atomic():
            available_ticket = self.tickets.select_related('raffle').filter(participant_ip__isnull=True).order_by('?').select_for_update().first()#to ensure non-sequential distribution of tickets
            if available_ticket:
                available_ticket.participant_ip = participant_ip
                available_ticket.save()
                self.refresh_from_db()
        return available_ticket


class Ticket(models.Model):
    """Represents a single ticket in a raffle."""
    raffle = models.ForeignKey('Raffle', on_delete=models.CASCADE, related_name='tickets')
    ticket_number = models.BigIntegerField(validators=[MinValueValidator(1)])
    verification_code = models.CharField(max_length=128, unique=True, editable=False, null=True, blank=True)
    participant_ip = models.GenericIPAddressField(null=True, blank=True, unique=False)
    is_winner = models.BooleanField(default=False, editable=False)

    class Meta:
        unique_together = [('raffle', 'ticket_number'), ('raffle', 'participant_ip')]

    def __str__(self):
        return f"Ticket number: {self.ticket_number} for {self.raffle.name}"
    
    def save(self, *args, **kwargs):
        """Hash and set the verification code before saving if not already set."""
        if not self.verification_code: 
            code = str(uuid.uuid4())  # Generate a unique verification code
            self.set_verification_code(code)
        super().save(*args, **kwargs)

    def set_verification_code(self, code):
        """Hash and set the verification code."""
        self.verification_code = make_password(str(code))

    def check_verification_code(self, code):
        """Check if the provided code matches the hashed verification code."""
        return check_password(str(code), self.verification_code)

    

class Winner(models.Model):
    """Represents a participant who has won a prize in a raffle."""
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, default=None)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    prize = models.JSONField()

    def __str__(self):
        return f"Winner of {self.prize} is with ticket {self.ticket.ticket_number}"
 
 