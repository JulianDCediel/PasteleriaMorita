import string
import uuid
from datetime import timedelta
from random import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from cuenta.models import Cliente
from gestion_empleados.models import Persona
from recuperacion_clave.models import TokenRecuperacion

def recuperar_clave(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            persona = Persona.objects.get(correo=email)
            cliente = Cliente.objects.get(persona=persona)

            token = str(uuid.uuid4())
            expiracion = timezone.now() + timedelta(minutes=30)

            TokenRecuperacion.objects.create(
                cliente=cliente,
                token=token,
                expiracion=expiracion
            )

            url = request.build_absolute_uri(
                reverse('CambiarClave', args=[token])
            )

            send_mail(
                subject='Restablecimiento de contraseña - Pastelería Morita',
                message=f'Hola {persona.nombre}, haz clic en el siguiente enlace para cambiar tu contraseña:\n\n{url}\n\nSi no solicitaste este cambio, ignora este mensaje.\n\nGracias,\nPastelería Morita',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )

            messages.success(request, 'Se envió un enlace para restablecer tu contraseña al correo registrado.')
        except (Persona.DoesNotExist, Cliente.DoesNotExist):
            messages.error(request, 'No encontramos una cuenta con ese correo.')
    return render(request, 'restablecer.html')

def cambiar_clave(request, token):
    try:
        token_obj = TokenRecuperacion.objects.get(token=token)
    except TokenRecuperacion.DoesNotExist:
        messages.error(request, 'El enlace de recuperación es inválido.')
        return redirect('credenciales')

    if not token_obj.es_valido():
        messages.error(request, 'El enlace de recuperación ha expirado.')
        return redirect('credenciales')

    if request.method == 'POST':
        nueva = request.POST.get('new_password1')
        confirmar = request.POST.get('new_password2')
        if nueva == confirmar:
            token_obj.cliente.contraseña = make_password(nueva)
            token_obj.cliente.save()
            token_obj.delete()  # Eliminar token luego de usarlo
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('credenciales')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')

    return render(request, 'cambiar.html', {'token': token})