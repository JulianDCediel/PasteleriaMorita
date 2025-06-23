from django.utils import timezone

from django.db import models

from cuenta.models import Cliente


class TokenRecuperacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    expiracion = models.DateTimeField()

    def es_valido(self):
        return timezone.now() <= self.expiracion

    def __str__(self):
        return f"Token para {self.cliente.persona.nombre} - válido hasta {self.expiracion}"