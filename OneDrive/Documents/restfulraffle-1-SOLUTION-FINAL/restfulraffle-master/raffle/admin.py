from django.contrib import admin

from .models import Raffle, Winner, Ticket 

# Register your models here.
admin.site.register(Raffle)
admin.site.register(Winner)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('raffle', 'ticket_number', 'verification_code', 'participant_ip', 'is_winner')

admin.site.register(Ticket, TicketAdmin)


