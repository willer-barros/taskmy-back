from rest_framework import serializers
from .models import Board, Card, List
from api.models import User

class CardSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        read_only = True,
        slug_field="username"
    )
    
    class Meta:
        model = Card
        fields = ["id", "title", "description", "position", "due_date", "members"]
        
class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    
    class Meta:
        model = List
        fields = ["id", "title", "position", "board", "cards"]
        
        
class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Board
        fields = ["id", "title", "description", "owner", "lists", "created_at", "updated_at"]