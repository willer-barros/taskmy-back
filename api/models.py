from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings


class Company(models.Model):
    """Empresa"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=True)
    is_active = models.BooleanField(default=True)
    
    # max_users = models.IntegerField(default=10)
    # max_boards = models.IntegerField(default=5)
    
    class Meta:
        verbose_name_plural = "Companies"
        
    def __str__(self):
        return self.name


class User(AbstractUser):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('member', 'Membro'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member"
    )
    
    def is_company_admin(self):
        return self.role == "admin"
    
    def __str__(self):
        return f"{self.username} ({self.company.name if self.company else 'Sem empresa'})"


class Board(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="boards",null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boards")
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"
    
    class Meta:
        ordering = ['-created_at']
    
class List(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.title} in {self.board.title}"
    
    class Meta:
        ordering = ['position']
    
class Card(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="cards")
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_cards', blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['position']
    