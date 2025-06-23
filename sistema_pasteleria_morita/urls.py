"""
URL configuration for sistema_pasteleria_morita project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


from carrito.views import carrito, agregar_al_carrito, actualizar_cantidad, eliminar_item, limpiar_carrito, \
    iniciar_pago, pago_exitoso
from credenciales_clientes.views import credenciales, get_municipios
from cuenta.views import mi_cuenta
from gestion_categorias.views import gestion_categorias, nueva_categoria, eliminar_categoria, editar_categoria
from gestion_empleados.views import gestion_empleados, nuevo_empleado, \
    editar_empleado, eliminar_empleado
from gestion_finanzas.views import gestion_finanzas, generar_informe_financiero
from gestion_pedidos.views import gestion_pedidos, ver_pedido, gestion_pedidos_empleados, ver_pedido_empleados
from gestion_presentacion.views import gestion_presentacion, nueva_presentacion, editar_presentacion, \
    eliminar_presentacion
from historial_pedidos.views import historial_pedidos, crear_review
from login.views import Ingreso
from menu_administracion.views import menu_admin
from menu_empleados.views import menu_empleado
from gestion_productos.views import gestion_productos, nuevo_producto, eliminar_producto, editar_producto
from nosotros.views import nosotros
from recuperacion_clave.views import recuperar_clave, cambiar_clave
from sistema_pasteleria_morita import settings
from django.contrib.auth import views as auth_views

from web_principal.views import web_principal
from web_productos.views import web_productos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('loginEmp', Ingreso, name='LoginEmp'),
    path('principalAdmin', menu_admin, name='prinAdmins'),
    path('logout/', auth_views.LogoutView.as_view(next_page='LoginEmp'), name='logout'),
    path('principalEmp', menu_empleado, name='prinEmps'),
    path('gestionEmpleados', gestion_empleados, name='gestEmpleados'),
    path('agregarEmpleado', nuevo_empleado, name='nuevoEmpleado'),
    path('eliminarEmpleado/<int:id>', eliminar_empleado),
    path('editarEmpleado/<int:id>', editar_empleado),
    path('gestionProductos', gestion_productos, name='gestProductos'),
    path('agregarProductos', nuevo_producto, name='nuevoProducto'),
    path('eliminarProducto/<int:id>', eliminar_producto),
    path('editarProducto/<int:id>', editar_producto),
    path('gestion_categorias', gestion_categorias, name='gestCategorias'),
    path('agregarCategoria', nueva_categoria, name='nuevaCategoria'),
    path('editarCategoria/<int:id>', editar_categoria),
    path('eliminarCategoria/<int:id>', eliminar_categoria),
    path('gestion_presentacion', gestion_presentacion, name='gestPresentacion'),
    path('agregarPresentacion', nueva_presentacion, name='nuevaPresentacion'),
    path('editarPresentacion/<int:id>', editar_presentacion),
    path('eliminarPresentacion/<int:id>', eliminar_presentacion),
    path('pedidos', gestion_pedidos, name='gestion_pedidos'),
    path('pedido/<int:pedido_id>', ver_pedido, name='ver_pedido'),
    path('finanzas', gestion_finanzas, name='gestion_finanzas'),
    path('informe', generar_informe_financiero, name='generar_informe_financiero'),
    path('pedidos_empleados', gestion_pedidos_empleados, name='gestion_pedidos_empleados'),
    path('pedido_empleados/<int:pedido_id>', ver_pedido_empleados, name='ver_pedido_empleados'),

# URLS CLIENTES
    path('', web_principal, name='pagPrincipal'),
    path('productos', web_productos, name='pagProductos'),
    path('credenciales', credenciales, name='credenciales'),
    path('get_municipios/',get_municipios, name='get_municipios'),
    path('mi_cuenta',mi_cuenta, name='mi_cuenta'),
    path('nosotros', nosotros, name='nosotros'),
    path('carrito', carrito, name='carrito'),
    path('recuperarClave', recuperar_clave, name='recuperarClave'),
    path('CambiarClave/<str:token>/', cambiar_clave, name='CambiarClave'),
#carrito
    path('carrito/agregar/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', eliminar_item, name='eliminar_item'),
    path('carrito/limpiar/', limpiar_carrito, name='limpiar_carrito'),
    path('carrito/iniciar-pago/', iniciar_pago, name='iniciar_pago'),
    path('carrito/pago-exitoso/', pago_exitoso, name='pago_exitoso'),
#pedidos
    path('mis_pedidos', historial_pedidos, name='historial_pedidos'),
    path('crear-review', crear_review, name='crear_review'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
