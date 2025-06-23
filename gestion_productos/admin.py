from django.contrib import admin

from gestion_productos.models import Producto, Categoria, Presentacion, PrecioProducto, ReviewProducto

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Presentacion)
admin.site.register(PrecioProducto)
admin.site.register(ReviewProducto)
