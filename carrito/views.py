import json
import os
from io import BytesIO

import mercadopago
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string, get_template
from carrito.models import DetallePedido, Pedido
from cuenta.models import Cliente
from gestion_productos.models import Presentacion, Producto, PrecioProducto
from django.utils import timezone
from xhtml2pdf import pisa

def agregar_al_carrito(request):
    if request.method == 'POST':
        try:
            precio_producto_id = int(request.POST.get('precio_producto_id'))
            cantidad = int(request.POST.get('cantidad', 1))
            nota = request.POST.get('nota', '')

            precio_producto = PrecioProducto.objects.select_related('producto', 'presentacion').get(
                id=precio_producto_id)

            # Estructura del item del carrito
            item = {
                'precio_producto_id': precio_producto.id,
                'producto_id': precio_producto.producto.id,
                'producto_nombre': precio_producto.producto.nombre,
                'presentacion_id': precio_producto.presentacion.id,
                'presentacion_nombre': precio_producto.presentacion.nombre,
                'precio': float(precio_producto.precio),
                'cantidad': cantidad,
                'nota': nota,
                'imagen': precio_producto.producto.imagen.url if precio_producto.producto.imagen else '',
            }

            # Obtener carrito actual de la sesión o crear uno nuevo
            carrito = request.session.get('carrito', [])

            # Verificar si el producto con la misma presentación ya está en el carrito
            item_existente = next(
                (i for i in carrito if i['precio_producto_id'] == precio_producto.id),
                None
            )

            if item_existente:
                item_existente['cantidad'] += cantidad
                if nota:
                    item_existente['nota'] = nota
            else:
                carrito.append(item)

            # Guardar carrito en la sesión
            request.session['carrito'] = carrito
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'cart_count': len(carrito),
                'message': 'Producto agregado al carrito'
            })

        except (ValueError, PrecioProducto.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'message': 'Error al agregar producto al carrito: ' + str(e)
            }, status=400)

    return JsonResponse({'success': False}, status=400)


def carrito(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('credenciales')

    carrito = request.session.get('carrito', [])
    for item in carrito:
        item['subtotal'] = item['precio'] * item['cantidad']
    # Calcular totales
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)
    print(subtotal)
    envio = 8000  # Valor fijo de ejemplo
    total = subtotal + envio

    return render(request, 'carrito.html', {
        'items': carrito,
        'subtotal': subtotal,
        'envio': envio,
        'total': total,
        'costo_envio': 8000  # Nuevo valor para JavaScript
    })


def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', [])
        item = next((i for i in carrito if i['precio_producto_id'] == item_id), None)

        if item:
            try:
                nueva_cantidad = int(request.POST.get('cantidad'))
                if nueva_cantidad > 0:
                    item['cantidad'] = nueva_cantidad
                    item['subtotal'] = item['precio'] * nueva_cantidad
                    request.session['carrito'] = carrito
                    request.session.modified = True

                    # Calcular nuevo subtotal general
                    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)

                    return JsonResponse({
                        'success': True,
                        'subtotal': item['subtotal'],
                        'cart_subtotal': subtotal,
                        'cart_count': len(carrito)
                    })
            except ValueError:
                pass

    return JsonResponse({'success': False}, status=400)


def eliminar_item(request, item_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', [])
        carrito = [item for item in carrito if item['precio_producto_id'] != item_id]
        request.session['carrito'] = carrito
        request.session.modified = True

        # Calcular nuevo subtotal general
        subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)

        return JsonResponse({
            'success': True,
            'cart_count': len(carrito),
            'subtotal': subtotal
        })

    return JsonResponse({'success': False}, status=400)

def limpiar_carrito(request):
    if request.method == 'POST':
        if 'carrito' in request.session:
            del request.session['carrito']
            request.session.modified = True
        return JsonResponse({
            'success': True,
            'cart_count': 0
        })
    return JsonResponse({'success': False}, status=400)


