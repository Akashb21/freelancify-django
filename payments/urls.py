from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:contract_id>/', views.checkout_view, name='checkout'),
    path('process/<int:contract_id>/', views.process_checkout, name='process_checkout'),
    path('invoice/<int:transaction_id>/download/', views.download_invoice, name='download_invoice'),
    path('history/', views.transaction_history, name='history'),
]
