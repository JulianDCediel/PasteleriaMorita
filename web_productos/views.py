from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404

from gestion_productos.models import Producto, Categoria, PrecioProducto, ReviewProducto


def web_productos(request):
    query = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    orden = request.GET.get('orden', 'nuevos')

    # Obtener todos los productos
    productos = Producto.objects.all()

    # Búsqueda por nombre
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Filtrar por categoría
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Ordenar productos
    if orden == 'nombre':
        productos = productos.order_by('nombre')
    else:  # nuevos primero (por defecto)
        productos = productos.order_by('-id')

    # Paginación
    paginator = Paginator(productos, 6)
    page_number = request.GET.get('page')
    productos_paginados = paginator.get_page(page_number)

    # Agregar precios asociados a cada producto
    for producto in productos_paginados:
        producto.precios = PrecioProducto.objects.filter(producto=producto)

        promedio = ReviewProducto.objects.filter(producto=producto).aggregate(avg=Avg('calificacion'))['avg']
        producto.calificacion_promedio = round(promedio, 1) if promedio else 0

    categorias = Categoria.objects.all()
    cliente_id = request.session.get('cliente_id')

    return render(request, 'web_productos.html', {
        'productos': productos_paginados,
        'categorias': categorias,
        'cliente_autenticado': bool(cliente_id)
    })

