from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect

from gestion_empleados.models import Persona, Empleado
from login.forms import LoginEmpleadoForm


def Ingreso(request):
    error = None
    if request.method == 'POST':
        form = LoginEmpleadoForm(request.POST)
        if form.is_valid():
            correo_input = form.cleaned_data['correo']
            contraseña_input = form.cleaned_data['contraseña']

            try:
                # Buscamos la persona por correo y luego el empleado asociado
                persona = Persona.objects.get(correo=correo_input)
                empleado = Empleado.objects.get(persona=persona)

                if check_password(contraseña_input, empleado.contraseña):
                    # Guardar sesión
                    request.session['empleado_id'] = empleado.id
                    tipo = empleado.tipo_usuario.tipo.lower()

                    # Redirigir según el tipo
                    if tipo == "admin":
                        return redirect('prinAdmins')
                    elif tipo == "empleado":
                        return redirect('prinEmps')
                    else:
                        error = "Tipo de usuario no reconocido"
                else:
                    error = "Contraseña incorrecta"
            except (Persona.DoesNotExist, Empleado.DoesNotExist):
                error = "Empleado no encontrado"
    else:
        form = LoginEmpleadoForm()

    return render(request, 'ingreso.html', {'form': form, 'error': error})

