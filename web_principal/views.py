from django.db.models import Avg
from django.shortcuts import render

from gestion_productos.models import Categoria, Producto, PrecioProducto, ReviewProducto


def web_principal(request):
    categorias = Categoria.objects.all()[:4]  # Limita a 4 categorías
    productos_destacados = Producto.objects.all().order_by('id')[:3]  # 3 productos destacados
    for producto in productos_destacados:
        precios = PrecioProducto.objects.filter(producto=producto)
        producto.precios = precios  # ← Esto crea un atributo temporal
        promedio = ReviewProducto.objects.filter(producto=producto).aggregate(avg=Avg('calificacion'))['avg']
        producto.calificacion_promedio = round(promedio, 1) if promedio else 0

    cliente_id = request.session.get('cliente_id')
    return render(request, 'web_principal.html', {
        'categorias': categorias,
        'productos': productos_destacados,
        'cliente_autenticado': bool(cliente_id)
    })