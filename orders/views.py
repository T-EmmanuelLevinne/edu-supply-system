from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from products.models import Product
from .forms import OrderForm, OrderStatusForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile') # Need profile to order
        
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.customer
            
            quantity = form.cleaned_data.get('quantity', 1)
            
            # Base price calculation
            from decimal import Decimal
            order.total_price = product.price * quantity
            
            if order.order_type == 'Room Delivery':
                order.delivery_fee = Decimal('5.00')
                order.total_price += order.delivery_fee
            else:
                order.delivery_fee = Decimal('0.00')
                order.delivery_date = None
                order.delivery_time = None
                order.want_it_now = False
                order.delivery_details = ''
            
            order.save()
            
            from .models import OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            return redirect('orders:view_receipt', pk=order.pk)
    else:
        initial_qty = request.GET.get('quantity', 1)
        form = OrderForm(initial={'quantity': initial_qty})
        
    return render(request, 'orders/place_order.html', {'form': form, 'product': product})

@login_required
def order_history(request):
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile')
        
    orders_list = Order.objects.filter(customer=request.user.customer).order_by('-order_date')
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'orders/order_history.html', {'page_obj': page_obj})

@login_required
def manage_orders(request):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    status_filter = request.GET.get('status')
    query = request.GET.get('q', '')
    
    orders_list = Order.objects.all().order_by('-order_date')
    
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)
        
    if query:
        from django.db.models import Q
        orders_list = orders_list.filter(
            Q(customer__user__first_name__icontains=query) |
            Q(customer__user__last_name__icontains=query) |
            Q(customer__student_id__icontains=query) |
            Q(id__icontains=query)
        )
        
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'orders/manage_orders.html', {
        'page_obj': page_obj,
        'current_status': status_filter,
        'query': query,
        'statuses': [s[0] for s in Order.STATUS_CHOICES]
    })

@login_required
def update_order_status(request, pk):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    order = get_object_or_404(Order, pk=pk)
    old_status = order.status
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            new_order = form.save(commit=False)
            
            # Logic: If it wasn't completed before, but now IS completed, decrease stock
            if old_status != 'Completed' and new_order.status == 'Completed':
                for item in new_order.items.all():
                    if item.product.stock >= item.quantity:
                        item.product.stock -= item.quantity
                        item.product.save()
                # If stock < quantity, in a real system we'd show an error, but let's assume staff verified.
            
            new_order.save()
            return redirect('orders:manage_orders')
    else:
        form = OrderStatusForm(instance=order)
        
    return render(request, 'orders/update_status.html', {'form': form, 'order': order})

@login_required
def delete_order(request, pk):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('orders:manage_orders')
    return render(request, 'orders/confirm_delete.html', {'order': order})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user.customer)
    if order.status != 'Pending':
        return redirect('orders:order_history')
        
    from .forms import CancelOrderForm
    if request.method == 'POST':
        form = CancelOrderForm(request.POST, instance=order)
        if form.is_valid():
            cancelled_order = form.save(commit=False)
            cancelled_order.status = 'Cancelled'
            cancelled_order.save()
            return redirect('orders:order_history')
    else:
        form = CancelOrderForm(instance=order)
    return render(request, 'orders/cancel_order.html', {'form': form, 'order': order})

