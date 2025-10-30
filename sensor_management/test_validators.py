"""
Testes para validators do sensor_management.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from sensor_management.models import validate_sensor_ip


class SensorValidatorTests(TestCase):
    """Testes para os validators de sensor."""
    
    def test_validate_sensor_ip_valid_ipv4(self):
        """Testa validação de IP IPv4 válido."""
        valid_ips = [
            '192.168.1.1',
            '10.0.0.1',
            '172.16.0.1',
            '8.8.8.8',
        ]
        
        for ip in valid_ips:
            try:
                validate_sensor_ip(ip)
            except ValidationError:
                self.fail(f"IP válido {ip} não deveria gerar erro")
    
    def test_validate_sensor_ip_valid_ipv6(self):
        """Testa validação de IP IPv6 válido."""
        valid_ips = [
            '::1',
            '2001:db8::1',
            'fe80::1',
        ]
        
        for ip in valid_ips:
            try:
                validate_sensor_ip(ip)
            except ValidationError:
                self.fail(f"IP válido {ip} não deveria gerar erro")
    
    def test_validate_sensor_ip_invalid(self):
        """Testa validação de IP inválido."""
        invalid_ips = [
            '256.256.256.256',
            '192.168.1',
            'not-an-ip',
            '192.168.1.1.1',
            '',
        ]
        
        for ip in invalid_ips:
            with self.assertRaises(ValidationError):
                validate_sensor_ip(ip)
    
    def test_validate_sensor_ip_localhost(self):
        """Testa validação de IP localhost."""
        # Loopback IPs são permitidos (para desenvolvimento)
        loopback_ips = [
            '127.0.0.1',
            '::1',
        ]
        
        for ip in loopback_ips:
            try:
                validate_sensor_ip(ip)
            except ValidationError:
                self.fail(f"IP loopback {ip} não deveria gerar erro")

