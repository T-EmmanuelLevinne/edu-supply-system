from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, CustomerForm
from .models import Customer

def register(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')
        
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            customer = customer_form.save(commit=False)
            customer.middle_name = user_form.cleaned_data.get('middle_name')
            customer.user = user
            customer.save()
            login(request, user)
            return redirect('products:product_list')
    else:
        user_form = UserRegistrationForm()
        customer_form = CustomerForm()
    return render(request, 'customers/register.html', {
        'user_form': user_form,
        'customer_form': customer_form
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('products:product_list')
    else:
        form = AuthenticationForm()
        
    form.fields['username'].label = "Username or Email"
    return render(request, 'customers/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('products:product_list')
    # If GET, you might want to show a confirm page or just redirect
    logout(request)
    return redirect('products:product_list')

@login_required
def profile(request):
    target_user_id = request.GET.get('user')
    if target_user_id and request.user.is_staff:
        from django.contrib.auth.models import User
        target_user = get_object_or_404(User, id=target_user_id)
        try:
            customer = target_user.customer
        except Customer.DoesNotExist:
            customer = None
    else:
        target_user = request.user
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = None

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=target_user)
        user_form.fields['password'].required = False
        user_form.fields['password_confirm'].required = False
        
        if customer:
            customer_form = CustomerForm(request.POST, instance=customer)
        else:
            customer_form = CustomerForm(request.POST)
            
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data.get('password'):
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            cust = customer_form.save(commit=False)
            cust.middle_name = user_form.cleaned_data.get('middle_name')
            cust.user = user
            cust.save()
            
            if target_user == request.user and user_form.cleaned_data.get('password'):
                login(request, user)
            
            if target_user_id and request.user.is_staff:
                 return redirect('customers:customer_list')
            return redirect('customers:profile')
    else:
        user_form = UserRegistrationForm(instance=target_user)
        if target_user and hasattr(target_user, 'customer'):
            user_form.fields['middle_name'].initial = target_user.customer.middle_name
        user_form.fields['password'].required = False
        user_form.fields['password_confirm'].required = False
        if customer:
            customer_form = CustomerForm(instance=customer)
        else:
            customer_form = CustomerForm()
            
    return render(request, 'customers/profile.html', {
        'user_form': user_form,
        'customer_form': customer_form
    })

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('products:product_list')
    return render(request, 'customers/confirm_delete.html')

@login_required
def customer_list(request):
    if not request.user.is_staff:
        return redirect('products:product_list')
        
    query = request.GET.get('q', '')
    customers = Customer.objects.all().order_by('-created_at')
    
    if query:
        from django.db.models import Q
        customers = customers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(student_id__icontains=query)
        )
        
    return render(request, 'customers/customer_list.html', {'customers': customers, 'query': query})

@login_required
def delete_user(request, user_id):
    if not request.user.is_staff:
        return redirect('products:product_list')
    
    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if target_user.is_superuser:
            # Prevent deleting superusers
            return redirect('customers:customer_list')
        target_user.delete()
        return redirect('customers:customer_list')
        
    return render(request, 'customers/confirm_delete_user.html', {'target_user': target_user})

@login_required
def customer_search_api(request):
    from django.http import JsonResponse
    if not request.user.is_staff:
        return JsonResponse({'results': []}, status=403)
        
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
        
    from django.db.models import Q
    customers = Customer.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(student_id__icontains=query)
    ).order_by('-created_at')[:5]
    
    results = []
    for c in customers:
        results.append({
            'id': c.id,
            'name': f"{c.user.first_name} {c.user.last_name}",
            'username': c.user.username,
            'student_id': c.student_id,
            'url': f"/customers/profile/?user={c.user.id}"
        })
    return JsonResponse({'results': results})