@login_required
def view_receipt(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Restrict to owner or staff
    if not request.user.is_staff and order.customer != request.user.customer:
        return redirect('orders:order_history')
    
    # Calculate claim date (skip weekends) for 3 business days
    from datetime import timedelta
    
    claim_date = order.order_date
    days_to_add = 3
    while days_to_add > 0:
        claim_date += timedelta(days=1)
        if claim_date.weekday() < 5:  # 0=Mon, 4=Fri
            days_to_add -= 1
            
    return render(request, 'orders/receipt.html', {'order': order, 'claim_date': claim_date})

@login_required
def cart_view(request):
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile')
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    if not hasattr(request.user, 'customer'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'redirect': '/customers/profile/'})
        return redirect('customers:profile')
        
    product = get_object_or_404(Product, pk=product_id)
    if product.stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': f'{product.name} is out of stock.'})
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
        
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if not item_created:
            new_quantity = cart_item.quantity + qty
            cart_item.quantity = min(new_quantity, product.stock)
        else:
            cart_item.quantity = min(qty, product.stock)
    else:
        if not item_created:
            new_quantity = cart_item.quantity + 1
            cart_item.quantity = min(new_quantity, product.stock)
            
    cart_item.save()
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = sum(i.quantity for i in cart.items.all())
        from django.template.loader import render_to_string
        cart_html = render_to_string('orders/hover_cart_partial.html', {'cart': cart, 'cart_item_count': cart_count}, request=request)
        return JsonResponse({
            'status': 'success', 
            'cart_count': cart_count, 
            'message': f'Added {product.name} to cart',
            'cart_html': cart_html
        })
        
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

@login_required
def remove_from_cart(request, item_id):
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile')
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__customer=request.user.customer)
    cart_item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = request.user.customer.cart
        cart_count = sum(i.quantity for i in cart.items.all())
        from django.template.loader import render_to_string
        cart_html = render_to_string('orders/hover_cart_partial.html', {'cart': cart, 'cart_item_count': cart_count}, request=request)
        return JsonResponse({'status': 'success', 'cart_count': cart_count, 'cart_html': cart_html})
        
    return redirect('orders:cart_view')

@login_required
def update_cart_item(request, item_id, action):
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile')
        
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__customer=request.user.customer)
    
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
                messages.error(request, f"Cannot add more {cart_item.product.name}. Only {cart_item.product.stock} in stock.")
            else:
                return JsonResponse({'status': 'error', 'message': f"Cannot add more. Only {cart_item.product.stock} in stock."})
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = request.user.customer.cart
        cart_count = sum(i.quantity for i in cart.items.all())
        from django.template.loader import render_to_string
        cart_html = render_to_string('orders/hover_cart_partial.html', {'cart': cart, 'cart_item_count': cart_count}, request=request)
        return JsonResponse({'status': 'success', 'cart_count': cart_count, 'cart_html': cart_html})
            
    return redirect('orders:cart_view')

@login_required
def cart_checkout_page(request):
    if not hasattr(request.user, 'customer'):
        return redirect('customers:profile')
        
    if request.method == 'POST':
        selected_item_ids = request.POST.getlist('selected_items')
        if not selected_item_ids:
            messages.error(request, "Please select at least one item to checkout.")
            return redirect('orders:cart_view')
            
        items = CartItem.objects.filter(id__in=selected_item_ids, cart__customer=request.user.customer)
        if not items.exists():
            messages.error(request, "Invalid items selected.")
            return redirect('orders:cart_view')
            
        request.session['checkout_items'] = selected_item_ids
        subtotal = sum(item.get_total_price() for item in items)
        
        form = OrderForm()
        # Create a mock order to use with place_order.html if needed, or pass items.
        return render(request, 'orders/cart_checkout.html', {
            'form': form,
            'items': items,
            'subtotal': subtotal
        })
        
    return redirect('orders:cart_view')

