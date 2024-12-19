from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from suppliers.models import Supplier
from .models import Product, Container
from .forms import ProductForm
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
import logging

logger = logging.getLogger(__name__)

def _get_product_data(product):
    linked_components = []
    if product.product_type == Product.ARTICLE:
        components = product.components.all()
        for component in components:
            linked_components.append({
                'id': component.id,
                'item_name': component.item_name,
                'quantity': component.quantity,
                'units_per_article': component.units_per_article,
            })
    return {
        'id': product.id,
        'item_name': product.item_name,
        'quantity': product.quantity,
        'uom': product.uom,
        'supplier_id': product.supplier.id if product.supplier else '',
        'supplier_name': product.supplier.supplier_name if product.supplier else '',
        'currency_code': product.currency_code,
        'retail_price': str(product.retail_price) if product.retail_price else '',
        'discountable_all': product.discountable_all,
        'discountable_members': product.discountable_members,
        'active': product.active,
        'photo_url': product.photo.url if product.photo else '',
        'product_type': product.product_type,
        'content_type': product.content_type,
        'custom_content_type': product.custom_content_type or '',
        'linked_article_id': product.linked_article.id if product.linked_article else '',
        'linked_article_name': product.linked_article.item_name if product.linked_article else '',
        'remaining_component_stock': product.get_total_component_stock() if product.product_type == Product.ARTICLE else 'N/A',
        'sellable_sets': product.calculate_sellable_sets() if product.product_type == Product.ARTICLE else 'N/A',
        'linked_components': linked_components,
        'container_id': product.container.id if product.container else '',
        'container_name': product.container.name if product.container else '',
        'pieces_per_container': product.pieces_per_container,
        'units_per_article': product.units_per_article,
    }

@login_required
def product_list(request):
    products = Product.objects.all().select_related('supplier', 'linked_article', 'container').prefetch_related(
        Prefetch('components', queryset=Product.objects.filter(product_type=Product.COMPONENT))
    ).order_by('-id')

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    product_data = [_get_product_data(product) for product in page_obj]
    container_choices = Container.objects.all()

    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'form': ProductForm(),
        'suppliers': list(Supplier.objects.filter(active=True).values('id', 'supplier_name')),
        'articles': list(Product.objects.filter(product_type=Product.ARTICLE).values('id', 'item_name')),
        'containers': container_choices,
        'products': product_data,
    })

@login_required
@require_POST
def add_product(request):
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save()
        messages.success(request, 'Product added successfully!')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            product_data = _get_product_data(product)
            return JsonResponse({'status': 'success', 'product': product_data})
        else:
            return redirect('product_list')
    else:
        logger.error('Form is invalid: %s', form.errors)
        messages.error(request, 'There was an error adding the product.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        else:
            return redirect('product_list')

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'product': _get_product_data(product)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        product = form.save()
        related_articles = []
        if product.product_type == Product.COMPONENT and product.linked_article:
            sellable_sets = product.linked_article.calculate_sellable_sets()
            related_articles.append({
                'id': product.linked_article.id,
                'sellable_sets': sellable_sets
            })

        return JsonResponse({
            'status': 'success',
            'message': 'Product updated successfully!',
            'related_articles': related_articles
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Form validation failed. Please correct the errors.',
        'errors': form.errors
    }, status=400)

@login_required
@require_POST
def delete_product(request, product_id):
    get_object_or_404(Product, id=product_id).delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def bulk_delete_products(request):
    product_ids = request.POST.getlist('product_ids', [])
    if product_ids:
        Product.objects.filter(id__in=product_ids).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'No products selected.'})

@login_required
@require_GET
def get_uom_options(request):
    container_id = request.GET.get('container_id')
    content_type = request.GET.get('content_type')

    if container_id and content_type:
        try:
            container = get_object_or_404(Container, id=container_id)
            uom_options = container.allowed_uoms.get(content_type, [])
            return JsonResponse({'status': 'success', 'uom_options': uom_options})
        except Container.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Container does not exist.'})
        except Exception as e:
            logger.error(f"Error fetching UOM options: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while fetching UOM options.'})

    return JsonResponse({'status': 'error', 'message': 'Container ID or content type not provided.'})

@login_required
@require_GET
def get_sellable_sets(request):
    article_id = request.GET.get('article_id')
    if article_id:
        article = get_object_or_404(Product, id=article_id, product_type=Product.ARTICLE)
        return JsonResponse({'status': 'success', 'sellable_sets': article.calculate_sellable_sets()})
    return JsonResponse({'status': 'error', 'message': 'Article ID not provided'})

@login_required
@require_GET
def get_article_data(request):
    article_id = request.GET.get('article_id')
    if article_id:
        article = get_object_or_404(Product, id=article_id, product_type=Product.ARTICLE)
        data = {
            'quantity': article.quantity,
            'pieces_per_container': article.pieces_per_container
        }
        return JsonResponse({'status': 'success', 'article_data': data})
    return JsonResponse({'status': 'error', 'message': 'Article ID not provided.'})

@login_required
def article_list(request):
    articles = Product.objects.filter(product_type=Product.ARTICLE).select_related('supplier', 'container').order_by('-id')
    paginator = Paginator(articles, 15)
    return render(request, 'inventory/article_list.html', {'page_obj': paginator.get_page(request.GET.get('page'))})

@login_required
def component_list(request):
    components = Product.objects.filter(product_type=Product.COMPONENT).select_related('supplier', 'container').order_by('-id')
    paginator = Paginator(components, 15)
    return render(request, 'inventory/component_list.html', {'page_obj': paginator.get_page(request.GET.get('page'))})

@login_required
def search_products(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        products = Product.objects.filter(item_name__icontains=query).select_related('supplier', 'container').order_by('-id') if query else Product.objects.all().select_related('supplier', 'container').order_by('-id')
        return JsonResponse({'status': 'success', 'products': [_get_product_data(product) for product in products]})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
