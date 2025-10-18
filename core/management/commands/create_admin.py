from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria um superusuário admin com senha aleatória'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username para o superusuário (padrão: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha para o superusuário (se não informada, será gerada automaticamente)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = f'{username}@ifcmonitoring.com'
        
        # Gera senha aleatória se não fornecida
        if options['password']:
            password = options['password']
        else:
            # Gera senha com 12 caracteres incluindo letras, números e símbolos
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Usuário "{username}" já existe!')
            )
            return
        
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='IFC Monitoring'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuário "{username}" criado com sucesso!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Senha: {password}\n'
                    f'⚠️  IMPORTANTE: Salve estas credenciais em local seguro!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar superusuário: {e}')
            )
