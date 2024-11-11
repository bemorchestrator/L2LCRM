from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('patients/bulk-delete/', views.bulk_delete_patients, name='bulk_delete_patients'),
    path('patients/edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('patients/update/<int:patient_id>/', views.update_patient, name='update_patient'),
    path('patients/search/', views.search_patients, name='search_patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
]
