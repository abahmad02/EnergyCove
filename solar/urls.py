from django.urls import path
from . import views
from .views import BillValidateAPIView, GetBillDataAPIView, GenerateInvoiceForSystem

urlpatterns = [
    path('', views.index, name='index'),
    path('quotation/', views.quotation, name='quotation'),
    path('api/bill/validate/', BillValidateAPIView.as_view(), name='bill_validate'),
    path('api/bill/<str:reference_number>/', GetBillDataAPIView.as_view(), name='get_bill_data'),
    path('generate_invoice_view/', views.generate_invoice_view, name='generate_invoice_view'),
    path('api/quote/<int:system_size>/', GenerateInvoiceForSystem.as_view(), name='get_quote_data'),
    path('control_panel/', views.control_panel, name='control_panel'),
    path('api/panels/', views.panel_list),
    path('api/panels/<int:id>/', views.panel_detail),
    path('api/inverters/', views.inverter_list),
    path('api/inverters/<int:id>/', views.inverter_detail),
    path('api/customers/', views.customer_list),
    path('api/set-prices/', views.set_prices),
    path('api/get-prices/', views.get_prices, name='get_prices'),
    path('api/set-default-panel/<int:panel_id>/', views.set_default_panel, name='set_default_panel'),
]