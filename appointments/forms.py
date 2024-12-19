# appointments/forms.py
from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'  # Include all fields
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'time_of_birth': forms.TimeInput(attrs={'type': 'time'}),
            'drink_alcohol': forms.RadioSelect(choices=Appointment.drink_alcohol_choices),
            'whatsapp_contactable': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'smoke': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'prepares_meals': forms.CheckboxInput(),
            'skips_breakfast': forms.CheckboxInput(),
            'vegan': forms.CheckboxInput(),
            'join_mailing_list': forms.CheckboxInput(),
            'pdpa_consent': forms.CheckboxInput(),
            'informed_consent': forms.CheckboxInput(),
        }
