from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon_class = models.CharField(max_length=50, default='fa-code', help_text="FontAwesome icon class")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Job(models.Model):
    BUDGET_TYPE_CHOICES = (
        ('FIXED', 'Fixed Price'),
        ('HOURLY', 'Hourly Rate'),
    )
    EXPERIENCE_CHOICES = (
        ('ENTRY', 'Entry Level'),
        ('INTERMEDIATE', 'Intermediate'),
        ('EXPERT', 'Expert'),
    )
    STATUS_CHOICES = (
        ('OPEN', 'Open for Bids'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CLOSED', 'Closed'),
    )

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES, default='FIXED')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='INTERMEDIATE')
    skills_required = models.CharField(max_length=255, blank=True, help_text="Comma-separated skills")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def get_skills_list(self):
        if not self.skills_required:
            return []
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def proposal_count(self):
        return self.proposals.count()

    def __str__(self):
        return self.title


class Proposal(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals_submitted')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(default=7)
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'freelancer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Proposal by {self.freelancer.username} for {self.job.title}"


class PortfolioProject(models.Model):
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    technologies = models.CharField(max_length=255, help_text="e.g. React, Django, PostgreSQL")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_projects')
    github_url = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    role_description = models.CharField(max_length=150, default="Full Stack Developer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_tech_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    def __str__(self):
        return f"{self.title} by {self.freelancer.username}"


class Service(models.Model):
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00)
    currency = models.CharField(max_length=10, default="₹")
    technologies = models.CharField(max_length=255, help_text="e.g. React, Django, PostgreSQL")
    delivery_days = models.IntegerField(default=15, help_text="e.g. 15-30 days")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_tech_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    def __str__(self):
        return f"{self.title} - {self.currency}{self.starting_price}"


class ProjectRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_project_requests')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_project_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_technology = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="₹")
    deadline_days = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request for {self.title} ({self.get_status_display()})"
