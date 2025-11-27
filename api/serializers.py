from rest_framework import serializers
from .models import Board, Card, List, Company
from api.models import User


class CompanySerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()
    boards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 
            'max_users', 'max_boards',
            'users_count', 'boards_count',
            'created_at'
        ]
        
    def get_users_count(self, obj):
        return obj.user.filter(is_active=True).count()
    
    def get_boards_count(self, obj):
        return obj.boards.count()


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name",'company', 'company_name', 'role']
        read_only_fields = ['id', 'company', 'company_name'] 
        
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
        
        def create(self, validated_data):
            password = validated_data.pop("password", None)
            user = User.objects.create(**validated_data)
            if password:
                user.set_password(password)
                user.save()
                
            return user

class CardSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )
    
    class Meta:
        model = Card
        fields = ["id", "title", "description", "position", "members", "created_at", "update_at"]


class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    
    class Meta:
        model = List
        fields = ["id", "title", "position", "board", "cards", "created_at"]
        read_only_fields = ["board", "position", "created_at"] 


class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Board
        fields = [
            "id", 
            "title", 
            "description", 
            "company",
            "company_name",
            "owner", 
            "priority",
            "priority_display",
            "start_date",
            "end_date",
            "lists", 
            "created_at", 
            "update_at"
        ]
        read_only_fields = ["created_at", "update_at", "company"]


# Serializer simplificado para listar projetos (sem as listas aninhadas)
class BoardListSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    cards_count = serializers.SerializerMethodField()
    lists_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = [
            "id", 
            "title", 
            "description",
            "owner",
            "priority",
            "priority_display",
            "start_date",
            "end_date",
            "cards_count",
            "lists_count",
            "created_at", 
            "update_at"
        ]
        read_only_fields = ["created_at", "update_at"]
    
    def get_cards_count(self, obj):
        """Conta total de cards em todas as listas do board"""
        return Card.objects.filter(list__board=obj).count()
    
    def get_lists_count(self, obj):
        """Conta total de listas no board"""
        return obj.lists.count()