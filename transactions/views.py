from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Transaction, TransactionItem
from .forms import TransactionForm, TransactionItemFormSet
from patients.models import Patients
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction as db_transaction
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from inventory.models import Product

@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('patient').all().order_by('-date')
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = TransactionForm()
    # For the "Add Transaction" modal on this page, we create a blank formset with no items
    formset = TransactionItemFormSet(queryset=TransactionItem.objects.none())
    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj,
        'form': form,
        'formset': formset
    })

@login_required
@require_POST
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        formset = TransactionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with db_transaction.atomic():
                    transaction = form.save()
                    items = formset.save(commit=False)
                    for item in items:
                        item.transaction = transaction
                        if item.product and item.price == 0:
                            if item.product.retail_price:
                                item.price = item.product.retail_price
                            else:
                                item.price = 0
                        item.save()
                    formset.save_m2m()
                messages.success(request, "Transaction and items added successfully.")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction and items added successfully.',
                    'transaction': {
                        'id': transaction.id,
                        'transaction_no': transaction.transaction_no,
                        'patient': str(transaction.patient),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'issuer': transaction.issuer,
                        'tel': transaction.tel,
                        'email': transaction.email,
                        'address': transaction.address,
                    }
                })
            except ValidationError as e:
                return JsonResponse({
                    'status': 'error',
                    'errors': {'__all__': [{'message': str(e)}]},
                    'message': str(e)
                })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': {
                    'form': form.errors.get_json_data(),
                    'formset': formset.errors
                },
                'message': 'Validation failed.'
            })
    else:
        form = TransactionForm()
        formset = TransactionItemFormSet()
    return render(request, 'transactions/add_transaction.html', {'form': form, 'formset': formset})

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    items = transaction.items.all()
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction, 'items': items})

@login_required
def edit_transaction(request, transaction_id):
    transaction_obj = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction_obj)
        formset = TransactionItemFormSet(request.POST, instance=transaction_obj)
        if form.is_valid() and formset.is_valid():
            try:
                with db_transaction.atomic():
                    transaction_updated = form.save()
                    items = formset.save(commit=False)
                    for item in items:
                        item.transaction = transaction_updated
                        if item.product and item.price == 0:
                            if item.product.retail_price:
                                item.price = item.product.retail_price
                            else:
                                item.price = 0
                        item.save()
                    for deleted_item in formset.deleted_objects:
                        deleted_item.delete()
                    formset.save_m2m()
                messages.success(request, "Transaction and items updated successfully.")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Transaction and items updated successfully.',
                        'transaction': {
                            'id': transaction_obj.id,
                            'transaction_no': transaction_obj.transaction_no,
                            'patient': str(transaction_obj.patient),
                            'date': transaction_obj.date.strftime('%Y-%m-%d'),
                            'issuer': transaction_obj.issuer,
                            'tel': transaction_obj.tel,
                            'email': transaction_obj.email,
                            'address': transaction_obj.address,
                        }
                    })
                else:
                    return redirect('transaction_list')
            except ValidationError as e:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'errors': {'__all__': [{'message': str(e)}]},
                        'message': str(e)
                    })
                else:
                    messages.error(request, str(e))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': {
                        'form': form.errors.get_json_data(),
                        'formset': formset.errors
                    },
                    'message': 'Validation failed.'
                })
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = TransactionForm(instance=transaction_obj)
            formset = TransactionItemFormSet(instance=transaction_obj)
            # Render partial HTML that includes the management form
            rendered_formset = render(request, 'transactions/_transaction_formset.html', {
                'formset': formset
            })
            data = {
                'id': transaction_obj.id,
                'transaction_no': transaction_obj.transaction_no,
                'patient': transaction_obj.patient.id,
                'date': transaction_obj.date.strftime('%Y-%m-%d'),
                'issuer': transaction_obj.issuer,
                'tel': transaction_obj.tel,
                'email': transaction_obj.email,
                'address': transaction_obj.address,
                'formset_html': rendered_formset.content.decode('utf-8')
            }
            return JsonResponse({'status': 'success', 'transaction': data})
        else:
            form = TransactionForm(instance=transaction_obj)
            formset = TransactionItemFormSet(instance=transaction_obj)

    return render(request, 'transactions/edit_transaction.html', {
        'form': form,
        'formset': formset,
        'transaction': transaction_obj
    })

@login_required
def invoice_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction,
        'patient': transaction.patient
    }
    return render(request, 'transactions/invoice.html', context)

@login_required
def search_transactions(request):
    query = request.GET.get('q', '').strip()
    if query:
        transactions = Transaction.objects.select_related('patient').filter(
            Q(name__icontains=query) | Q(transaction_no__icontains=query)
        ).order_by('-date')
    else:
        transactions = Transaction.objects.select_related('patient').all().order_by('-date')
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rendered_transactions = render(request, 'transactions/_transaction_rows.html', {'transactions': page_obj})
    return JsonResponse({'status': 'success', 'html': rendered_transactions.content.decode('utf-8')})

@login_required
@require_POST
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Transaction deleted successfully.")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Transaction deleted successfully.'})
    else:
        return redirect('transaction_list')

@login_required
@require_POST
def bulk_delete_transactions(request):
    transaction_ids = request.POST.getlist('transaction_ids[]')
    if transaction_ids:
        transactions = Transaction.objects.filter(id__in=transaction_ids)
        count = transactions.count()
        transactions.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"{count} transaction(s) deleted successfully."})
        else:
            messages.success(request, f"{count} transaction(s) deleted successfully.")
            return redirect('transaction_list')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': "No transactions selected for deletion."})
        else:
            messages.error(request, "No transactions selected for deletion.")
            return redirect('transaction_list')

@login_required
def get_patient_details(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    data = {
        'email': patient.email,
        'address': patient.address,
        'phone': patient.phone,
    }
    return JsonResponse({'status': 'success', 'data': data})

@login_required
def get_transaction_items(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    items = transaction.items.select_related('product').all()
    items_data = []
    for item in items:
        items_data.append({
            'item_type': item.item_type,
            'product': item.product.item_name if item.product else 'N/A',
            'quantity': item.quantity,
            'price': str(item.price),
        })
    return JsonResponse({'status': 'success', 'items': items_data})

@login_required
def get_product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'status': 'success',
        'data': {
            'retail_price': str(product.retail_price if product.retail_price else '0.00')
        }
    })
