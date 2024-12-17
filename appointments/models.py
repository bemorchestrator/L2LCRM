from django.db import models

class Appointment(models.Model):
    # Basic Information
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    nric_passport = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    time_of_birth = models.TimeField(blank=True, null=True)
    country_of_birth = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    whatsapp_contactable = models.BooleanField(default=False)
    referral_source = models.CharField(max_length=255)  # How did you hear about us?

    # Personal Details
    profession = models.CharField(max_length=100)
    race = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    marital_status_choices = [
        ('married', 'Married'),
        ('single', 'Single'),
        ('divorced', 'Divorced / Widowed'),
    ]
    marital_status = models.CharField(max_length=20, choices=marital_status_choices)
    number_of_children = models.PositiveIntegerField(blank=True, null=True)
    normal_delivery = models.BooleanField(default=False)

    # Lifestyle Information
    smoke = models.BooleanField(default=False)
    drink_alcohol_choices = [
        ('less_than_3', 'Yes, less than 3 times per week'),
        ('more_than_3', 'Yes, more than 3 times per week'),
        ('no', 'No'),
    ]
    drink_alcohol = models.CharField(max_length=20, choices=drink_alcohol_choices)
    special_diet = models.CharField(max_length=100, blank=True, null=True)
    current_conditions = models.CharField(max_length=50, blank=True, null=True)

    # Health Information
    medications_supplements = models.TextField()  # Pharmaceutical Medications, Supplements, Traditional Medicine
    symptoms_onset = models.CharField(max_length=255, blank=True, null=True)
    provoked_by = models.CharField(max_length=255, blank=True, null=True)
    better_with = models.CharField(max_length=255, blank=True, null=True)
    symptom_severity = models.PositiveSmallIntegerField(help_text="Severity from 1 - 10", blank=True, null=True)
    condition_notes = models.TextField(blank=True, null=True)  # How do you feel about the condition?

    # Specific Health Areas
    digestion = models.CharField(max_length=255, blank=True, null=True)
    menstrual_health = models.CharField(max_length=255, blank=True, null=True)
    heart_health = models.CharField(max_length=255, blank=True, null=True)
    nervous_system = models.CharField(max_length=255, blank=True, null=True)
    skin_condition = models.CharField(max_length=255, blank=True, null=True)
    past_surgery = models.TextField(blank=True, null=True)
    immune_health = models.CharField(max_length=255, blank=True, null=True)
    thyroid = models.CharField(max_length=255, blank=True, null=True)
    energy_level = models.CharField(max_length=255, blank=True, null=True)
    sleep_health = models.CharField(max_length=255, blank=True, null=True)

    # Lifestyle Preferences
    prepares_meals = models.BooleanField(default=False)
    skips_breakfast = models.BooleanField(default=False)
    breakfast_description = models.TextField(blank=True, null=True)
    vegan = models.BooleanField(default=False)
    daily_beverage = models.CharField(max_length=255, blank=True, null=True)
    daily_favorite_food = models.CharField(max_length=255, blank=True, null=True)

    # Communication Preferences
    join_mailing_list = models.BooleanField(default=False)

    # Consent Fields
    pdpa_consent = models.BooleanField(default=False)
    informed_consent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.full_name} - {self.date_of_birth}"
