from django.db import models
from datetime import date

class Patients(models.Model):
    nric = models.CharField(max_length=20, unique=True, default="UNKNOWN-NRIC")
    first_name = models.CharField(max_length=255, blank=True, null=True, default="Unknown")
    last_name = models.CharField(max_length=255, blank=True, null=True, default="Unknown")
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default="Not specified")
    address = models.TextField(blank=True, null=True, default="No address provided")
    phone = models.CharField(max_length=20, blank=True, null=True, default="N/A")
    fax = models.CharField(max_length=20, blank=True, null=True, default="N/A")
    email = models.EmailField(blank=True, null=True, default="unknown@example.com")
    consented = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True, default="No remarks")
    active = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, help_text="Upload a profile photo for the patient.")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            return age
        return None

    def __str__(self):
        return f"{self.first_name} {self.last_name} (NRIC: {self.nric})"

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patients, related_name='diagnoses', on_delete=models.CASCADE)
    apt = models.CharField(max_length=50, blank=True, null=True, default="Not specified")
    summary = models.TextField(blank=True, null=True, default="No summary provided")
    instructions = models.TextField(blank=True, null=True, default="No instructions")
    lifestyle = models.TextField(blank=True, null=True, default="No lifestyle details")
    next_apt = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='diagnosis_images/', blank=True, null=True)
    medication_status = models.CharField(max_length=50, choices=[('Issued', 'Issued'), ('Invoiced', 'Invoiced')], default='Invoiced')
    diagnosis_date = models.DateField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Diagnoses"
        ordering = ['-diagnosis_date', '-created']

    def __str__(self):
        return f"Diagnosis for {self.patient.nric} on {self.diagnosis_date}"
