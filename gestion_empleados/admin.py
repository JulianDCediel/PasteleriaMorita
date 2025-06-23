from django.contrib import admin

from gestion_empleados.models import TipoUsuario, Empleado, Persona

admin.site.register(Persona)
admin.site.register(TipoUsuario)
admin.site.register(Empleado)

