from django.contrib import messages
from django.shortcuts import render, redirect

from carrito.models import Pedido
from cuenta.models import Cliente
from gestion_productos.models import ReviewProducto, Producto


# Create your views here.
def historial_pedidos(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('credenciales')  # Redirige si no hay sesión

    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return redirect('credenciales')

    pedidos = Pedido.objects.filter(cliente=cliente) \
        .prefetch_related(
        'detalles',  # accede a los detalles
        'detalles__producto',  # accede al producto del detalle
        'detalles__presentacion'  # accede a la presentación del detalle
    ) \
        .order_by('-fecha')
    for pedido in pedidos:
        for detalle in pedido.detalles.all():
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario

    return render(request, 'historial_pedidos.html', {
        'cliente': cliente,
        'pedidos': pedidos
    })

def crear_review(request):
    if request.method == 'POST':
        cliente_id = request.session.get('cliente_id')
        if not cliente_id:
            return redirect('credenciales')

        try:
            producto_id = request.POST.get('producto_id')
            calificacion = int(request.POST.get('calificacion'))
            comentario = request.POST.get('comentario', '')

            cliente = Cliente.objects.get(id=cliente_id)
            producto = Producto.objects.get(id=producto_id)

            review, created = ReviewProducto.objects.update_or_create(
                producto=producto,
                cliente=cliente,
                defaults={
                    'calificacion': calificacion,
                    'comentario': comentario
                }
            )

            messages.success(request, '¡Gracias por tu reseña!')
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return redirect('historial_pedidos')  # o la vista que tengas para el historial