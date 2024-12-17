# patients/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Patients, Diagnosis
from .forms import PatientForm, DiagnosisForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

# Existing Patient Views ...

@csrf_protect
@login_required
def patient_list(request):
    """
    View to display the list of patients with pagination.
    """
    patients = Patients.objects.all().order_by('-created')  # Fetch all patients ordered by creation date
    paginator = Paginator(patients, 10)  # Display 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = PatientForm()
    return render(request, 'patients/patient_list.html', {
        'page_obj': page_obj,
        'form': form
    })

def patient_detail(request, patient_id):
    """
    View to display the details of a specific patient and handle edit form.
    """
    patient = get_object_or_404(Patients, id=patient_id)
    diagnoses = patient.diagnoses.all().order_by('-diagnosis_date')  # Fetch related diagnoses
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            try:
                patient = form.save()
                updated_patient = Patients.objects.get(id=patient_id)
                data = {
                    'id': updated_patient.id,
                    'nric': updated_patient.nric,
                    'first_name': updated_patient.first_name,
                    'last_name': updated_patient.last_name,
                    'birth_date': updated_patient.birth_date.strftime('%m/%d/%Y') if updated_patient.birth_date else '',
                    'age': updated_patient.age,
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
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the patient.', 'error': str(e)})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the form.', 'errors': errors})
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'form': form,
        'diagnoses': diagnoses,
        'diagnosis_form': DiagnosisForm()
    })

