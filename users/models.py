from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('CLIENT', 'Client / Employer'),
        ('FREELANCER', 'Freelancer / Professional'),
        ('ADMIN', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FREELANCER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True, default='Remote')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_client(self):
        return self.role == 'CLIENT'

    def is_freelancer(self):
        return self.role == 'FREELANCER'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('PROGRAMMING', 'Programming Languages'),
        ('FRONTEND', 'Frontend Development'),
        ('BACKEND', 'Backend Development'),
        ('DATABASE', 'Databases'),
        ('OTHER', 'Other Tools & Tech'),
    )
    name = models.CharField(max_length=50, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    title = models.CharField(max_length=150, blank=True, default="Full Stack Developer")
    bio = models.TextField(blank=True, default="Passionate software developer building modern web applications.")
    experience = models.CharField(max_length=50, blank=True, default="2+ years", help_text="e.g. 2+ years")
    education = models.CharField(max_length=150, blank=True, default="B.Tech in Computer Science")
    availability = models.CharField(max_length=50, blank=True, default="Available for hire", help_text="e.g. Available for hire, Part-time")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=800.00, help_text="Rate in ₹ or $")
    currency = models.CharField(max_length=10, default="₹")
    skills = models.CharField(max_length=255, blank=True, help_text="Comma-separated skills (e.g. React, Django, Python, PostgreSQL)")
    company_name = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    rating_count = models.IntegerField(default=1)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def calculate_completion_percentage(self):
        fields = [self.title, self.bio, self.experience, self.education, self.skills, self.github_link, self.user.avatar]
        filled = sum([1 for f in fields if f])
        return int((filled / len(fields)) * 100)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Favorite(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'freelancer')

    def __str__(self):
        return f"{self.client.username} saved {self.freelancer.username}"


class PortfolioItem(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    technologies = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.profile.user.username})"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
