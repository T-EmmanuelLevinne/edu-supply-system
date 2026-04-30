from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm

def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')
    price_filter = request.GET.get('price')
    rating_filter = request.GET.get('rating')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category=category)
        
    deals = request.GET.get('deals')
    if deals == 'true':
        products = products.filter(is_on_sale=True)
        
    if price_filter == 'under_50':
        products = products.filter(price__lt=50)
    elif price_filter == '50_100':
        products = products.filter(price__gte=50, price__lte=100)
    elif price_filter == 'over_100':
        products = products.filter(price__gt=100)
        
    if rating_filter == '4_up':
        products = products.filter(rating__gte=4.0)
    elif rating_filter == '3_up':
        products = products.filter(rating__gte=3.0)
        
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'rating_desc':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')
        
    paginator = Paginator(products, 8) # 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = [c[0] for c in Product.CATEGORY_CHOICES]
    
    wishlisted_product_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        wishlisted_product_ids = request.user.customer.wishlist.values_list('id', flat=True)
    
    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'query': query,
        'current_sort': sort,
        'current_price': price_filter,
        'current_rating': rating_filter,
        'wishlisted_product_ids': wishlisted_product_ids,
    })

@login_required
def toggle_wishlist(request, pk):
    from django.http import JsonResponse
    product = get_object_or_404(Product, pk=pk)
    
    if request.user.is_staff:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Staff cannot use wishlist'})
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

    if not hasattr(request.user, 'customer'):
        from customers.models import Customer
        Customer.objects.create(user=request.user)

    status = 'added'
    if product in request.user.customer.wishlist.all():
        request.user.customer.wishlist.remove(product)
        status = 'removed'
    else:
        request.user.customer.wishlist.add(product)
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status})
    
    # Redirect back to where the user came from
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        from .models import Review
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        product.update_rating()
        return redirect('products:product_detail', pk=pk)
        
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def delete_review(request, pk):
    if not request.user.is_staff:
        return redirect('products:product_list')
    from .models import Review
    review = get_object_or_404(Review, pk=pk)
    product = review.product
    if request.method == 'POST':
        review.delete()
        product.update_rating()
        return redirect('products:product_detail', pk=product.pk)
    return render(request, 'products/confirm_delete_review.html', {'review': review})

def delivery_info(request):
    return render(request, 'products/delivery.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('products:product_list')
    
    products_count = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10)
    
    from django.contrib.auth.models import User
    from orders.models import Order
    users_count = User.objects.count()
    orders_count = Order.objects.count()
    
    # Bottom Product Table logic
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    
    all_products = Product.objects.all().order_by('-created_at')
    if query:
        all_products = all_products.filter(name__icontains=query)
    if category_filter:
        all_products = all_products.filter(category=category_filter)
        
    categories = [c[0] for c in Product.CATEGORY_CHOICES]
    
    return render(request, 'products/admin_dashboard.html', {
        'products_count': products_count,
        'low_stock_products': low_stock_products,
        'users_count': users_count,
        'orders_count': orders_count,
        'all_products': all_products,
        'categories': categories,
        'query': query,
        'current_category': category_filter
    })

@login_required
def product_create(request):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'action': 'Create'})

@login_required
def product_update(request, pk):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'action': 'Update'})

@login_required
def product_delete(request, pk):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products:product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def wishlist_view(request):
    if hasattr(request.user, 'customer'):
        products = request.user.customer.wishlist.all()
    else:
        products = []
        
    wishlisted_product_ids = [p.id for p in products]
    
    return render(request, 'products/wishlist.html', {
        'products': products,
        'wishlisted_product_ids': wishlisted_product_ids
    })

def product_search_api(request):
    from django.http import JsonResponse
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    # Return top 5 matches
    products = Product.objects.filter(name__icontains=query)[:5]
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'image_url': p.image.url if p.image else '',
            'url': p.get_absolute_url()
        })
    return JsonResponse({'results': results})
