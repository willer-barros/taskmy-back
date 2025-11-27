from api.models import Company, User
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

def setup_company(company_name, admin_username, admin_email, admin_password):
    """Cria uma empresa e seu administrador inicial"""
    
    # Criar empresa
    company = Company.objects.create(
        name=company_name,
        slug=company_name.lower().replace(' ', '-'),
        max_users=10,
        max_boards=5
    )
    
    # Criar usuário admin
    admin = User.objects.create_user(
        username=admin_username,
        email=admin_email,
        password=admin_password,
        company=company,
        role='admin'
    )
    
    print(f"✅ Empresa '{company_name}' criada!")
    print(f"✅ Admin '{admin_username}' criado!")
    # print(f"🔑 Token: {Token.objects.create(user=admin).key}")
    
    return company, admin

# Usar assim:
# setup_company("Minha Empresa", "admin", "admin@minhaempresa.com", "senha123")