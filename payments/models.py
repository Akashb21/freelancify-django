from django.db import models
from django.conf import settings
import uuid

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('ESCROW_HELD', 'Funds Held in Escrow'),
        ('RELEASED', 'Released to Freelancer'),
        ('REFUNDED', 'Refunded to Client'),
    )

    invoice_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, related_name='transactions')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ESCROW_HELD')
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, default="Escrow Deposit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.invoice_number[:8]} - ${self.amount} ({self.get_status_display()})"
