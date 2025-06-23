from django.contrib import admin

from cuenta.models import Departamento, Municipio, Direccion, Cliente

admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Direccion)
admin.site.register(Cliente)