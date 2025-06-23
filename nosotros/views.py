from django.shortcuts import render, redirect

from cuenta.models import Cliente


def nosotros(request):
    cliente_id = request.session.get('cliente_id')
    return render(request, 'nosotros.html', {'cliente': cliente_id})
