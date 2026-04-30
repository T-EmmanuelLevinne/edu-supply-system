from .models import Cart

def cart_processor(request):
    cart_item_count = 0
    cart = None
    if request.user.is_authenticated:
        # Assuming the customer is linked to the user
        try:
            customer = request.user.customer
            cart = Cart.objects.filter(customer=customer).first()
            if cart:
                cart_item_count = sum(item.quantity for item in cart.items.all())
        except AttributeError:
            # User has no customer profile
            pass
            
    return {'cart_item_count': cart_item_count, 'cart': cart}
