from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('booking/delete/<int:pk>/', views.delete_booking, name='delete_booking'),
    
    # Регистрация
    path('accounts/register/', views.register_view, name='register'),
    
    # Маршруты для CRUD Клиентов
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/update/<int:pk>/', views.client_update, name='client_update'),
    path('clients/delete/<int:pk>/', views.client_delete, name='client_delete'),
]
