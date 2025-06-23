from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from gestion_empleados.forms import EmpleadoEditarForm
from gestion_empleados.models import Empleado, Persona
from login.forms import PersonaForm, EmpleadoForm



def gestion_empleados(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado_sesion = Empleado.objects.get(id=empleado_id)
    query = request.GET.get('q')

    if query:
        # Buscar por nombre o apellido de la persona asociada
        empleados = Empleado.objects.filter(
            persona__nombre__icontains=query) | Empleado.objects.filter(
            persona__primer_apellido__icontains=query)
    else:
        empleados = Empleado.objects.select_related('persona').order_by('id')

    return render(request, 'Empleados.html', {
        'empleado': empleado_sesion,
        'empleados': empleados
    })


def nuevo_empleado(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado_sesion = Empleado.objects.get(id=empleado_id)

    if request.method == 'POST':
        persona_form = PersonaForm(request.POST)
        empleado_form = EmpleadoForm(request.POST)

        if persona_form.is_valid() and empleado_form.is_valid():
            # Guardar primero la persona
            persona = persona_form.save()
            # Luego el empleado con referencia a la persona
            empleado = empleado_form.save(commit=False)
            empleado.persona = persona
            empleado.save()
            return redirect('gestEmpleados')
    else:
        persona_form = PersonaForm()
        empleado_form = EmpleadoForm()

    return render(request, 'nuevoEmpleado.html', {
        'empleado': empleado_sesion,
        'persona_form': persona_form,
        'empleado_form': empleado_form
    })


def editar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado_sesion = Empleado.objects.get(id=empleado_id)
    empleado = get_object_or_404(Empleado, pk=id)

    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=empleado.persona)
        empleado_form = EmpleadoEditarForm(request.POST, instance=empleado)

        if persona_form.is_valid() and empleado_form.is_valid():
            persona_form.save()
            empleado_form.save()
            return redirect('gestEmpleados')
    else:
        persona_form = PersonaForm(instance=empleado.persona)
        empleado_form = EmpleadoEditarForm(instance=empleado)

    return render(request, 'editarEmpleado.html', {
        'empleado': empleado_sesion,
        'persona_form': persona_form,
        'empleado_form': empleado_form,
        'empleado_editar': empleado
    })


def eliminar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = get_object_or_404(Empleado, pk=id)
    if empleado:
        # Eliminamos también la persona asociada
        persona = empleado.persona
        empleado.delete()
        persona.delete()

    return redirect('gestEmpleados')