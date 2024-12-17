# patients/urls.py

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
    path('patients/<str:nric>/diagnosis/', views.diagnosis_detail, name='diagnosis_detail'),
    
    # Diagnosis-related URLs
    path('patients/<str:nric>/diagnosis/add/', views.add_diagnosis, name='add_diagnosis'),
    path('patients/<str:nric>/diagnosis/edit/<int:diagnosis_id>/', views.edit_diagnosis, name='edit_diagnosis'),
    path('patients/<str:nric>/diagnosis/delete/<int:diagnosis_id>/', views.delete_diagnosis, name='delete_diagnosis'),
    path('patients/<str:nric>/diagnosis/bulk-delete/', views.bulk_delete_diagnoses, name='bulk_delete_diagnoses'),
    path('patients/<str:nric>/diagnosis/search/', views.search_diagnoses, name='search_diagnoses'),
    path('patients/<str:nric>/diagnosis/update/<int:diagnosis_id>/', views.update_diagnosis, name='update_diagnosis'),
]
