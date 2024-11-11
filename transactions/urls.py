# transactions/urls.py
from django.urls import path
from .views import (
    transaction_list, add_transaction, transaction_detail,
    invoice_view, search_transactions, delete_transaction,
    bulk_delete_transactions, edit_transaction, get_patient_details
)

urlpatterns = [
    path('', transaction_list, name='transaction_list'),
    path('add/', add_transaction, name='add_transaction'),
    path('<int:transaction_id>/', transaction_detail, name='transaction_detail'),
    path('<int:transaction_id>/invoice/', invoice_view, name='invoice_view'),
    path('search/', search_transactions, name='search_transactions'),
    path('delete/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
    path('bulk-delete/', bulk_delete_transactions, name='bulk_delete_transactions'),
    path('edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('patient/<int:patient_id>/details/', get_patient_details, name='get_patient_details'),  # New endpoint
]
