from django.contrib import admin
from .models import Board, List, Card, Company

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'end_date', 'id')
    search_fields = ('title',)
    
    
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('title', 'board')
    list_filter = ('board',)
    
    
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'list') 
    