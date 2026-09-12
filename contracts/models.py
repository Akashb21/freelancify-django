from django.db import models
from django.conf import settings

class Contract(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active / Work in Progress'),
        ('SUBMITTED', 'Work Submitted - Pending Review'),
        ('COMPLETED', 'Completed'),
        ('DISPUTED', 'Under Dispute'),
        ('CANCELLED', 'Cancelled'),
    )
    job = models.OneToOneField('jobs.Job', on_delete=models.CASCADE, related_name='contract')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_contracts')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='freelancer_contracts')
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    is_escrow_funded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract #{self.id} - {self.job.title}"


class WorkSubmission(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='submissions')
    message = models.TextField()
    file_attachment = models.FileField(upload_to='submissions/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, help_text="GitHub repo, Figma, or staging link")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission for Contract #{self.contract.id} at {self.submitted_at}"


class Review(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(default=5, choices=[(i, f"{i} Stars") for i in range(1, 6)])
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username} ({self.rating}★)"
