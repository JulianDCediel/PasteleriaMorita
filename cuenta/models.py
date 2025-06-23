from django.db import models
from gestion_empleados.models import Persona


class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"

class Direccion(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    calle = models.CharField(max_length=255)  # o nombre_via, etc.

    def __str__(self):
        return f"{self.calle}, {self.municipio}"


class Cliente(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    numero_documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15)
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT)
    contraseña = models.CharField(max_length=128)

    def __str__(self):
        return str(self.persona)

