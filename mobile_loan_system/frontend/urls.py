from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customers/', views.customers_page, name='customers'),
    path('inventory/', views.inventory_page, name='inventory'),
    path('loans/', views.loans_page, name='loans'),
    path('loans/<int:loan_id>/', views.loan_detail_page, name='loan_detail'),
]
