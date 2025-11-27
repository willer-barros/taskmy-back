from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Board, List, Card, Company
from .serializers import BoardSerializer, BoardListSerializer, ListSerializer, CardSerializer, UserSerializer, CompanySerializer
from api.models import User


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes= [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = CompanySerializer
    
    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company_id)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        if not self.request.user.company:
            return User.objects.none()
        return User.objects.filter(company=self.request.user.company, is_active=True)
    
    def perform_create(self, serializer):
        if not self.request.user.is_company_admin():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Apenas Login admin pode criar usuários")
        
        company = self.request.user.company
        current_users = company.users.count()
        
        # if current_users >= company.max_users:
        #     from rest_framework.exceptions import ValidationError
        #     raise ValidationError(f"Limite de {company.max_users} usuários atingido")
        
        serializer.save(company=self.request.user.company)
        
    @action(detail=True, methods=['patch'])
    def change_role(self, request, pk=None):
        if not request.user.is_company_admin():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Apenas Login admin pode criar usuários")
        
        user = self.get_object()
        new_role = request.data.get("role")
        
        if new_role not in ['admin', 'manager', 'member']:
            return Response({'error': 'Role inválido'}, status=400)
    
    
        user.role = new_role
        user.save()
        
        return Response({'status': 'Role atualizado', 'role': new_role})
        
    # def get_serializer_class(self):
    #     return UserSerializer
    



class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_serializer_class(self):
        # Usa serializer leve para listagem
        if self.action == 'list':
            return BoardListSerializer
        return BoardSerializer
    
    def get_queryset(self):
        if not self.request.user.company:
            return Board.objects.none()
        return Board.objects.filter(company=self.request.user.company)
        
    
    def perform_create(self, serializer):
        company = self.request.user.company
        current_boards = company.boards.count()
        
        if current_boards >= company.max_boards:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Limite de {company.max_boards} projetos atingido")
        
        board = serializer.save(
            owner=self.request.user,
            company=self.request.user.company
        )
        
        List.objects.create(title="A Fazer", board=board, position=0)
        List.objects.create(title="Em Andamento", board=board, position=1)
        List.objects.create(title="Concluído", board=board, position=2)
        
        return board


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        board_pk = self.kwargs.get('board_pk')
        return List.objects.filter(
            board__id=board_pk, 
            board__owner=self.request.user
        ).prefetch_related('cards')  # Otimização
    
    def perform_create(self, serializer):
        board_pk = self.kwargs.get('board_pk')
        board = Board.objects.get(id=board_pk, owner=self.request.user)
        
        # Define posição automaticamente
        last_position = board.lists.count()
        serializer.save(board=board, position=last_position)
    
    @action(detail=True, methods=['patch'])
    def reorder(self, request, board_pk=None, pk=None):
        """Reordena a posição da lista"""
        list_obj = self.get_object()
        new_position = request.data.get('position')
        
        if new_position is not None:
            list_obj.position = new_position
            list_obj.save()
            return Response({'status': 'position updated'})
        
        return Response(
            {'error': 'position is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        list_pk = self.kwargs.get("list_pk")
        return Card.objects.filter(
            list__id=list_pk, 
            list__board__owner=self.request.user
        ).select_related('list').prefetch_related('members')  # Otimização
    
    def perform_create(self, serializer):
        list_pk = self.kwargs.get("list_pk")
        list_obj = List.objects.get(
            id=list_pk, 
            board__owner=self.request.user
        )
        
        # Define posição automaticamente
        last_position = list_obj.cards.count()
        card = serializer.save(list=list_obj, position=last_position)
        
        # Adiciona o usuário atual como membro
        card.members.add(self.request.user)
        
        return card
    
    @action(detail=True, methods=['patch'])
    def move(self, request, board_pk=None, list_pk=None, pk=None):
        """Move o card para outra lista e/ou reordena"""
        card = self.get_object()
        new_list_id = request.data.get('list_id')
        new_position = request.data.get('position')
        
        if new_list_id:
            # Verifica se a nova lista pertence ao mesmo board e usuário
            new_list = List.objects.get(
                id=new_list_id,
                board__owner=self.request.user
            )
            card.list = new_list
        
        if new_position is not None:
            card.position = new_position
        
        card.save()
        
        serializer = self.get_serializer(card)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, board_pk=None, list_pk=None, pk=None):
        """Adiciona um membro ao card"""
        card = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            from api.models import User
            user = User.objects.get(id=user_id)
            card.members.add(user)
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, board_pk=None, list_pk=None, pk=None):
        """Remove um membro do card"""
        card = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            from api.models import User
            user = User.objects.get(id=user_id)
            card.members.remove(user)
            return Response({'status': 'member removed'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )