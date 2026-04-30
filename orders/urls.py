from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('history/', views.order_history, name='order_history'),
    path('manage/', views.manage_orders, name='manage_orders'),
    path('<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('<int:pk>/delete/', views.delete_order, name='delete_order'),
    path('<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('<int:pk>/receipt/', views.view_receipt, name='view_receipt'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout-options/', views.cart_checkout_page, name='cart_checkout_page'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    
    # Delivery Staff URLs
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/accept/<int:order_id>/', views.delivery_accept, name='delivery_accept'),
    path('delivery/cancel/<int:order_id>/', views.delivery_cancel, name='delivery_cancel'),
    path('delivery/scan/<int:order_id>/', views.delivery_scan, name='delivery_scan'),
    path('delivery/complete/<int:order_id>/', views.delivery_complete, name='delivery_complete'),
    path('api/search/', views.order_search_api, name='order_search_api'),
]
