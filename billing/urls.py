from django.urls import path
from . import views
app_name = 'billing'
urlpatterns = [
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/<uuid:pk>/', views.quotation_detail, name='quotation_detail'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<uuid:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('pricing/', views.pricing_list, name='pricing_list'),
]
