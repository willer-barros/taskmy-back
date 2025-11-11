from django.contrib import admin
from .models import Board, List, Card # Seus modelos

# --- Configuração do Board ---
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    # Campos que aparecem na lista de Boards (no painel do Admin)
    list_display = ('title', 'end_date', 'id')
    
    # Adiciona um campo de pesquisa para filtrar por título
    search_fields = ('title',)
    
    # Adiciona filtros laterais (se houver campos ForeignKey ou BooleanField)
    # list_filter = ('is_active',) 


# --- Configuração da List (Coluna) ---
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    # Mostra o título da lista e a qual Board ela pertence
    list_display = ('title', 'board')
    
    # Permite filtrar as listas por Board
    list_filter = ('board',)
    
# --- Configuração do Card (Tarefa) ---
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    # Exibe título, descrição (truncada) e a qual List pertence
    list_display = ('title', 'description', 'list') 
    