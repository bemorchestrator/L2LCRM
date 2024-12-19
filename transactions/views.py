from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Transaction, TransactionItem
from .forms import TransactionForm
from patients.models import Patients
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from inventory.models import Product
from django.template.loader import render_to_string

@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('patient').all().order_by('-date')
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = TransactionForm()
    products = Product.objects.all()
    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj,
        'form': form,
        'products': products
    })

@login_required
@require_POST
def add_transaction(request):
    form = TransactionForm(request.POST)
    if form.is_valid():
        try:
            with db_transaction.atomic():
                transaction = form.save()
                item_types = request.POST.getlist('item_type[]', [])
                product_ids = request.POST.getlist('product[]', [])
                quantities = request.POST.getlist('quantity[]', [])
                prices = request.POST.getlist('price[]', [])

                for i in range(len(item_types)):
                    item_type = item_types[i].strip()
                    prod_id = product_ids[i].strip() if i < len(product_ids) else ''
                    quantity = quantities[i].strip() if i < len(quantities) else '0'
                    price = prices[i].strip() if i < len(prices) else '0.00'

                    if not item_type:
                        continue

                    q = int(quantity) if quantity.isdigit() else 0
                    p = float(price) if price.replace('.', '', 1).isdigit() else 0.00
                    product = Product.objects.filter(id=prod_id).first() if prod_id else None

                    # If price not set and product has retail_price
                    if product and p == 0:
                        p = product.retail_price if product.retail_price else 0

                    if q > 0:
                        item = TransactionItem(
                            transaction=transaction,
                            item_type=item_type,
                            product=product,
                            quantity=q,
                            price=p
                        )
                        item.save()

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
                'form': form.errors.get_json_data()
            },
            'message': 'Validation failed.'
        })

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
        if form.is_valid():
            try:
                with db_transaction.atomic():
                    transaction_updated = form.save()

                    # Delete old items first
                    transaction_updated.items.all().delete()

                    # Re-add items from POST
                    item_types = request.POST.getlist('item_type[]', [])
                    product_ids = request.POST.getlist('product[]', [])
                    quantities = request.POST.getlist('quantity[]', [])
                    prices = request.POST.getlist('price[]', [])

                    for i in range(len(item_types)):
                        item_type = item_types[i].strip()
                        prod_id = product_ids[i].strip() if i < len(product_ids) else ''
                        quantity = quantities[i].strip() if i < len(quantities) else '0'
                        price = prices[i].strip() if i < len(prices) else '0.00'

                        if not item_type:
                            continue

                        q = int(quantity) if quantity.isdigit() else 0
                        p = float(price) if price.replace('.', '', 1).isdigit() else 0.00
                        product = Product.objects.filter(id=prod_id).first() if prod_id else None

                        if product and p == 0:
                            p = product.retail_price if product.retail_price else 0

                        if q > 0:
                            item = TransactionItem(
                                transaction=transaction_updated,
                                item_type=item_type,
                                product=product,
                                quantity=q,
                                price=p
                            )
                            item.save()

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
                        'form': form.errors.get_json_data()
                    },
                    'message': 'Validation failed.'
                })
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = TransactionForm(instance=transaction_obj)
            items = transaction_obj.items.all()

            # Render a partial HTML snippet of items in non-formset manner
            # We'll generate HTML for items: item_type[], product[], quantity[], price[]
            products = Product.objects.all()
            html_items = render_to_string('transactions/_transaction_items.html', {
                'items': items,
                'products': products
            }, request=request)

            data = {
                'id': transaction_obj.id,
                'transaction_no': transaction_obj.transaction_no,
                'patient': transaction_obj.patient.id,
                'date': transaction_obj.date.strftime('%Y-%m-%d'),
                'issuer': transaction_obj.issuer,
                'tel': transaction_obj.tel,
                'email': transaction_obj.email,
                'address': transaction_obj.address,
                'formset_html': html_items
            }
            return JsonResponse({'status': 'success', 'transaction': data})
        else:
            form = TransactionForm(instance=transaction_obj)
            products = Product.objects.all()
            return render(request, 'transactions/edit_transaction.html', {
                'form': form,
                'transaction': transaction_obj,
                'products': products
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
