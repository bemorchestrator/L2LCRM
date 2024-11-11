# patients/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Patients
from .forms import PatientForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

@csrf_protect
@login_required
def patient_list(request):
    """
    View to display the list of patients with pagination.
    """
    patients = Patients.objects.all()  # Fetch all patients
    paginator = Paginator(patients, 10)  # Display 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = PatientForm()
    return render(request, 'patients/patient_list.html', {
        'page_obj': page_obj,
        'form': form
    })

def add_patient(request):
    """
    View to handle adding a new patient.
    """
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            patient = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare patient data to send back, including age
                patient_data = {
                    'id': patient.id,
                    'patient_no': patient.patient_no,
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
                    'age': patient.age,  # Include age
                    'nric': patient.nric,
                    'country': patient.country,
                    'address': patient.address,
                    'phone': patient.phone,
                    'fax': patient.fax,
                    'email': patient.email,
                    'consented': 'Yes' if patient.consented else 'No',
                    'remarks': patient.remarks,
                    'active': 'Yes' if patient.active else 'No',
                    'profile_photo_url': patient.profile_photo.url if patient.profile_photo else ''
                }
                return JsonResponse({'status': 'success', 'message': 'Patient added successfully!', 'patient': patient_data})
            else:
                messages.success(request, 'Patient has been successfully added!')
                return redirect('patient_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'errors': errors})
            else:
                messages.error(request, 'There was an error adding the patient. Please try again.')
                return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patients/add_patient.html', {'form': form})

@require_POST
def delete_patient(request, patient_id):
    """
    View to delete a single patient via AJAX or non-AJAX request.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        patient = get_object_or_404(Patients, id=patient_id)
        # Optionally delete the profile photo file from storage
        if patient.profile_photo:
            patient.profile_photo.delete()
        patient.delete()
        return JsonResponse({'status': 'success'})
    else:
        patient = get_object_or_404(Patients, id=patient_id)
        # Optionally delete the profile photo file from storage
        if patient.profile_photo:
            patient.profile_photo.delete()
        patient.delete()
        messages.success(request, 'Patient has been successfully deleted.')
        return redirect('patient_list')

@require_POST
def bulk_delete_patients(request):
    """
    View to delete multiple patients via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        patient_ids = request.POST.getlist('patient_ids')
        if patient_ids:
            patients = Patients.objects.filter(id__in=patient_ids)
            for patient in patients:
                if patient.profile_photo:
                    patient.profile_photo.delete()
            patients.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No patients selected.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def edit_patient(request, patient_id):
    """
    View to fetch patient data for editing via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        patient = get_object_or_404(Patients, id=patient_id)
        data = {
            'id': patient.id,
            'patient_no': patient.patient_no,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
            'age': patient.age,  # Include age
            'nric': patient.nric,
            'country': patient.country,
            'address': patient.address,
            'phone': patient.phone,
            'fax': patient.fax,
            'email': patient.email,
            'consented': patient.consented,
            'remarks': patient.remarks,
            'active': patient.active,
            'profile_photo_url': patient.profile_photo.url if patient.profile_photo else ''
        }
        return JsonResponse({'status': 'success', 'patient': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@require_POST
def update_patient(request, patient_id):
    """
    View to update a patient via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        patient = get_object_or_404(Patients, id=patient_id)
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            patient = form.save()
            updated_patient = Patients.objects.get(id=patient_id)
            data = {
                'id': updated_patient.id,
                'patient_no': updated_patient.patient_no,
                'first_name': updated_patient.first_name,
                'last_name': updated_patient.last_name,
                'birth_date': updated_patient.birth_date.strftime('%m/%d/%Y') if updated_patient.birth_date else '',
                'age': updated_patient.age,  # Include age
                'nric': updated_patient.nric,
                'country': updated_patient.country,
                'address': updated_patient.address,
                'phone': updated_patient.phone,
                'fax': updated_patient.fax,
                'email': updated_patient.email,
                'consented': 'Yes' if updated_patient.consented else 'No',
                'remarks': updated_patient.remarks,
                'active': 'Yes' if updated_patient.active else 'No',
                'profile_photo_url': updated_patient.profile_photo.url if updated_patient.profile_photo else ''
            }
            return JsonResponse({'status': 'success', 'message': 'Patient updated successfully!', 'patient': data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the form.', 'errors': errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def search_patients(request):
    """
    View to handle real-time search with autocomplete functionality.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        if query:
            patients = Patients.objects.filter(
                first_name__icontains=query
            ) | Patients.objects.filter(
                last_name__icontains=query
            ) | Patients.objects.filter(
                patient_no__icontains=query
            ) | Patients.objects.filter(
                nric__icontains=query
            )
        else:
            patients = Patients.objects.all()
        
        # Serialize patients
        patients_data = []
        for patient in patients:
            patients_data.append({
                'id': patient.id,
                'patient_no': patient.patient_no,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
                'age': patient.age,  # Include age
                'nric': patient.nric,
                'country': patient.country,
                'address': patient.address,
                'phone': patient.phone,
                'fax': patient.fax,
                'email': patient.email,
                'consented': 'Yes' if patient.consented else 'No',
                'remarks': patient.remarks,
                'active': 'Yes' if patient.active else 'No',
                'profile_photo_url': patient.profile_photo.url if patient.profile_photo else ''
            })
        return JsonResponse({'status': 'success', 'patients': patients_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})
