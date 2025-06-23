from django.db import models
from django.utils import timezone

from cuenta.models import Cliente
from gestion_productos.models import Producto, Presentacion


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    metodo_entrega = models.CharField(max_length=20, choices=[
        ('domicilio', 'Domicilio'),
        ('recoger', 'Recoger en tienda')
    ])
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
    ], default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    presentacion = models.ForeignKey(Presentacion, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    nota = models.TextField(blank=True)

    def __str__(self):
        return f"{self.producto.nombre} ({self.presentacion.nombre}) x{self.cantidad}"