from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('delete/', views.delete_profile, name='delete_profile'),
    path('list/', views.customer_list, name='customer_list'),
    path('<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('api/search/', views.customer_search_api, name='customer_search_api'),
]
