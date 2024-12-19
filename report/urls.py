# report/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_sales_report_list, name='item_sales_report_list'),
    path('add/', views.add_report, name='add_report'),
    path('edit/<int:report_id>/', views.edit_report, name='edit_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('bulk_delete/', views.bulk_delete_reports, name='bulk_delete_reports'),
    path('search/', views.search_reports, name='search_reports'),
    path('generate/', views.generate_report, name='generate_report'),
]
