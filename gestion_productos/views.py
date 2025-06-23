from idlelib.rpc import request_queue
from sys import prefix

from django.shortcuts import render, redirect, get_object_or_404

from gestion_empleados.models import Empleado
from gestion_productos.forms import PrecioProductoFormSet, ProductoBaseForm
from gestion_productos.models import Producto, PrecioProducto


def gestion_productos(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    productos = Producto.objects.all().order_by('nombre')
    for producto in productos:
        precios = PrecioProducto.objects.filter(producto=producto)
        producto.precios = precios  # ← Esto crea un atributo temporal
    return render(request, 'Productos.html', {'empleado': empleado,'productos': productos})


def nuevo_producto(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    if request.method == 'POST':
        form = ProductoBaseForm(request.POST, request.FILES)
        formset = PrecioProductoFormSet(request.POST, instance=Producto(), prefix='precios')

        if form.is_valid() and formset.is_valid():
            producto = form.save()
            formset.instance = producto
            formset.save()
            return redirect('gestProductos')
        else:
            print(form.errors)
            print(formset.errors)
    else:
        form = ProductoBaseForm()
        formset = PrecioProductoFormSet(instance=Producto(), prefix='precios')

    return render(request, 'nuevoProducto.html', {
        'empleado': empleado,
        'form': form,
        'formset': formset,
        'titulo': 'Nuevo Producto'
    })


def editar_producto(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    producto = get_object_or_404(Producto, pk=id)

    if request.method == 'POST':
        form = ProductoBaseForm(request.POST, request.FILES, instance=producto)
        formset = PrecioProductoFormSet(request.POST, instance=producto, prefix='precios')

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('gestProductos')
    else:
        form = ProductoBaseForm(instance=producto)
        formset = PrecioProductoFormSet(instance=producto, prefix='precios')

    return render(request, 'editarProducto.html', {
        'empleado': empleado,
        'form': form,
        'formset': formset,
        'producto': producto,
        'titulo': 'Editar Producto'
    })


def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    producto.delete()  # Esto debería eliminar en cascada los PrecioProducto
    return redirect('gestProductos')

