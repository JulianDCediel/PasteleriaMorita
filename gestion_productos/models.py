from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from cuenta.models import Cliente


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='categorias/', null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos/')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')


    def __str__(self):
        return self.nombre

# Modelo de presentación (porción, tamaño 10, etc.)
class Presentacion(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# Relación entre producto y presentación con precio
class PrecioProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    presentacion = models.ForeignKey(Presentacion, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'presentacion')  # Evita duplicados

    def __str__(self):
        return f"{self.producto.nombre} - {self.presentacion.nombre}: ${self.precio}"


class ReviewProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # o tu modelo de usuario
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('producto', 'cliente')  # Un cliente puede dejar una reseña por producto

    def __str__(self):
        return f"{self.producto.nombre} - {self.calificacion}⭐ por {self.cliente}"