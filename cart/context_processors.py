from .cart import Cart

# Create context processor so out cart can work on all pages

def cart(request):
    return {'cart':Cart(request)}
