from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.timezone import now

from carrito.models import Pedido
from gestion_empleados.models import Empleado
from gestion_productos.models import Producto


def menu_admin(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('LoginEmp')

    empleado = Empleado.objects.get(id=empleado_id)

    # Pedidos del día
    hoy = now()

    pedidos_hoy = Pedido.objects.filter(fecha__date=hoy).count()


    # Productos activos (por ahora se cuenta todos, puedes filtrar por estado si lo implementas)
    productos_activos = Producto.objects.count()

    # Ingresos del mes
    mes_actual = now().month
    ingresos_mes = Pedido.objects.filter(
        fecha__month=mes_actual,
        estado__in=['pagado', 'en_camino', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0

    # Últimos 5 pedidos
    pedidos_recientes = Pedido.objects.select_related('cliente__persona').order_by('-fecha')[:5]


    context = {
        'empleado': empleado,
        'pedidos_hoy': pedidos_hoy,
        'productos_activos': productos_activos,
        'ingresos_mes': ingresos_mes,
        'pedidos_recientes': pedidos_recientes,
    }

    return render(request, 'menu_admin.html', context)