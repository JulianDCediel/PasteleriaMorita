import base64
from io import BytesIO

import matplotlib
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, F, Avg
from datetime import datetime

import calendar
from collections import defaultdict

from django.template.loader import get_template, render_to_string
from django.utils.timezone import now
from xhtml2pdf import pisa

from carrito.models import DetallePedido, Pedido
from gestion_empleados.models import Empleado
import matplotlib.pyplot as plt
matplotlib.use('Agg')


def gestion_finanzas(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)
    current_year = now().year
    estados_validos = ['pagado', 'en_camino', 'entregado']

    # Filtros por mes/año
    mes = request.GET.get('mes')
    año = request.GET.get('año', current_year)

    # Consulta base
    pedidos = Pedido.objects.filter(estado__in=estados_validos)

    if año:
        pedidos = pedidos.filter(fecha__year=año)
    if mes:
        pedidos = pedidos.filter(fecha__month=mes)

    # Ingresos mensuales (año actual)
    ingresos_mensuales = pedidos.annotate(
        mes=F('fecha__month')
    ).values('mes').annotate(
        total=Sum('total')
    ).order_by('mes')

    # Ingresos mensuales (año anterior)
    ingresos_anterior = Pedido.objects.filter(
        estado__in=estados_validos,
        fecha__year=int(año) - 1
    ).annotate(
        mes=F('fecha__month')
    ).values('mes').annotate(
        total=Sum('total')
    ).order_by('mes')

    # Datos para gráficos
    meses_data = [calendar.month_name[i] for i in range(1, 13)]
    ingresos_data = [0] * 12
    ingresos_data_anterior = [0] * 12

    for item in ingresos_mensuales:
        ingresos_data[item['mes'] - 1] = float(item['total'])

    for item in ingresos_anterior:
        ingresos_data_anterior[item['mes'] - 1] = float(item['total'])

    # Totales y promedios
    total_ingresos = pedidos.aggregate(Sum('total'))['total__sum'] or 0
    total_pedidos = pedidos.count()
    promedio = pedidos.aggregate(Avg('total'))['total__avg'] or 0

    # Productos más vendidos
    productos_top = DetallePedido.objects.filter(
        pedido__estado__in=estados_validos
    ).values(
        'producto__nombre'
    ).annotate(
        unidades=Sum('cantidad'),
        ingresos=Sum(F('precio_unitario') * F('cantidad'))
    ).order_by('-ingresos')[:10]

    # Presentaciones más vendidas
    presentaciones_top = DetallePedido.objects.filter(
        pedido__estado__in=estados_validos
    ).values(
        'producto__nombre', 'presentacion__nombre'
    ).annotate(
        unidades=Sum('cantidad'),
        ingresos=Sum(F('precio_unitario') * F('cantidad'))
    ).order_by('-ingresos')[:10]

    # Datos para gráficos de comparación
    labels_productos = [p['producto__nombre'] for p in productos_top]
    data_productos = [float(p['ingresos']) for p in productos_top]

    labels_presentaciones = [
        f"{p['producto__nombre']} - {p['presentacion__nombre']}"
        for p in presentaciones_top
    ]
    data_presentaciones = [float(p['ingresos']) for p in presentaciones_top]
    # Para productos
    productos_top = list(productos_top)  # Convertir a lista para poder modificarlo
    for producto in productos_top:
        producto['porcentaje'] = (producto['ingresos'] / total_ingresos * 100) if total_ingresos else 0

    # Para presentaciones
    presentaciones_top = list(presentaciones_top)
    for presentacion in presentaciones_top:
        presentacion['porcentaje'] = (presentacion['ingresos'] / total_ingresos * 100) if total_ingresos else 0

    context = {
        'empleado': empleado,
        'meses': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'años': range(current_year - 2, current_year + 1),
        'mes': int(mes) if mes else None,
        'año': int(año) if año else current_year,
        'total_ingresos': total_ingresos,
        'total_pedidos': total_pedidos,
        'promedio': promedio,
        'productos_top': productos_top,
        'presentaciones_top': presentaciones_top,
        'labels': meses_data,
        'datos': ingresos_data,
        'datos_anterior': ingresos_data_anterior,
        'labels_productos': labels_productos,
        'data_productos': data_productos,
        'labels_presentaciones': labels_presentaciones,
        'data_presentaciones': data_presentaciones,
    }

    return render(request, 'gestion_finanzas.html', context)

def generar_informe_financiero(request):
    año = int(request.GET.get('año', datetime.now().year))
    mes = request.GET.get('mes')

    pedidos = Pedido.objects.filter(estado__in=['pagado', 'en_camino', 'entregado'])
    if mes:
        pedidos = pedidos.filter(fecha__year=año, fecha__month=int(mes))
    else:
        pedidos = pedidos.filter(fecha__year=año)

    detalles = DetallePedido.objects.filter(pedido__in=pedidos).select_related('producto', 'presentacion')

    ingresos = sum(p.total for p in pedidos)
    total_pedidos = pedidos.count()
    ingreso_promedio = ingresos / total_pedidos if total_pedidos > 0 else 0

    # Gráfica 1: Ingresos por producto
    productos = {}
    for detalle in detalles:
        key = detalle.producto.nombre
        productos[key] = productos.get(key, 0) + detalle.precio_unitario * detalle.cantidad

    fig1, ax1 = plt.subplots()
    ax1.bar(productos.keys(), productos.values(), color='salmon')
    ax1.set_title('Comparación entre Productos')
    ax1.set_ylabel('Ingresos ($)')
    ax1.tick_params(axis='x', rotation=90)
    buffer1 = BytesIO()
    plt.tight_layout()
    fig1.savefig(buffer1, format='png')
    buffer1.seek(0)
    graph_productos = base64.b64encode(buffer1.read()).decode('utf-8')
    plt.close(fig1)

    # Gráfica 2: Ingresos por presentación
    presentaciones = {}
    for detalle in detalles:
        key = f"{detalle.producto.nombre} - {detalle.presentacion.nombre}"
        presentaciones[key] = presentaciones.get(key, 0) + detalle.precio_unitario * detalle.cantidad

    fig2, ax2 = plt.subplots()
    ax2.bar(presentaciones.keys(), presentaciones.values(), color='lightblue')
    ax2.set_title('Comparación entre Presentaciones')
    ax2.set_ylabel('Ingresos ($)')
    ax2.tick_params(axis='x', rotation=90)
    buffer2 = BytesIO()
    plt.tight_layout()
    fig2.savefig(buffer2, format='png')
    buffer2.seek(0)
    graph_presentaciones = base64.b64encode(buffer2.read()).decode('utf-8')
    plt.close(fig2)

    # Render HTML
    html = render_to_string('informe_financiero_pdf.html', {
        'año': año,
        'mes': mes,
        'pedidos': pedidos,
        'detalles': detalles,
        'ingresos': ingresos,
        'total_pedidos': total_pedidos,
        'ingreso_promedio': ingreso_promedio,
        'graph_productos': graph_productos,
        'graph_presentaciones': graph_presentaciones
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_financiero.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response