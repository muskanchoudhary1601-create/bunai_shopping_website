from .cart import Cart
from .models import Category


def cart_context(request):
    """Provides the shopping cart and active categories to all customer-facing templates."""
    return {
        'cart': Cart(request),
        'global_categories': Category.objects.all(),
    }
