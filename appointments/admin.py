from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Dynamically include all fields
    list_display = [field.name for field in Appointment._meta.fields]

    # Use valid fields in filters
    list_filter = ('created_at',)  # Replace 'status' with 'created_at' for now
    search_fields = ('full_name', 'email', 'contact_number')
    ordering = ('-created_at',)
