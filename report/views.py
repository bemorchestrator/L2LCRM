# report/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Sum, Avg
from .models import ItemSalesReport
from .forms import ItemSalesReportForm

def item_sales_report_list(request):
    """
    View to list all item sales reports with pagination.
    Renders the item_sales_report.html template.
    """
    reports = ItemSalesReport.objects.all().order_by('-date_from')
    paginator = Paginator(reports, 10)  # Show 10 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Replace request.is_ajax() with header inspection
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If AJAX request, return the rendered table rows
        return render(request, 'report/_report_rows.html', {'reports': page_obj.object_list})

    return render(request, 'report/item_sales_report.html', {
        'page_obj': page_obj
    })

@require_POST
def add_report(request):
    """
    View to add a new item sales report via AJAX.
    """
    form = ItemSalesReportForm(request.POST)
    if form.is_valid():
        report = form.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Report added successfully!',
            'report': {
                'id': report.id,
                'item_name': report.item_name,
                'total_sales': str(report.total_sales),
                'total_cost': str(report.total_cost),
                'total_discount': str(report.total_discount),
                'total_tax': str(report.total_tax),
                'average_list_price': str(report.average_list_price),
                'average_cost_price': str(report.average_cost_price),
                'quantity_sold': report.quantity_sold,
                'date_from': report.date_from.strftime('%Y-%m-%d'),
                'date_to': report.date_to.strftime('%Y-%m-%d'),
            }
        })
    else:
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)

@require_POST
def delete_report(request, report_id):
    """
    View to delete a single report via AJAX.
    """
    report = get_object_or_404(ItemSalesReport, id=report_id)
    report.delete()
    return JsonResponse({
        'status': 'success',
        'message': 'Report deleted successfully!'
    })

@require_POST
def bulk_delete_reports(request):
    """
    View to bulk delete reports via AJAX.
    Expects 'report_ids[]' in POST data.
    """
    report_ids = request.POST.getlist('report_ids[]')
    reports = ItemSalesReport.objects.filter(id__in=report_ids)
    deleted_count = reports.count()
    reports.delete()
    return JsonResponse({
        'status': 'success',
        'message': f'{deleted_count} report(s) deleted successfully!'
    })

@require_GET
def edit_report(request, report_id):
    """
    View to fetch report details for editing via AJAX.
    """
    report = get_object_or_404(ItemSalesReport, id=report_id)
    report_data = {
        'id': report.id,
        'item_name': report.item_name,
        'total_sales': str(report.total_sales),
        'total_cost': str(report.total_cost),
        'total_discount': str(report.total_discount),
        'total_tax': str(report.total_tax),
        'average_list_price': str(report.average_list_price),
        'average_cost_price': str(report.average_cost_price),
        'quantity_sold': report.quantity_sold,
        'date_from': report.date_from.strftime('%Y-%m-%d'),
        'date_to': report.date_to.strftime('%Y-%m-%d'),
    }
    return JsonResponse({
        'status': 'success',
        'report': report_data
    })

@require_GET
def search_reports(request):
    """
    View to search reports based on query via AJAX.
    """
    query = request.GET.get('q', '')
    reports = ItemSalesReport.objects.filter(
        Q(item_name__icontains=query) |
        Q(total_sales__icontains=query) |
        Q(total_cost__icontains=query) |
        Q(total_discount__icontains=query) |
        Q(total_tax__icontains=query) |
        Q(average_list_price__icontains=query) |
        Q(average_cost_price__icontains=query) |
        Q(quantity_sold__icontains=query) |
        Q(date_from__icontains=query) |
        Q(date_to__icontains=query)
    ).order_by('-date_from')
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'report/_report_rows.html', {'reports': page_obj.object_list})

def generate_report(request):
    """
    View to generate aggregated reports dynamically based on queries.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        reports = ItemSalesReport.objects.filter(date_from__gte=start_date, date_to__lte=end_date)
    else:
        reports = ItemSalesReport.objects.all()

    aggregated_data = reports.aggregate(
        total_sales=Sum('total_sales'),
        total_cost=Sum('total_cost'),
        total_discount=Sum('total_discount'),
        total_tax=Sum('total_tax'),
        average_list_price=Avg('average_list_price'),
        average_cost_price=Avg('average_cost_price'),
        quantity_sold=Sum('quantity_sold')
    )

    return JsonResponse({
        'status': 'success',
        'data': aggregated_data
    })
