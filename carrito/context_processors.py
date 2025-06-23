def cart_count(request):
    carrito = request.session.get('carrito', [])
    return {
        'cart_count': len(carrito)
    }