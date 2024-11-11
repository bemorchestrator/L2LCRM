from django.db import models
from datetime import date

class Patients(models.Model):
    patient_no = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nric = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    consented = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        help_text="Upload a profile photo for the patient."
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        """Calculates the age of the patient based on the birth_date."""
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            return age
        return None

    def __str__(self):
        # Assuming you want to display first and last name
        return f"{self.first_name} {self.last_name} ({self.patient_no})"