def iniciar_pago(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    carrito = request.session.get('carrito', [])

    if not carrito:
        return JsonResponse({'error': 'El carrito está vacío'}, status=400)

    # Obtener datos del cuerpo JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al leer los datos'}, status=400)

    metodo_envio = data.get('delivery')  # 'domicilio' o 'recoger'
    request.session['metodo_envio'] = metodo_envio
    # Calcular subtotal
    subtotal = sum(float(item['precio']) * int(item['cantidad']) for item in carrito)

    # Calcular costo de envío (8000 si es domicilio, 0 si es recoger)
    costo_envio = 8000 if metodo_envio == 'domicilio' else 0
    total = subtotal + costo_envio

    # Construir descripción detallada
    descripcion = "\n".join(
        f"{item['producto_nombre']} - {item['presentacion_nombre']} "
        f"(Cant: {item['cantidad']}, Precio: ${float(item['precio']):,})"
        for item in carrito
    )

    # Agregar info de envío a la descripción
    descripcion += f"\n\nMétodo de entrega: {'Domicilio (+$8,000)' if metodo_envio == 'domicilio' else 'Recoger en tienda'}"
    BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
    preference_data = {
        "items": [{
        "title": "Compra en Pastelería Morita",
            "quantity": 1,
            "unit_price": total,  # Ya incluye el envío si fue seleccionado
            "currency_id": "COP",
            "description": descripcion,
        }],
    "back_urls": {
            "success": f"{BASE_URL}/carrito/pago-exitoso/",
            "failure": f"{BASE_URL}/productos/",
            "pending": f"{BASE_URL}/"
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    if "init_point" in preference:
        return JsonResponse({"init_point": preference["init_point"]})
    else:
        print("❌ Error en la respuesta de Mercado Pago:", preference)
        return JsonResponse({"error": "No se pudo generar el enlace de pago"}, status=500)


def pago_exitoso(request):
    carrito = request.session.get('carrito', [])
    metodo_envio = request.session.get('metodo_envio', 'recoger')
    cliente_id = request.session.get('cliente_id')  # ← debe estar en la sesión tras login

    if not carrito or not cliente_id:
        messages.error(request, "No se encontró información del carrito o cliente.")
        return redirect('credenciales')

    try:
        cliente = Cliente.objects.get(id=cliente_id)

        # Calcular total
        subtotal = sum(float(item['precio']) * int(item['cantidad']) for item in carrito)
        costo_envio = 8000 if metodo_envio == 'domicilio' else 0
        total = subtotal + costo_envio

        # Crear pedido
        pedido = Pedido.objects.create(
            cliente=cliente,
            fecha=timezone.now(),
            metodo_entrega=metodo_envio,
            direccion_entrega=cliente.direccion.calle if metodo_envio == 'domicilio' else "",
            costo_envio=costo_envio,
            total=total,
            estado='pagado'
        )

        # Crear detalles del pedido
        for item in carrito:
            producto = Producto.objects.get(id=item['producto_id'])
            presentacion = Presentacion.objects.get(id=item['presentacion_id'])

            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                presentacion=presentacion,
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                nota=item.get('nota', '')
            )
        generar_factura_y_enviar(request, pedido.id)
        # Vaciar carrito y limpiar datos temporales

        request.session['carrito'] = []
        request.session.pop('metodo_envio', None)

        messages.success(request, "¡Pago exitoso! Tu pedido ha sido registrado.")
        return redirect('pagPrincipal')

    except Exception as e:
        print("❌ Error al registrar el pedido:", e)
        messages.error(request, "Ocurrió un error al guardar el pedido.")
        return redirect('pagPrincipal')

def generar_factura_y_enviar(request, pedido_id):
    pedido = Pedido.objects.select_related('cliente__persona').prefetch_related('detalles__producto', 'detalles__presentacion').get(id=pedido_id)

    # Convertir a lista para poder añadir campo personalizado
    detalles = list(pedido.detalles.all())
    for detalle in detalles:
        detalle.subtotal = detalle.precio_unitario * detalle.cantidad

    # Renderizar plantilla HTML con subtotales
    template = get_template('factura_pdf.html')
    html = template.render({
        'pedido': pedido,
        'detalles': detalles  # Pasamos los detalles modificados
    })

    # Generar PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    buffer.seek(0)
    pdf_file = buffer.read()

    # Enviar por correo
    email = EmailMessage(
        subject='Factura de tu compra - Pastelería Morita',
        body='Adjuntamos tu factura en PDF. ¡Gracias por tu compra!',
        from_email='pasteleriamorita3@gmail.com',
        to=[pedido.cliente.persona.correo],
    )
    email.attach(f'factura_pedido_{pedido.id}.pdf', pdf_file, 'application/pdf')
    email.send()

    return HttpResponse('Factura generada y enviada correctamente.')