@login_required
def checkout_cart(request):
    if request.method == 'POST':
        selected_item_ids = request.session.get('checkout_items', [])
        if not selected_item_ids:
            return redirect('orders:cart_view')
            
        items = CartItem.objects.filter(id__in=selected_item_ids, cart__customer=request.user.customer)
        if not items.exists():
            return redirect('orders:cart_view')
            
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.customer
            
            from decimal import Decimal
            subtotal = sum(item.get_total_price() for item in items)
            order.total_price = subtotal
            
            if order.order_type == 'Room Delivery':
                order.delivery_fee = Decimal('5.00')
                order.total_price += order.delivery_fee
            else:
                order.delivery_fee = Decimal('0.00')
                order.delivery_date = None
                order.delivery_time = None
                order.want_it_now = False
                order.delivery_details = ''
                
            order.save()
            
            from .models import OrderItem
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                
            items.delete()
            if 'checkout_items' in request.session:
                del request.session['checkout_items']
            
            messages.success(request, "Your selected items have been successfully checked out!")
            return redirect('orders:view_receipt', pk=order.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
                    
    return redirect('orders:cart_view')

import json

@login_required
def delivery_dashboard(request):
    if not hasattr(request.user, 'customer') or not request.user.customer.is_delivery_staff:
        return redirect('products:product_list')
        
    # Show Pending orders (excluding Store Pickup) and orders accepted by this staff that are Processing
    pending_orders = Order.objects.filter(status='Pending').exclude(order_type='Store Pickup').order_by('-order_date')
    my_processing_orders = Order.objects.filter(status='Processing', accepted_by=request.user.customer).order_by('-order_date')
    
    return render(request, 'orders/delivery_dashboard.html', {
        'pending_orders': pending_orders,
        'my_processing_orders': my_processing_orders
    })

@login_required
def delivery_accept(request, order_id):
    if not hasattr(request.user, 'customer') or not request.user.customer.is_delivery_staff:
        return redirect('products:product_list')
        
    order = get_object_or_404(Order, pk=order_id, status='Pending')
    if order.order_type == 'Store Pickup':
        messages.error(request, "Cannot accept Store Pickup orders.")
        return redirect('orders:delivery_dashboard')
        
    order.status = 'Processing'
    order.accepted_by = request.user.customer
    order.save()
    messages.success(request, f"You have accepted Order #{order.id}.")
    return redirect('orders:delivery_dashboard')

@login_required
def delivery_cancel(request, order_id):
    if not hasattr(request.user, 'customer') or not request.user.customer.is_delivery_staff:
        return redirect('products:product_list')
        
    order = get_object_or_404(Order, pk=order_id)
    if order.status in ['Pending', 'Processing']:
        order.status = 'Cancelled'
        order.cancel_reason = 'Cancelled by Delivery Staff'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
        
    return redirect('orders:delivery_dashboard')

@login_required
def delivery_scan(request, order_id):
    if not hasattr(request.user, 'customer') or not request.user.customer.is_delivery_staff:
        return redirect('products:product_list')
        
    order = get_object_or_404(Order, pk=order_id, status='Processing', accepted_by=request.user.customer)
    return render(request, 'orders/delivery_scan.html', {'order': order})

@login_required
def delivery_complete(request, order_id):
    if not hasattr(request.user, 'customer') or not request.user.customer.is_delivery_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data', '')
            
            order = get_object_or_404(Order, pk=order_id, status='Processing', accepted_by=request.user.customer)
            expected_qr = f"ORD-{order.id}"
            
            if qr_data == expected_qr:
                order.status = 'Completed'
                order.save()
                
                # Decrease stock since order is completed
                for item in order.items.all():
                    if item.product.stock >= item.quantity:
                        item.product.stock -= item.quantity
                        item.product.save()
                        
                return JsonResponse({'status': 'success', 'message': f'Order #{order.id} marked as Completed!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid QR Code for this order.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def order_search_api(request):
    if not request.user.is_staff:
        return JsonResponse({'results': []}, status=403)
        
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
        
    from django.db.models import Q
    orders_list = Order.objects.filter(
        Q(customer__user__first_name__icontains=query) |
        Q(customer__user__last_name__icontains=query) |
        Q(customer__student_id__icontains=query) |
        Q(id__icontains=query)
    ).order_by('-order_date')[:5]
    
    results = []
    for o in orders_list:
        results.append({
            'id': o.id,
            'status': o.status,
            'customer': f"{o.customer.user.first_name} {o.customer.user.last_name}",
            'student_id': o.customer.student_id,
            'url': f"/orders/{o.id}/status/"
        })
    return JsonResponse({'results': results})
