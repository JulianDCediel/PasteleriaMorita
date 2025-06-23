from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import redirect, render

from cuenta.forms import EditarClienteForm
from cuenta.models import Cliente, Municipio, Departamento


def mi_cuenta(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('credenciales')

    cliente = Cliente.objects.select_related(
        'persona',
        'direccion__municipio__departamento'
    ).get(id=cliente_id)

    departamentos = Departamento.objects.all()
    municipios = Municipio.objects.filter(departamento=cliente.direccion.municipio.departamento)

    if request.method == 'POST':
        form = EditarClienteForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Actualizar persona
                    cliente.persona.nombre = form.cleaned_data['nombre']
                    cliente.persona.primer_apellido = form.cleaned_data['primer_apellido']
                    cliente.persona.segundo_apellido = form.cleaned_data['segundo_apellido']
                    cliente.persona.correo = form.cleaned_data['correo']
                    cliente.persona.save()

                    # Actualizar cliente
                    cliente.telefono = form.cleaned_data['telefono']

                    # Actualizar contraseña si se proporcionó
                    if form.cleaned_data['password']:
                        cliente.contraseña = make_password(form.cleaned_data['password'])

                    cliente.save()

                    # Actualizar dirección
                    municipio = Municipio.objects.get(id=form.cleaned_data['municipio'])
                    cliente.direccion.municipio = municipio
                    cliente.direccion.calle = form.cleaned_data['calle']
                    cliente.direccion.save()

                    messages.success(request, 'Tus datos se han actualizado correctamente', extra_tags='edit')
                    return redirect('mi_cuenta')

            except Exception as e:
                messages.error(request, f'Ocurrió un error al actualizar tus datos: {str(e)}', extra_tags='edit')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}', extra_tags='edit')

    context = {
        'cliente': cliente,
        'departamentos': departamentos,
        'municipios': municipios
    }
    return render(request, 'micuenta.html', context)
