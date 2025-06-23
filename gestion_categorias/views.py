from django.shortcuts import render, redirect, get_object_or_404

from gestion_categorias.forms import CategoriaForm, CategoriaEditarForm
from gestion_empleados.models import Empleado
from gestion_productos.models import Categoria


def gestion_categorias(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    query = request.GET.get('q')
    if query:
        categorias = Categoria.objects.filter(nombre__icontains=query)
    else:
        categorias = Categoria.objects.order_by('id')
    return render(request, 'Categorias.html', {'empleado': empleado, 'categorias': categorias})

def nueva_categoria(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')
    empleado = Empleado.objects.get(id=empleado_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestCategorias')
    else:
        form = CategoriaForm()
    return render(request, 'nuevaCategoria.html', {'empleado': empleado, 'formCategoria': form})

def editar_categoria(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado_session = Empleado.objects.get(id=empleado_id)
    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == 'POST':
        form = CategoriaEditarForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('gestCategorias')
    else:
        form = CategoriaEditarForm(instance=categoria)

    return render(request, 'editarCategoria.html', {
        'empleado': empleado_session,
        'formCategoria': form,
        'categoria_editar': categoria
    })

def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    if categoria:
        categoria.delete()
    return redirect('gestCategorias')