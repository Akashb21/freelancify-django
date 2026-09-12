from django.core.management.base import BaseCommand
from users.models import CustomUser, Profile, Skill, Favorite
from jobs.models import Category, Job, Proposal, PortfolioProject, Service, ProjectRequest
from chat.models import Conversation, Message
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds test data according to exact Functional Requirements specification'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting data seeding..."))

        # 1. Standard Skills Taxonomy (Section 25)
        skills_data = [
            ("Python", "PROGRAMMING"), ("Java", "PROGRAMMING"), ("C++", "PROGRAMMING"),
            ("JavaScript", "PROGRAMMING"), ("TypeScript", "PROGRAMMING"),
            ("React", "FRONTEND"), ("HTML", "FRONTEND"), ("CSS", "FRONTEND"), ("Next.js", "FRONTEND"),
            ("Django", "BACKEND"), ("Node.js", "BACKEND"), ("Express", "BACKEND"),
            ("PostgreSQL", "DATABASE"), ("MySQL", "DATABASE"), ("MongoDB", "DATABASE"),
            ("Git", "OTHER"), ("Docker", "OTHER"), ("AWS", "OTHER"), ("Machine Learning", "OTHER"),
        ]

        for s_name, cat in skills_data:
            Skill.objects.get_or_create(name=s_name, defaults={'category_type': cat})
        self.stdout.write("Seeded Skills.")

        # 2. Categories (Section 24)
        categories_data = [
            ("Web Development", "fa-code"),
            ("Mobile Development", "fa-mobile-screen"),
            ("AI / Machine Learning", "fa-brain"),
            ("Data Science", "fa-database"),
            ("UI / UX Design", "fa-palette"),
            ("Backend Development", "fa-server"),
            ("Frontend Development", "fa-laptop-code"),
            ("Full Stack Development", "fa-layer-group"),
            ("Cloud / DevOps", "fa-cloud"),
        ]

        cats = {}
        for name, icon in categories_data:
            slug = slugify(name)
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon_class': icon}
            )
            cats[name] = cat
        self.stdout.write("Seeded Categories.")

        # 3. Users (Section 4 Rahul Kumar Example)
        if not CustomUser.objects.filter(username='admin').exists():
            admin = CustomUser.objects.create_superuser('admin', 'admin@freelancify.com', 'admin123')
            admin.role = 'ADMIN'
            admin.save()
            Profile.objects.get_or_create(user=admin, defaults={'title': 'Platform Administrator'})

        client1, c1_created = CustomUser.objects.get_or_create(
            username='techcorp',
            defaults={'email': 'contact@techcorp.com', 'first_name': 'Sarah', 'last_name': 'Jenkins', 'role': 'CLIENT', 'location': 'San Francisco, CA'}
        )
        if c1_created:
            client1.set_password('pass123')
            client1.save()
            Profile.objects.get_or_create(user=client1, defaults={'title': 'VP of Engineering', 'company_name': 'TechCorp Solutions'})

        # Rahul Kumar (Spec Example Freelancer)
        rahul, r_created = CustomUser.objects.get_or_create(
            username='rahul_kumar',
            defaults={'email': 'rahul@dev.io', 'first_name': 'Rahul', 'last_name': 'Kumar', 'role': 'FREELANCER', 'location': 'Bengaluru, India'}
        )
        if r_created:
            rahul.set_password('pass123')
            rahul.save()
            Profile.objects.get_or_create(user=rahul, defaults={
                'title': 'Full Stack Developer',
                'bio': '2+ years experience developing high performance web platforms using React, Django, Python, and PostgreSQL.',
                'hourly_rate': 800.00,
                'currency': '₹',
                'experience': '2+ years',
                'education': 'B.Tech in Computer Science',
                'availability': 'Available for hire',
                'skills': 'React, Django, Python, PostgreSQL',
                'github_link': 'https://github.com',
                'linkedin_link': 'https://linkedin.com',
                'rating_average': 4.85,
                'rating_count': 12
            })

        david, d_created = CustomUser.objects.get_or_create(
            username='dev_master',
            defaults={'email': 'david@devmaster.dev', 'first_name': 'David', 'last_name': 'Chen', 'role': 'FREELANCER', 'location': 'Seattle, WA'}
        )
        if d_created:
            david.set_password('pass123')
            david.save()
            Profile.objects.get_or_create(user=david, defaults={
                'title': 'Senior Python & React Architect',
                'bio': 'Building scalable SaaS web applications with Django and React.',
                'hourly_rate': 1200.00,
                'currency': '₹',
                'skills': 'Python, Django, React, TypeScript, Docker, AWS',
                'rating_average': 4.95,
                'rating_count': 18
            })

        self.stdout.write("Seeded Users.")

        # 4. Portfolio Projects (Section 5 Example)
        PortfolioProject.objects.get_or_create(
            freelancer=rahul,
            title='E-Commerce Platform',
            defaults={
                'description': 'A full-stack e-commerce platform with authentication, product management, cart and order management.',
                'technologies': 'React, Django, PostgreSQL',
                'category': cats['Full Stack Development'],
                'github_url': 'https://github.com',
                'demo_url': 'https://example.com',
                'role_description': 'Full Stack Lead Developer'
            }
        )

        # 5. Service Listing (Section 9 Example)
        Service.objects.get_or_create(
            freelancer=rahul,
            title='Full Stack Web Development',
            defaults={
                'description': 'End-to-end modern web application development with responsive React frontend and robust Django API backend.',
                'starting_price': 15000.00,
                'currency': '₹',
                'technologies': 'React, Django, PostgreSQL',
                'delivery_days': 20
            }
        )

        # 6. Sample Project Request (Section 10 Example)
        ProjectRequest.objects.get_or_create(
            client=client1,
            freelancer=rahul,
            title='Build an E-commerce Website',
            defaults={
                'description': 'Looking to build a custom responsive store front with product filtering and cart integration.',
                'required_technology': 'React + Django',
                'budget': 30000.00,
                'currency': '₹',
                'deadline_days': 30,
                'status': 'PENDING'
            }
        )

        # 7. Saved Developer Favorite (Section 15 Example)
        Favorite.objects.get_or_create(client=client1, freelancer=rahul)

        self.stdout.write(self.style.SUCCESS("Data seeding matching exact Functional Requirements complete!"))
