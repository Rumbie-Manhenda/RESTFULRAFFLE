from .models import Raffle, Ticket
from django import forms

class RaffleForm(forms.ModelForm):
    class Meta:
        model = Raffle
        fields = ['name', 'total_tickets', 'prizes']
    
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter raffle name'})
    )
    total_tickets = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total number of tickets'})
    )
    prizes = forms.JSONField(
        initial=[{"name": "iPad", "amount": 1}, {"name": "AirPods", "amount": 2}],
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter prizes as JSON'})
    )


