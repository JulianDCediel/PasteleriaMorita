from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=150)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.primer_apellido}"

# Tabla para tipos de usuario (admin, empleado)
class TipoUsuario(models.Model):
    tipo = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'id:{self.id} tipo:{self.tipo}'

# Tabla principal de productos
class Empleado(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    contraseña = models.CharField(max_length=128)
    tipo_usuario = models.ForeignKey('TipoUsuario', on_delete=models.PROTECT)

    def __str__(self):
        return f" {self.persona.nombre} {self.persona.primer_apellido}"

