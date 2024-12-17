# appointments/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import AppointmentForm

def book_appointment(request):
    if request.method == 'POST':
        if request.is_ajax():
            form = AppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Appointment booked successfully!'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
        else:
            form = AppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('appointment_success')  # Redirect after successful form submission
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/book_appointment.html', {'form': form})
