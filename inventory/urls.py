# inventory/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('products/bulk_delete/', views.bulk_delete_products, name='bulk_delete_products'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/update/<int:product_id>/', views.update_product, name='update_product'),
    path('search_products/', views.search_products, name='search_products'),
    path('get-uom-options/', views.get_uom_options, name='get_uom_options'),
    path('articles/', views.article_list, name='article_list'),
    path('components/', views.component_list, name='component_list'),
    
]
