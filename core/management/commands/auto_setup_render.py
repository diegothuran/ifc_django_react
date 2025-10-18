from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os


class Command(BaseCommand):
    """
    Comando para configuração automática no Render.
    
    Este comando é executado automaticamente durante o deploy no Render
    para configurar dados iniciais sem intervenção manual.
    
    Uso:
    python manage.py auto_setup_render
    """
    
    help = 'Configuração automática para deploy no Render'
    
    def handle(self, *args, **options):
        """Função principal do comando."""
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando configuração automática para Render...')
        )
        
        # Verificar se estamos em ambiente de produção
        is_production = os.getenv('RENDER', False) or os.getenv('DJANGO_ENV') == 'production'
        auto_setup_enabled = os.getenv('AUTO_SETUP_DATA', 'true').lower() == 'true'
        
        if is_production:
            self.stdout.write(
                self.style.SUCCESS('🌐 Ambiente de produção detectado (Render)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('💻 Ambiente de desenvolvimento detectado')
            )
        
        try:
            # Executar migrações
            self.stdout.write('📊 Executando migrações...')
            call_command('migrate', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('✅ Migrações executadas com sucesso')
            )
            
            # Coletar arquivos estáticos
            self.stdout.write('📁 Coletando arquivos estáticos...')
            call_command('collectstatic', '--noinput', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('✅ Arquivos estáticos coletados')
            )
            
            # Configurar dados iniciais (apenas se não existirem)
            if auto_setup_enabled:
                self.stdout.write('🔧 Configurando dados iniciais...')
                call_command('setup_initial_data', verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS('✅ Dados iniciais configurados')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⏭️ Setup automático de dados desabilitado (AUTO_SETUP_DATA=false)')
                )
            
            # Verificar status do banco
            self.check_database_status()
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Configuração automática concluída com sucesso!')
            )
            
            if is_production:
                self.stdout.write(
                    self.style.WARNING(
                        '\n📋 Informações de acesso:\n'
                        '• Admin: /admin/\n'
                        '• Usuário: admin\n'
                        '• Senha: admin123\n'
                        '• Dashboard: /dashboard/'
                    )
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante configuração: {str(e)}')
            )
            raise
    
    def check_database_status(self):
        """Verifica o status do banco de dados."""
        try:
            from django.db import connection
            
            # Obter lista de tabelas de forma compatível com todos os bancos
            table_names = connection.introspection.table_names()
            
            # Verificar se as tabelas principais existem
            required_tables = [
                'core_user',
                'plant_viewer_buildingplan',
                'sensor_management_sensor',
                'sensor_management_sensordata'
            ]
            
            existing_tables = [table for table in required_tables if table in table_names]
            
            if len(existing_tables) >= 4:
                self.stdout.write(
                    self.style.SUCCESS('✅ Banco de dados configurado corretamente')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'   Tabelas encontradas: {len(table_names)}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Algumas tabelas podem estar faltando ({len(existing_tables)}/4)')
                )
                self.stdout.write(
                    self.style.WARNING(f'   Tabelas encontradas: {existing_tables}')
                )
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Não foi possível verificar o banco: {e}')
            )
