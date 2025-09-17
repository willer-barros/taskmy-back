from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Board, List, Card
from .serializers import BoardSerializer, ListSerializer, CardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.boards.all()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
        
        
class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        board_pk = self.kwargs['board_pk']
        return List.objects.filter(board__id=board_pk, board__owner=self.request.user)
    
    
class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        list_pk = self.kwargs["list_pk"]
        return Card.objects.filter(list__id=list_pk, list__board__owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(members=[self.request.user])