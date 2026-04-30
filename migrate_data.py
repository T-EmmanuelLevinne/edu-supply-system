import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_supply_store.settings')
django.setup()

from orders.models import Order, OrderItem

orders = Order.objects.all()
count = 0
for order in orders:
    if not order.items.exists():
        OrderItem.objects.create(
            order=order,
            product=order.product,
            quantity=order.quantity,
            price=order.product.price
        )
        count += 1

print(f"Successfully migrated {count} orders to OrderItems.")