def add_patient(request):
    """
    View to handle adding a new patient.
    """
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            try:
                patient = form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Prepare patient data to send back, including age
                    patient_data = {
                        'id': patient.id,
                        'nric': patient.nric,
                        'first_name': patient.first_name,
                        'last_name': patient.last_name,
                        'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
                        'age': patient.age,  # Include age
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
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'An error occurred while adding the patient.', 'error': str(e)})
                else:
                    messages.error(request, 'There was an error adding the patient. Please try again.')
                    return redirect('patient_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'errors': errors})
            else:
                messages.error(request, 'There was an error adding the patient. Please check the form and try again.')
                return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patients/add_patient.html', {'form': form})

@require_POST
def delete_patient(request, patient_id):
    """
    View to delete a single patient via AJAX or non-AJAX request.
    """
    patient = get_object_or_404(Patients, id=patient_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Optionally delete the profile photo file from storage
            if patient.profile_photo:
                patient.profile_photo.delete()
            patient.delete()
            return JsonResponse({'status': 'success', 'message': 'Patient has been successfully deleted.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the patient.', 'error': str(e)})
    else:
        try:
            # Optionally delete the profile photo file from storage
            if patient.profile_photo:
                patient.profile_photo.delete()
            patient.delete()
            messages.success(request, 'Patient has been successfully deleted.')
            return redirect('patient_list')
        except Exception as e:
            messages.error(request, 'An error occurred while deleting the patient.')
            return redirect('patient_list')

@require_POST
def bulk_delete_patients(request):
    """
    View to delete multiple patients via AJAX.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        patient_ids = request.POST.getlist('patient_ids')
        if patient_ids:
            try:
                patients = Patients.objects.filter(id__in=patient_ids)
                for patient in patients:
                    if patient.profile_photo:
                        patient.profile_photo.delete()
                patients.delete()
                return JsonResponse({'status': 'success', 'message': 'Selected patients have been successfully deleted.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the selected patients.', 'error': str(e)})
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
            'nric': patient.nric,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
            'age': patient.age,  # Include age
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
            try:
                patient = form.save()
                updated_patient = Patients.objects.get(id=patient_id)
                data = {
                    'id': updated_patient.id,
                    'nric': updated_patient.nric,
                    'first_name': updated_patient.first_name,
                    'last_name': updated_patient.last_name,
                    'birth_date': updated_patient.birth_date.strftime('%m/%d/%Y') if updated_patient.birth_date else '',
                    'age': updated_patient.age,  # Include age
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
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the patient.', 'error': str(e)})
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
                nric__icontains=query
            ) | Patients.objects.filter(
                first_name__icontains=query
            ) | Patients.objects.filter(
                last_name__icontains=query
            )
        else:
            patients = Patients.objects.all().order_by('-created')
        
        # Serialize patients
        patients_data = []
        for patient in patients:
            patients_data.append({
                'id': patient.id,
                'nric': patient.nric,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'birth_date': patient.birth_date.strftime('%m/%d/%Y') if patient.birth_date else '',
                'age': patient.age,  # Include age
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

# New Diagnosis Views

@login_required
def diagnosis_detail(request, nric):
    """
    View to display the details of a specific patient's diagnoses.
    """
    patient = get_object_or_404(Patients, nric=nric)
    diagnoses = patient.diagnoses.all().order_by('-diagnosis_date')  # Fetch related diagnoses with ordering
    paginator = Paginator(diagnoses, 10)  # 10 diagnoses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    diagnosis_form = DiagnosisForm()
    return render(request, 'patients/diagnosis_detail.html', {
        'patient': patient,
        'diagnoses': page_obj,
        'diagnosis_form': diagnosis_form
    })

@require_POST
@login_required
def add_diagnosis(request, nric):
    """
    View to add a new diagnosis for a specific patient via AJAX or standard POST request.
    """
    patient = get_object_or_404(Patients, nric=nric)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = DiagnosisForm(request.POST, request.FILES)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.patient = patient
            diagnosis.save()
            # Serialize the newly created diagnosis
            diagnosis_data = {
                'id': diagnosis.id,
                'apt': diagnosis.apt,
                'summary': diagnosis.summary,
                'instructions': diagnosis.instructions,
                'lifestyle': diagnosis.lifestyle,
                'next_apt': diagnosis.next_apt.strftime('%m/%d/%Y %H:%M') if diagnosis.next_apt else '',
                'image_url': diagnosis.image.url if diagnosis.image else '',
                'medication_status': diagnosis.medication_status,
                'diagnosis_date': diagnosis.diagnosis_date.strftime('%m/%d/%Y'),
            }
            return JsonResponse({'status': 'success', 'message': 'Diagnosis added successfully!', 'diagnosis': diagnosis_data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the diagnosis form.', 'errors': errors})
    else:
        form = DiagnosisForm(request.POST, request.FILES)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.patient = patient
            diagnosis.save()
            messages.success(request, 'Diagnosis has been successfully added.')
            return redirect('diagnosis_detail', nric=nric)
        else:
            messages.error(request, 'There was an error adding the diagnosis. Please check the form and try again.')
            return redirect('diagnosis_detail', nric=nric)

@require_POST
@login_required
def delete_diagnosis(request, nric, diagnosis_id):
    """
    View to delete a diagnosis via AJAX or standard POST request.
    """
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, patient__nric=nric)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Optionally delete the image file from storage
            if diagnosis.image:
                diagnosis.image.delete()
            diagnosis.delete()
            return JsonResponse({'status': 'success', 'message': 'Diagnosis has been successfully deleted.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the diagnosis.', 'error': str(e)})
    else:
        try:
            # Optionally delete the image file from storage
            if diagnosis.image:
                diagnosis.image.delete()
            diagnosis.delete()
            messages.success(request, 'Diagnosis has been successfully deleted.')
            return redirect('diagnosis_detail', nric=nric)
        except Exception as e:
            messages.error(request, 'An error occurred while deleting the diagnosis.')
            return redirect('diagnosis_detail', nric=nric)

@csrf_protect
@login_required
def edit_diagnosis(request, nric, diagnosis_id):
    """
    View to fetch and edit an existing diagnosis via AJAX or standard POST request.
    """
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, patient__nric=nric)
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = DiagnosisForm(request.POST, request.FILES, instance=diagnosis)
            if form.is_valid():
                try:
                    form.save()
                    # Serialize the updated diagnosis
                    updated_diagnosis = Diagnosis.objects.get(id=diagnosis_id)
                    diagnosis_data = {
                        'id': updated_diagnosis.id,
                        'apt': updated_diagnosis.apt,
                        'summary': updated_diagnosis.summary,
                        'instructions': updated_diagnosis.instructions,
                        'lifestyle': updated_diagnosis.lifestyle,
                        'next_apt': updated_diagnosis.next_apt.strftime('%m/%d/%Y %H:%M') if updated_diagnosis.next_apt else '',
                        'image_url': updated_diagnosis.image.url if updated_diagnosis.image else '',
                        'medication_status': updated_diagnosis.medication_status,
                        'diagnosis_date': updated_diagnosis.diagnosis_date.strftime('%m/%d/%Y'),
                    }
                    return JsonResponse({'status': 'success', 'message': 'Diagnosis updated successfully!', 'diagnosis': diagnosis_data})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the diagnosis.', 'error': str(e)})
            else:
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'message': 'There were errors in the diagnosis form.', 'errors': errors})
        else:
            form = DiagnosisForm(request.POST, request.FILES, instance=diagnosis)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Diagnosis has been successfully updated.')
                    return redirect('diagnosis_detail', nric=nric)
                except Exception as e:
                    messages.error(request, 'An error occurred while updating the diagnosis.')
                    return redirect('diagnosis_detail', nric=nric)
            else:
                messages.error(request, 'There was an error updating the diagnosis. Please check the form and try again.')
                return redirect('diagnosis_detail', nric=nric)
    else:
        form = DiagnosisForm(instance=diagnosis)
        return render(request, 'patients/edit_diagnosis.html', {
            'form': form,
            'diagnosis': diagnosis
        })

@login_required
def update_diagnosis(request, nric, diagnosis_id):
    """
    View to handle updating a diagnosis via AJAX.
    """
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, patient__nric=nric)
    if request.method == 'POST':
        form = DiagnosisForm(request.POST, request.FILES, instance=diagnosis)
        if form.is_valid():
            try:
                form.save()
                updated_diagnosis = Diagnosis.objects.get(id=diagnosis_id)
                diagnosis_data = {
                    'id': updated_diagnosis.id,
                    'apt': updated_diagnosis.apt,
                    'summary': updated_diagnosis.summary,
                    'instructions': updated_diagnosis.instructions,
                    'lifestyle': updated_diagnosis.lifestyle,
                    'next_apt': updated_diagnosis.next_apt.strftime('%m/%d/%Y %H:%M') if updated_diagnosis.next_apt else '',
                    'image_url': updated_diagnosis.image.url if updated_diagnosis.image else '',
                    'medication_status': updated_diagnosis.medication_status,
                    'diagnosis_date': updated_diagnosis.diagnosis_date.strftime('%m/%d/%Y'),
                }
                return JsonResponse({'status': 'success', 'message': 'Diagnosis updated successfully!', 'diagnosis': diagnosis_data})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the diagnosis.', 'error': str(e)})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'There were errors in the diagnosis form.', 'errors': errors})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@require_POST
@login_required
def bulk_delete_diagnoses(request, nric):
    """
    View to delete multiple diagnoses via AJAX.
    """
    patient = get_object_or_404(Patients, nric=nric)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        diagnosis_ids = request.POST.getlist('diagnosis_ids')
        if diagnosis_ids:
            try:
                diagnoses = Diagnosis.objects.filter(id__in=diagnosis_ids, patient=patient)
                for diagnosis in diagnoses:
                    if diagnosis.image:
                        diagnosis.image.delete()
                diagnoses.delete()
                return JsonResponse({'status': 'success', 'message': 'Selected diagnoses have been successfully deleted.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while deleting the selected diagnoses.', 'error': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'No diagnoses selected.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def search_diagnoses(request, nric):
    """
    View to handle real-time search with autocomplete functionality for diagnoses.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        patient = get_object_or_404(Patients, nric=nric)
        if query:
            diagnoses = patient.diagnoses.filter(
                apt__icontains=query
            ) | patient.diagnoses.filter(
                summary__icontains=query
            ) | patient.diagnoses.filter(
                instructions__icontains=query
            ) | patient.diagnoses.filter(
                lifestyle__icontains=query
            )
        else:
            diagnoses = patient.diagnoses.all().order_by('-diagnosis_date')

        # Serialize diagnoses
        diagnoses_data = []
        for diagnosis in diagnoses:
            diagnoses_data.append({
                'id': diagnosis.id,
                'apt': diagnosis.apt,
                'summary': diagnosis.summary,
                'instructions': diagnosis.instructions,
                'lifestyle': diagnosis.lifestyle,
                'next_apt': diagnosis.next_apt.strftime('%m/%d/%Y %H:%M') if diagnosis.next_apt else '',
                'image_url': diagnosis.image.url if diagnosis.image else '',
                'medication_status': diagnosis.medication_status,
                'diagnosis_date': diagnosis.diagnosis_date.strftime('%m/%d/%Y'),
            })
        return JsonResponse({'status': 'success', 'diagnoses': diagnoses_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def diagnosis_detail(request, nric):
    # Fetch the patient object based on NRIC
    patient = get_object_or_404(Patients, nric=nric)
    
    # Fetch all diagnoses related to the patient, ordered by diagnosis_date descending
    diagnoses_queryset = patient.diagnoses.all().order_by('-diagnosis_date')
    
    # Pagination setup (optional, adjust per your requirements)
    paginator = Paginator(diagnoses_queryset, 10)  # Show 10 diagnoses per page
    page_number = request.GET.get('page')
    diagnoses = paginator.get_page(page_number)
    
    if request.method == 'POST':
        # Handle form submission for adding a new diagnosis
        diagnosis_form = DiagnosisForm(request.POST, request.FILES)
        if diagnosis_form.is_valid():
            new_diagnosis = diagnosis_form.save(commit=False)
            new_diagnosis.patient = patient  # Associate with the current patient
            new_diagnosis.save()
            # Redirect or return a success response
            return redirect('diagnosis_detail', nric=nric)
        else:
            # If form is invalid, you might want to handle errors
            pass
    else:
        # For GET requests, instantiate a blank form
        diagnosis_form = DiagnosisForm()
    
    context = {
        'patient': patient,
        'diagnoses': diagnoses,
        'diagnosis_form': diagnosis_form,  # Pass the form to the template
    }
    
    return render(request, 'patients/diagnosis_detail.html', context)