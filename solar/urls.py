from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quotation/', views.quotation, name='quotation'),
    path('generate_invoice_view/', views.generate_invoice_view, name='generate_invoice_view'),
    path('control_panel/', views.control_panel, name='control_panel'),
    path('api/panels/', views.panel_list),
    path('api/panels/<int:id>/', views.panel_detail),
    path('api/inverters/', views.inverter_list),
    path('api/inverters/<int:id>/', views.inverter_detail),
    path('api/customers/', views.customer_list),
    path('api/set-prices/', views.set_prices),
    path('api/get-prices/', views.get_prices, name='get_prices'),
]
