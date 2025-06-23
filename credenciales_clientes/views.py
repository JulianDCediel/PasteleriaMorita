from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from cuenta.models import Departamento, Municipio, Direccion, Persona, Cliente
from .forms import ClienteLoginForm, ClienteRegistroForm


def credenciales(request):
    departamentos = Departamento.objects.all()

    if request.method == 'POST':
        form_id = request.POST.get('form_id')

        if form_id == 'loginForm':
            login_form = ClienteLoginForm(request.POST)
            if login_form.is_valid():

                correo = login_form.cleaned_data['correo']
                password = login_form.cleaned_data['password']

                try:
                    persona = Persona.objects.get(correo=correo)
                    cliente = Cliente.objects.get(persona=persona)

                    if check_password(password, cliente.contraseña):
                        request.session['cliente_id'] = cliente.id
                        messages.success(request, f'Bienvenido {persona.nombre}!')
                        return redirect('pagPrincipal')
                except (Persona.DoesNotExist, Cliente.DoesNotExist):
                    pass

                messages.error(request, 'Correo o contraseña incorrectos')
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario')

            return render(request, 'credenciales.html', {
                'departamentos': departamentos,
                'login_form': login_form,
                'register_form': ClienteRegistroForm()
            })

        elif form_id == 'registerForm':
            register_form = ClienteRegistroForm(request.POST)
            if register_form.is_valid():
                try:
                    register_form.save()
                    messages.success(request, 'Registro exitoso! Por favor inicia sesión')
                    return redirect('credenciales')
                except Exception as e:
                    messages.error(request, f'Error al registrar: {str(e)}')
                    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            else:
                for field, errors in register_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

            return render(request, 'credenciales.html', {
                'departamentos': departamentos,
                'login_form': ClienteLoginForm(),
                'register_form': register_form
            })

    return render(request, 'credenciales.html', {
        'departamentos': departamentos,
        'login_form': ClienteLoginForm(),
        'register_form': ClienteRegistroForm()
    })


def get_municipios(request):
    departamento_id = request.GET.get('departamento_id')
    municipios = Municipio.objects.filter(departamento_id=departamento_id).values('id', 'nombre')
    return JsonResponse({'municipios': list(municipios)})