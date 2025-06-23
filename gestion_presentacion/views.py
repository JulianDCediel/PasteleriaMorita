from django.shortcuts import render, redirect, get_object_or_404

from gestion_empleados.models import Empleado
from gestion_presentacion.forms import PresentacionForm, PresentacionEditarForm
from gestion_productos.models import Presentacion


def gestion_presentacion(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    query = request.GET.get('q')
    if query:
        presentacion = Presentacion.objects.filter(nombre__icontains=query)
    else:
        presentacion = Presentacion.objects.order_by('id')
    return render(request, 'Presentacion.html', {'empleado': empleado, 'presentaciones': presentacion})

def nueva_presentacion(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    if request.method == 'POST':
        form = PresentacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestPresentacion')
    else:
        form = PresentacionForm()
    return render(request, 'nuevaPresentacion.html', {'empleado': empleado, 'formPresentacion': form})

def editar_presentacion(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado_session = Empleado.objects.get(id=empleado_id)
    presentacion = get_object_or_404(Presentacion, pk=id)

    if request.method == 'POST':
        form = PresentacionEditarForm(request.POST, request.FILES, instance=presentacion)
        if form.is_valid():
            form.save()
            return redirect('gestPresentacion')
    else:
        form = PresentacionEditarForm(instance=presentacion)

    return render(request, 'editarPresentacion.html', {
        'empleado': empleado_session,
        'formPresentacion': form,
        'presentacion_editar': presentacion
    })

def eliminar_presentacion(request, id):
    categoria = get_object_or_404(Presentacion, pk=id)
    if categoria:
        categoria.delete()
    return redirect('gestPresentacion')
