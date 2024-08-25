import django_filters
from .models import Raffle, Winner

class RaffleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    total_tickets = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    winners_drawn = django_filters.BooleanFilter(field_name='winner', lookup_expr='isnull', exclude=True)

    class Meta:
        model = Raffle
        fields = ['name', 'total_tickets', 'created_at', 'winners_drawn']

class WinnerFilter(django_filters.FilterSet):
    class Meta:
        model = Winner
        fields = ['raffle', 'ticket__participant_ip']
        filter_overrides = {
            'prize': {
                'filter_class': django_filters.CharFilter,
                'field_name': 'prize__name',
                'lookup_expr': 'icontains',
            },
        }
