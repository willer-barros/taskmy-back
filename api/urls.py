from django.urls import path
from .views import BoardViewSet, ListViewSet, CardViewSet
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # URLs para Board
    path('boards/', BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list'),
    path('boards/<int:pk>/', BoardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='board-detail'),
    
    # URLs para List (aninhadas em Board)
    path('boards/<int:board_pk>/lists/', ListViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list-list'),
    path('boards/<int:board_pk>/lists/<int:pk>/', ListViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='board-list-detail'),
    
    # URLs para Card (aninhadas em List)
    path('boards/<int:board_pk>/lists/<int:list_pk>/cards/', CardViewSet.as_view({'get': 'list', 'post': 'create'}), name='list-card-list'),
    path('boards/<int:board_pk>/lists/<int:list_pk>/cards/<int:pk>/', CardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='list-card-detail'),
    
    # URLs para mover o card
    path('boards/<int:board_pk>/lists/<int:list_pk>/cards/<int:pk>/move/', CardViewSet.as_view({'patch': 'move'}), name='list-card-move'),
    
    #URL de auth
    path("auth-token/", obtain_auth_token, name="auth-token")
]
