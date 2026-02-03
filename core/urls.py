from django.urls import path
from . import views

urlpatterns = [
    path('sales-made/', views.sales_made_list, name='sales_made_list'),
    path('add-payment/<int:client_id>/', views.confirm_add_payment, name='confirm_add_payment'),
]
