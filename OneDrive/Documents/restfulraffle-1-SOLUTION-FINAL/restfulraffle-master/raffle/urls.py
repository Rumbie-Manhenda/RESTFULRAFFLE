from django.urls import path
from .views import (
    RaffleListCreateView, RaffleDetailView, ParticipateView, 
     RaffleWinnersView, VerifyTicketView
)

urlpatterns = [
    path('', RaffleListCreateView.as_view(), name='raffle-list-create'),
    path('<uuid:pk>/', RaffleDetailView.as_view(), name='raffle-detail'),
    path('<uuid:pk>/participate/', ParticipateView.as_view(), name='raffle-participate'),
    path('<uuid:pk>/winners/', RaffleWinnersView.as_view(), name='winner-list'),
    path('<uuid:pk>/verify-ticket/', VerifyTicketView.as_view(), name='verify-ticket'),
]



# ticket number 8