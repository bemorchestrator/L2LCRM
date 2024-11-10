# inventory/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch

@login_required
def product_list(request):
    """
    View to display the list of products with pagination and remaining components.
    """
    # Prefetch related components only for Articles to optimize queries
    products = Product.objects.all().select_related('supplier').prefetch_related(
        Prefetch('components', queryset=Product.objects.filter(product_type=Product.COMPONENT))
    )

    # Add component stock information for articles
    for product in products:
        if product.product_type == Product.ARTICLE:
            product.remaining_component_stock = product.get_total_component_stock()
        else:
            product.remaining_component_stock = 'N/A'  # For Components

    paginator = Paginator(products, 15)  # Display 15 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = ProductForm()
    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'form': form
    })


def add_product(request):
    """
    View to handle adding a new product.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare product data to send back
                product_data = {
                    'id': product.id,
                    'item_name': product.item_name,
                    'quantity': product.quantity,
                    'uom': product.uom,
                    'supplier_id': product.supplier.id if product.supplier else '',
                    'supplier_name': product.supplier.supplier_name if product.supplier else '',
                    'currency_code': product.currency_code,
                    'retail_price': str(product.retail_price),
                    'discountable_all': 'Yes' if product.discountable_all else 'No',
                    'discountable_members': 'Yes' if product.discountable_members else 'No',
                    'active': 'Yes' if product.active else 'No',
                    'photo_url': product.photo.url if product.photo else '',
                    'product_type': product.product_type,
                    'product_category': product.product_category,
                    'custom_product_category': product.custom_product_category or '',
                    'linked_article_id': product.linked_article.id if product.linked_article else None,
                }
                return JsonResponse({'status': 'success', 'message': 'Product added successfully!', 'product': product_data})
            else:
                messages.success(request, 'Product has been successfully added!')
                return redirect('product_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'errors': errors})
            else:
                messages.error(request, 'There was an error adding the product. Please try again.')
                return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/add_product.html', {'form': form})


@require_POST
def delete_product(request, product_id):
    """
    View to delete a single product via AJAX or non-AJAX request.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'status': 'success'})
    else:
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, 'Product has been successfully deleted.')
        return redirect('product_list')


@require_POST
def bulk_delete_products(request):
    """
    View to delete multiple products via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_ids = request.POST.getlist('product_ids')
        if product_ids:
            Product.objects.filter(id__in=product_ids).delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No products selected.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def edit_product(request, product_id):
    """
    View to fetch product data for editing via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        data = {
            'id': product.id,
            'item_name': product.item_name,
            'quantity': product.quantity,
            'uom': product.uom,
            'supplier_id': product.supplier.id if product.supplier else '',
            'supplier_name': product.supplier.supplier_name if product.supplier else '',
            'currency_code': product.currency_code,
            'retail_price': str(product.retail_price) if product.retail_price else '',
            'discountable_all': bool(product.discountable_all),
            'discountable_members': bool(product.discountable_members),
            'active': bool(product.active),
            'photo_url': product.photo.url if product.photo else '',
            'product_type': product.product_type,
            'product_category': product.product_category,
            'custom_product_category': product.custom_product_category or '',
            'linked_article_id': product.linked_article.id if product.linked_article else '',
        }
        return JsonResponse({'status': 'success', 'product': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@require_POST
def update_product(request, product_id):
    """
    View to update a product via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            updated_product = Product.objects.select_related('supplier').get(id=product_id)
            data = {
                'id': updated_product.id,
                'item_name': updated_product.item_name,
                'quantity': updated_product.quantity,
                'uom': updated_product.uom,
                'supplier_id': updated_product.supplier.id if updated_product.supplier else '',
                'supplier_name': updated_product.supplier.supplier_name if updated_product.supplier else '',
                'currency_code': updated_product.currency_code,
                'retail_price': str(updated_product.retail_price),
                'discountable_all': 'Yes' if updated_product.discountable_all else 'No',
                'discountable_members': 'Yes' if updated_product.discountable_members else 'No',
                'active': 'Yes' if updated_product.active else 'No',
                'photo_url': updated_product.photo.url if updated_product.photo else '',
                'product_type': updated_product.product_type,
                'product_category': updated_product.product_category,
                'custom_product_category': updated_product.custom_product_category or '',
                'linked_article_id': updated_product.linked_article.id if updated_product.linked_article else None,
                'remaining_component_stock': updated_product.get_total_component_stock() if updated_product.product_type == Product.ARTICLE else 'N/A',
            }
            return JsonResponse({'status': 'success', 'message': 'Product updated successfully!', 'product': data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the form.', 'errors': errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def search_products(request):
    """
    View to handle real-time search with autocomplete functionality.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        if query:
            products = Product.objects.filter(item_name__icontains=query).select_related('supplier').prefetch_related(
                Prefetch('components', queryset=Product.objects.filter(product_type=Product.COMPONENT))
            )
        else:
            products = Product.objects.all().select_related('supplier').prefetch_related(
                Prefetch('components', queryset=Product.objects.filter(product_type=Product.COMPONENT))
            )
        
        # Add remaining_component_stock to each product
        for product in products:
            if product.product_type == Product.ARTICLE:
                product.remaining_component_stock = product.get_total_component_stock()
            else:
                product.remaining_component_stock = 'N/A'
        
        # Serialize products
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'item_name': product.item_name,
                'quantity': product.quantity,
                'uom': product.uom,
                'supplier_name': product.supplier.supplier_name if product.supplier else '',
                'currency_code': product.currency_code,
                'retail_price': str(product.retail_price),
                'discountable_all': 'Yes' if product.discountable_all else 'No',
                'discountable_members': 'Yes' if product.discountable_members else 'No',
                'active': 'Yes' if product.active else 'No',
                'photo_url': product.photo.url if product.photo else '',
                'product_type': product.product_type,
                'product_category': product.product_category,
                'custom_product_category': product.custom_product_category or '',
                'linked_article_id': product.linked_article.id if product.linked_article else None,
                'remaining_component_stock': product.remaining_component_stock,
            })
        return JsonResponse({'status': 'success', 'products': products_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@require_GET
def get_uom_options(request):
    """
    AJAX view to return UOM options based on selected product_category.
    """
    product_category = request.GET.get('product_category')
    uom_mappings = {
        'Capsule': ['Pieces', 'Bottles'],
        'Tablet': ['Pieces', 'Bottles'],
        'Powder': ['Grams', 'Kilograms'],
        'Liquid': ['ml', 'Liters'],
    }
    uom_options = uom_mappings.get(product_category, [])
    return JsonResponse({'uom_options': uom_options})


def article_list(request):
    articles = Product.objects.filter(product_type=Product.ARTICLE).select_related('supplier')
    paginator = Paginator(articles, 15)  # Adjust as needed
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory/article_list.html', {'page_obj': page_obj})