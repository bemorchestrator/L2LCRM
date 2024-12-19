from django import forms
from .models import Patients, Diagnosis

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = [
            'first_name',
            'last_name',
            'birth_date',
            'nric',
            'country',
            'address',
            'phone',
            'fax',
            'email',
            'consented',
            'remarks',
            'active',
            'profile_photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'birth_date': forms.DateInput(attrs={
                'placeholder': 'Birth Date',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'type': 'date'
            }),
            'nric': forms.TextInput(attrs={
                'placeholder': 'NRIC',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'Country',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Address',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'rows': 3
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'fax': forms.TextInput(attrs={
                'placeholder': 'Fax',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'consented': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'remarks': forms.Textarea(attrs={
                'placeholder': 'Remarks',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'rows': 3
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'profile_photo': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        # If creating a new patient, clear initial data to show placeholders
        if not self.instance.pk:
            for field in self.fields:
                self.fields[field].initial = None


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = [
            'apt',
            'summary',
            'instructions',
            'lifestyle',
            'next_apt',
            'medication_status',
            'diagnosis_date',
            'image'
        ]
        widgets = {
            'apt': forms.TextInput(attrs={
                'placeholder': 'APT Code',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'summary': forms.Textarea(attrs={
                'placeholder': 'Summary',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'rows': 3
            }),
            'instructions': forms.Textarea(attrs={
                'placeholder': 'Instructions',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'rows': 3
            }),
            'lifestyle': forms.Textarea(attrs={
                'placeholder': 'Lifestyle Recommendations',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'rows': 3
            }),
            'next_apt': forms.DateTimeInput(attrs={
                'placeholder': 'Next Appointment',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'type': 'datetime-local'
            }),
            'medication_status': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'diagnosis_date': forms.DateInput(attrs={
                'placeholder': 'Diagnosis Date',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white',
                'type': 'date'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(DiagnosisForm, self).__init__(*args, **kwargs)
        # If creating a new diagnosis, clear initial data to show placeholders
        if not self.instance.pk:
            for field in self.fields:
                if field != 'medication_status' and field != 'image':
                    self.fields[field].initial = ''
