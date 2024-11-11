# transactions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Transaction
from .forms import TransactionForm
from patients.models import Patients
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def transaction_list(request):
    """
    View to display the list of transactions with pagination.
    """
    transactions = Transaction.objects.select_related('patient').all().order_by('-date')
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Pass the form to the template
    form = TransactionForm()
    
    return render(request, 'transactions/transaction_list.html', {'page_obj': page_obj, 'form': form})

@login_required
@require_POST
def add_transaction(request):
    """
    View to handle adding a new transaction via AJAX.
    """
    form = TransactionForm(request.POST)
    if form.is_valid():
        transaction = form.save()
        # Prepare the data to send back to the client
        transaction_data = {
            'id': transaction.id,
            'transaction_no': transaction.transaction_no,
            'patient': str(transaction.patient),
            'date': transaction.date.strftime('%Y-%m-%d'),
            'issuer': transaction.issuer,
            'tel': transaction.tel,
            'email': transaction.email,
            'address': transaction.address,
        }
        return JsonResponse({'status': 'success', 'transaction': transaction_data, 'message': 'Transaction has been successfully added.'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors.as_json(), 'message': 'There was an error adding the transaction.'})

@login_required
def transaction_detail(request, transaction_id):
    """
    View to display the details of a specific transaction.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})

@login_required
def invoice_view(request, transaction_id):
    """
    View to generate and display an invoice for a specific transaction.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction,
        'patient': transaction.patient
    }
    return render(request, 'transactions/invoice.html', context)

@login_required
def search_transactions(request):
    """
    View to search for transactions based on patient name or transaction number via AJAX.
    """
    query = request.GET.get('q', '').strip()
    transactions = (
        Transaction.objects.select_related('patient').filter(
            Q(name__icontains=query) | Q(transaction_no__icontains=query)
        ).order_by('-date')
        if query else Transaction.objects.select_related('patient').all().order_by('-date')
    )

    # Pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the partial template for transactions
    rendered_transactions = render(request, 'transactions/_transaction_rows.html', {'transactions': page_obj})

    return JsonResponse({'status': 'success', 'html': rendered_transactions.content.decode('utf-8')})

@login_required
@require_POST
def delete_transaction(request, transaction_id):
    """
    View to delete a specific transaction via AJAX.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return JsonResponse({'status': 'success', 'message': 'Transaction has been deleted.'})

@login_required
@require_POST
def bulk_delete_transactions(request):
    """
    View to bulk delete transactions via AJAX.
    """
    transaction_ids = request.POST.getlist('transaction_ids[]')
    if transaction_ids:
        transactions = Transaction.objects.filter(id__in=transaction_ids)
        count = transactions.count()
        transactions.delete()
        return JsonResponse({'status': 'success', 'message': f'{count} transaction(s) have been deleted.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'No transactions selected for deletion.'})

@login_required
def edit_transaction(request, transaction_id):
    """
    View to handle editing a transaction via AJAX.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            # Update the auto-filled fields
            transaction.name = f"{transaction.patient.first_name} {transaction.patient.last_name}"
            transaction.email = transaction.patient.email
            transaction.address = transaction.patient.address
            transaction.tel = transaction.patient.phone  # Ensure tel is updated
            transaction.save()
            transaction_data = {
                'id': transaction.id,
                'transaction_no': transaction.transaction_no,  # Ensure transaction_no is included
                'patient': str(transaction.patient),
                'date': transaction.date.strftime('%Y-%m-%d'),
                'issuer': transaction.issuer,
                'tel': transaction.tel,
                'email': transaction.email,
                'address': transaction.address,
            }
            return JsonResponse({'status': 'success', 'transaction': transaction_data, 'message': 'Transaction has been successfully updated.'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors.as_json(), 'message': 'There was an error updating the transaction.'})
    else:
        # If GET request, return transaction data
        transaction_data = {
            'id': transaction.id,
            'patient': transaction.patient.id,
            'issuer': transaction.issuer,
            'transaction_no': transaction.transaction_no,  # Include transaction_no for edit
            # 'tel' is auto-populated; no need to include here
        }
        return JsonResponse({'status': 'success', 'transaction': transaction_data})

@login_required
def get_patient_details(request, patient_id):
    """
    View to fetch patient details based on patient ID via AJAX.
    """
    patient = get_object_or_404(Patients, id=patient_id)
    data = {
        'email': patient.email,
        'address': patient.address,
        'phone': patient.phone,  # Include phone number
    }
    return JsonResponse({'status': 'success', 'data': data})
