from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from carrito.models import Pedido
from gestion_empleados.models import Empleado


def gestion_pedidos(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)

    filtro = request.GET.get('estado')
    busqueda = request.GET.get('q')

    pedidos = Pedido.objects.select_related('cliente__persona').order_by('-fecha')

    if filtro:
        pedidos = pedidos.filter(estado=filtro)

    if busqueda:
        pedidos = pedidos.filter(
            Q(cliente__persona__nombre__icontains=busqueda) |
            Q(cliente__persona__primer_apellido__icontains=busqueda)
        )

    return render(request, 'gestion_pedidos.html', {
        'empleado': empleado,
        'pedidos': pedidos,
        'filtro': filtro,
        'busqueda': busqueda
    })

def ver_pedido(request, pedido_id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)
    pedido = get_object_or_404(Pedido.objects.select_related('cliente__persona').prefetch_related('detalles__producto', 'detalles__presentacion'), id=pedido_id)
    estados = Pedido._meta.get_field('estado').choices

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido._meta.get_field('estado').choices):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, "Estado actualizado correctamente.")
            return redirect('ver_pedido', pedido_id=pedido.id)

    return render(request, 'pedido.html', {
        'empleado': empleado,
        'pedido': pedido,
        'estados': estados
    })

#EMPLEADOS
def gestion_pedidos_empleados(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)

    filtro = request.GET.get('estado')
    busqueda = request.GET.get('q')

    pedidos = Pedido.objects.select_related('cliente__persona').order_by('-fecha')

    if filtro:
        pedidos = pedidos.filter(estado=filtro)

    if busqueda:
        pedidos = pedidos.filter(
            Q(cliente__persona__nombre__icontains=busqueda) |
            Q(cliente__persona__primer_apellido__icontains=busqueda)
        )

    return render(request, 'gestion_pedidos_empleados.html', {
        'empleado': empleado,
        'pedidos': pedidos,
        'filtro': filtro,
        'busqueda': busqueda
    })

def ver_pedido_empleados(request, pedido_id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)
    pedido = get_object_or_404(Pedido.objects.select_related('cliente__persona').prefetch_related('detalles__producto', 'detalles__presentacion'), id=pedido_id)
    estados = Pedido._meta.get_field('estado').choices

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido._meta.get_field('estado').choices):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, "Estado actualizado correctamente.")
            return redirect('ver_pedido_empleados', pedido_id=pedido.id)

    return render(request, 'pedido_empleados.html', {
        'empleado': empleado,
        'pedido': pedido,
        'estados': estados
    })