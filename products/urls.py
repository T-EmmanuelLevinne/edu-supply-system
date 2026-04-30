from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/update/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('delivery/', views.delivery_info, name='delivery_info'),
    path('api/search/', views.product_search_api, name='product_search_api'),
]
