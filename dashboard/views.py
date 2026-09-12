from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Category, Proposal, PortfolioProject, Service, ProjectRequest
from contracts.models import Contract, Review
from users.models import CustomUser, Favorite
from payments.models import Transaction

def home_view(request):
    featured_jobs = Job.objects.filter(status='OPEN', is_approved=True).select_related('client', 'category')[:6]
    categories = Category.objects.all()[:8]
    top_freelancers = CustomUser.objects.filter(role='FREELANCER').select_related('profile').order_by('-profile__rating_average')[:4]
    featured_projects = PortfolioProject.objects.all().select_related('freelancer', 'freelancer__profile')[:6]
    
    total_jobs_count = Job.objects.count()
    total_freelancers_count = CustomUser.objects.filter(role='FREELANCER').count()
    total_paid_out = sum([t.amount for t in Transaction.objects.filter(status='RELEASED')])

    context = {
        'featured_jobs': featured_jobs,
        'categories': categories,
        'top_freelancers': top_freelancers,
        'featured_projects': featured_projects,
        'total_jobs_count': total_jobs_count,
        'total_freelancers_count': total_freelancers_count,
        'total_paid_out': total_paid_out,
    }
    return render(request, 'home.html', context)


@login_required
def dashboard_view(request):
    user = request.user
    
    if user.is_client():
        posted_jobs = Job.objects.filter(client=user).order_by('-created_at')
        active_contracts = Contract.objects.filter(client=user, status='ACTIVE').select_related('freelancer', 'job')
        project_requests = ProjectRequest.objects.filter(client=user).select_related('freelancer', 'freelancer__profile')
        saved_developers = Favorite.objects.filter(client=user).select_related('freelancer', 'freelancer__profile')
        total_spent = user.profile.total_spent

        active_projects_count = active_contracts.count() + project_requests.filter(status='ACCEPTED').count()
        completed_projects_count = Contract.objects.filter(client=user, status='COMPLETED').count() + project_requests.filter(status='COMPLETED').count()

        context = {
            'role': 'CLIENT',
            'posted_jobs': posted_jobs,
            'active_contracts': active_contracts,
            'project_requests': project_requests,
            'saved_developers': saved_developers,
            'active_projects_count': active_projects_count,
            'completed_projects_count': completed_projects_count,
            'total_spent': total_spent,
        }
        return render(request, 'dashboard/client_dashboard.html', context)

    elif user.is_freelancer():
        active_contracts = Contract.objects.filter(freelancer=user, status='ACTIVE').select_related('client', 'job')
        submitted_proposals = Proposal.objects.filter(freelancer=user).select_related('job')
        completed_contracts = Contract.objects.filter(freelancer=user, status='COMPLETED').select_related('client', 'job')
        
        my_projects = PortfolioProject.objects.filter(freelancer=user)
        my_services = Service.objects.filter(freelancer=user)
        project_requests = ProjectRequest.objects.filter(freelancer=user).select_related('client')
        
        active_requests_count = project_requests.filter(status='PENDING').count()
        completed_projects_count = completed_contracts.count() + project_requests.filter(status='COMPLETED').count()
        total_projects_count = my_projects.count() + completed_projects_count
        profile_completion = user.profile.calculate_completion_percentage()
        total_earnings = user.profile.total_earnings

        context = {
            'role': 'FREELANCER',
            'active_contracts': active_contracts,
            'submitted_proposals': submitted_proposals,
            'completed_contracts': completed_contracts,
            'my_projects': my_projects,
            'my_services': my_services,
            'project_requests': project_requests,
            'active_requests_count': active_requests_count,
            'completed_projects_count': completed_projects_count,
            'total_projects_count': total_projects_count,
            'profile_completion': profile_completion,
            'total_earnings': total_earnings,
        }
        return render(request, 'dashboard/freelancer_dashboard.html', context)

    else: # Admin
        all_users = CustomUser.objects.all().order_by('-date_joined')[:10]
        pending_jobs = Job.objects.filter(is_approved=False)
        all_transactions = Transaction.objects.all()[:10]
        all_projects = PortfolioProject.objects.count()
        all_requests = ProjectRequest.objects.count()

        context = {
            'role': 'ADMIN',
            'all_users': all_users,
            'pending_jobs': pending_jobs,
            'all_transactions': all_transactions,
            'all_projects': all_projects,
            'all_requests': all_requests,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
