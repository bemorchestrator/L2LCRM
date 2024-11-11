# transactions/models.py
from django.db import models
from patients.models import Patients

class Transaction(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='transactions')
    transaction_no = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(auto_now_add=True)
    issuer = models.CharField(max_length=255, default='JOHNTANG')  # Replace with dynamic logic if needed
    tel = models.CharField(max_length=20, blank=True, null=True)

    # Auto-fillable fields from the patient
    name = models.CharField(max_length=255, editable=False)
    email = models.EmailField(editable=False)
    address = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        """Ensure auto-filling of patient details and unique transaction number when a transaction is created."""
        if not self.id:  # Only populate for new transactions
            # Generate sequential transaction_no in format TXN00000
            last_transaction = Transaction.objects.order_by('-id').first()
            if last_transaction and last_transaction.transaction_no.startswith('TXN'):
                last_number = int(last_transaction.transaction_no[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.transaction_no = f"TXN{new_number:05d}"

            # Populate patient details
            self.name = f"{self.patient.first_name} {self.patient.last_name}"
            self.email = self.patient.email
            self.address = self.patient.address
            self.tel = self.patient.phone  # Automatically set tel from patient's phone
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.transaction_no} for {self.patient}"
