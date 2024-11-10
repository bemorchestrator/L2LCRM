from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import Supplier
from .forms import SupplierForm
from django.core.paginator import Paginator

@csrf_protect
def supplier_list(request):
    """
    View to display the list of suppliers with pagination.
    """
    suppliers = Supplier.objects.all()  # Fetch all suppliers
    paginator = Paginator(suppliers, 15)  # Display 15 suppliers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = SupplierForm()
    return render(request, 'suppliers/supplier_list.html', {
        'page_obj': page_obj,
        'form': form
    })

def add_supplier(request):
    """
    View to handle form submission for adding a new supplier.
    If the request is AJAX, it returns a JSON response; otherwise, it redirects.
    """
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare supplier data to send back
                supplier_data = {
                    'id': supplier.id,
                    'supplier_no': supplier.supplier_no,
                    'supplier_name': supplier.supplier_name,
                    'contact': supplier.contact,
                    'country': supplier.country,
                    'address': supplier.address,
                    'phone': supplier.phone,
                    'fax': supplier.fax,
                    'email': supplier.email,
                    'staff_in_charge': supplier.staff_in_charge,
                    'remarks': supplier.remarks,
                    'active': 'Yes' if supplier.active else 'No',
                    'updated': supplier.updated.strftime('%Y-%m-%d %H:%M:%S'),
                    'created': supplier.created.strftime('%Y-%m-%d %H:%M:%S'),
                }
                return JsonResponse({'status': 'success', 'message': 'Supplier added successfully!', 'supplier': supplier_data})
            else:
                messages.success(request, 'Supplier has been successfully added!')
                return redirect('supplier_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'errors': errors})
            else:
                messages.error(request, 'There was an error adding the supplier. Please try again.')
                return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form})

@require_POST
def delete_supplier(request, supplier_id):
    """
    View to delete a single supplier via AJAX or non-AJAX request.
    """
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Supplier deleted successfully.'})
    else:
        messages.success(request, 'Supplier has been successfully deleted.')
        return redirect('supplier_list')

@require_POST
def bulk_delete_suppliers(request):
    """
    View to delete multiple suppliers via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        supplier_ids = request.POST.getlist('supplier_ids')
        if supplier_ids:
            Supplier.objects.filter(id__in=supplier_ids).delete()
            return JsonResponse({'status': 'success', 'message': 'Selected suppliers have been deleted.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No suppliers selected.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def edit_supplier(request, supplier_id):
    """
    View to fetch supplier data for editing via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        supplier = get_object_or_404(Supplier, id=supplier_id)
        data = {
            'id': supplier.id,
            'supplier_no': supplier.supplier_no,
            'supplier_name': supplier.supplier_name,
            'contact': supplier.contact,
            'country': supplier.country,
            'address': supplier.address,
            'phone': supplier.phone,
            'fax': supplier.fax,
            'email': supplier.email,
            'staff_in_charge': supplier.staff_in_charge,
            'remarks': supplier.remarks,
            'active': supplier.active,
            'updated': supplier.updated.strftime('%Y-%m-%d %H:%M:%S'),
            'created': supplier.created.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse({'status': 'success', 'supplier': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@require_POST
def update_supplier(request, supplier_id):
    """
    View to update a supplier via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        supplier = get_object_or_404(Supplier, id=supplier_id)
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            updated_supplier = Supplier.objects.get(id=supplier_id)
            supplier_data = {
                'id': updated_supplier.id,
                'supplier_no': updated_supplier.supplier_no,
                'supplier_name': updated_supplier.supplier_name,
                'contact': updated_supplier.contact,
                'country': updated_supplier.country,
                'address': updated_supplier.address,
                'phone': updated_supplier.phone,
                'fax': updated_supplier.fax,
                'email': updated_supplier.email,
                'staff_in_charge': updated_supplier.staff_in_charge,
                'remarks': updated_supplier.remarks,
                'active': 'Yes' if updated_supplier.active else 'No',
                'updated': updated_supplier.updated.strftime('%Y-%m-%d %H:%M:%S'),
                'created': updated_supplier.created.strftime('%Y-%m-%d %H:%M:%S'),
            }
            return JsonResponse({'status': 'success', 'message': 'Supplier updated successfully!', 'supplier': supplier_data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the form.', 'errors': errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def search_suppliers(request):
    """
    View to handle real-time search with autocomplete functionality.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        if query:
            suppliers = Supplier.objects.filter(supplier_name__icontains=query)
        else:
            suppliers = Supplier.objects.all()
        
        # Serialize suppliers
        suppliers_data = []
        for supplier in suppliers:
            suppliers_data.append({
                'id': supplier.id,
                'supplier_no': supplier.supplier_no,
                'supplier_name': supplier.supplier_name,
                'contact': supplier.contact,
                'country': supplier.country,
                'address': supplier.address,
                'phone': supplier.phone,
                'fax': supplier.fax,
                'email': supplier.email,
                'staff_in_charge': supplier.staff_in_charge,
                'remarks': supplier.remarks,
                'active': 'Yes' if supplier.active else 'No',
                'updated': supplier.updated.strftime('%Y-%m-%d %H:%M:%S'),
                'created': supplier.created.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return JsonResponse({'status': 'success', 'suppliers': suppliers_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})