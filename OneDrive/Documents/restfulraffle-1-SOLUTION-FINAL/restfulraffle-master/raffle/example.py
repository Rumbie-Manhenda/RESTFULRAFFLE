from django.views.generic import ListView
 

from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from .serializers import *
from .permissions import is_manager_ip
from .logging_utils import logger, custom_exception_handler
from .exceptions import *
from .forms import RaffleForm

class RaffleListCreateView(generics.ListCreateAPIView, ListView):
    """
    API view to list and create raffles.

    - GET: Returns a paginated list of all raffles, ordered by creation date (latest first).
          Supports filtering by 'name', 'total_tickets', 'created_at', and 'winners_drawn' using query parameters.
    - POST: Creates a new raffle. Only accessible by manager IPs defined in settings.
    """


    serializer_class = RaffleSerializer
    model= Raffle
    template_name= 'raffle_list.html'
    permission_classes = [AllowAny]
  
    
    def get_queryset(self):
        queryset = self.model.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.order_by('-created_at')
   
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self,request,*args, **kwargs):
     if not is_manager_ip(request):
         context = {'raffle': None, 'request': request, 'template_name':self.template_name}
         return custom_exception_handler(PermissionDeniedException(),context)
     form = RaffleForm(request.POST)
     if form.is_valid():
         raffle = form.save()
         serializer= self.serializer_class(raffle) 
         serializer.save()
         self.object_list= self.get_queryset() 
     return super().post(request,*args,**kwargs) 
    
    
class RaffleDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific raffle.
    """
   
    serializer_class = RaffleSerializer
    permission_classes = [AllowAny]
    template_name = 'raffle_detail.html'
    queryset = Raffle.objects.all()
    
    def get(self, request, *args, **kwargs):
        return super().get(request,*args, **kwargs)
    
    def additional_context(self):
        raffle = self.get_object()
        serializer= self.serializer_class(raffle)
        context={'raffle': raffle,
        'available_tickets': serializer.data.get('available_tickets'),
        'winners_drawn': serializer.data.get('winners_drawn')
        }
        return context
        
    def get_serializer_context(self):
        context=  super().get_serializer_context()
        context.update(self.additional_context())
        return context
    
    def get_context_data(self,**kwargs):
        context=  super().get_context_data(**kwargs)
        context.update(self.additional_context())
        return context