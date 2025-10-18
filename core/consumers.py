"""
WebSocket Consumers para comunicação em tempo real
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from sensor_management.models import Sensor, SensorData, SensorAlert


class SensorDataConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações em tempo real de dados de sensores
    """
    
    async def connect(self):
        """Conectar ao WebSocket"""
        self.room_group_name = 'sensor_updates'
        
        # Adicionar ao grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Enviar mensagem de boas-vindas
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Conectado ao sistema de monitoramento em tempo real'
        }))
    
    async def disconnect(self, close_code):
        """Desconectar do WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receber mensagem do cliente"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Responder ao ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            
            elif message_type == 'subscribe_sensor':
                # Inscrever em atualizações de um sensor específico
                sensor_id = data.get('sensor_id')
                # Implementar lógica de subscrição específica se necessário
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'sensor_id': sensor_id
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensagem inválido'
            }))
    
    async def sensor_update(self, event):
        """
        Receber atualização de sensor do grupo e enviar para o cliente
        """
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data']
        }))
    
    async def alert_created(self, event):
        """
        Receber novo alerta do grupo e enviar para o cliente
        """
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data']
        }))


class PlantViewerConsumer(AsyncWebsocketConsumer):
    """
    Consumer para visualizador 3D de plantas
    Permite interação em tempo real com o modelo 3D
    """
    
    async def connect(self):
        """Conectar ao WebSocket"""
        self.plant_id = self.scope['url_route']['kwargs'].get('plant_id')
        self.room_group_name = f'plant_{self.plant_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Desconectar do WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receber mensagem do cliente"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'element_selected':
                # Broadcast seleção de elemento para outros usuários
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'element_selected',
                        'element_id': data.get('element_id'),
                        'user': self.scope['user'].username if self.scope['user'].is_authenticated else 'Anônimo'
                    }
                )
        
        except json.JSONDecodeError:
            pass
    
    async def element_selected(self, event):
        """Broadcast de seleção de elemento"""
        await self.send(text_data=json.dumps({
            'type': 'element_selected',
            'element_id': event['element_id'],
            'user': event['user']
        }))


# Funções auxiliares para enviar atualizações do Django
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def broadcast_sensor_update(sensor_id, data):
    """
    Enviar atualização de sensor para todos os clientes conectados
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'sensor_updates',
        {
            'type': 'sensor_update',
            'data': {
                'sensor_id': sensor_id,
                'value': data.get('value'),
                'unit': data.get('unit'),
                'timestamp': data.get('timestamp'),
                'quality': data.get('quality', 100)
            }
        }
    )


def broadcast_alert(alert):
    """
    Enviar novo alerta para todos os clientes conectados
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'sensor_updates',
        {
            'type': 'alert_created',
            'data': {
                'id': alert.id,
                'sensor_id': alert.sensor.id,
                'sensor_name': alert.sensor.name,
                'message': alert.message,
                'severity': alert.level if hasattr(alert, 'level') else 'warning',
                'created_at': alert.created_at.isoformat() if hasattr(alert, 'created_at') else alert.timestamp.isoformat()
            }
        }
    )

