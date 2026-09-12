from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Category, Proposal, PortfolioProject, Service, ProjectRequest
from .forms import JobForm, ProposalForm
from users.models import CustomUser, Notification

def job_list_view(request):
    jobs = Job.objects.filter(is_approved=True, status='OPEN').select_related('client', 'category')
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    exp = request.GET.get('exp', '')
    min_b = request.GET.get('min_b', '')
    max_b = request.GET.get('max_b', '')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills_required__icontains=query)
        )

    if cat_slug:
        jobs = jobs.filter(category__slug=cat_slug)

    if exp:
        jobs = jobs.filter(experience_level=exp)

    if min_b:
        try:
            jobs = jobs.filter(budget_max__gte=float(min_b))
        except ValueError:
            pass

    if max_b:
        try:
            jobs = jobs.filter(budget_min__lte=float(max_b))
        except ValueError:
            pass

    context = {
        'jobs': jobs,
        'categories': categories,
        'query': query,
        'selected_category': cat_slug,
        'exp': exp,
        'min_b': min_b,
        'max_b': max_b,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    user_proposal = None
    existing_contract = None

    if request.user.is_authenticated:
        if request.user.is_freelancer():
            user_proposal = Proposal.objects.filter(job=job, freelancer=request.user).first()
        from contracts.models import Contract
        existing_contract = Contract.objects.filter(job=job).first()

    if request.method == 'POST' and request.user.is_authenticated and request.user.is_freelancer():
        if user_proposal:
            messages.warning(request, "You have already submitted a proposal for this job.")
            return redirect('jobs:job_detail', pk=job.pk)

        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.job = job
            proposal.freelancer = request.user
            proposal.save()

            Notification.objects.create(
                user=job.client,
                title=f"New Proposal for '{job.title[:30]}...'",
                message=f"{request.user.username} submitted a proposal (${proposal.bid_amount}) for your job.",
                link=f"/jobs/{job.pk}/"
            )

            messages.success(request, "Your proposal has been submitted successfully!")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = ProposalForm()

    context = {
        'job': job,
        'form': form,
        'user_proposal': user_proposal,
        'existing_contract': existing_contract,
        'proposals': job.proposals.select_related('freelancer', 'freelancer__profile') if request.user == job.client else []
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_create_view(request):
    if not request.user.is_client() and not request.user.is_superuser:
        messages.error(request, "Only client accounts can post new jobs.")
        return redirect('jobs:job_list')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()

            messages.success(request, "Your job posting has been created successfully!")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()

    return render(request, 'jobs/job_create.html', {'form': form})


@login_required
def proposal_accept_view(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    job = proposal.job

    if request.user != job.client:
        messages.error(request, "You are not authorized to accept this proposal.")
        return redirect('jobs:job_detail', pk=job.pk)

    proposal.status = 'ACCEPTED'
    proposal.save()

    job.proposals.exclude(pk=proposal.pk).update(status='REJECTED')
    job.status = 'IN_PROGRESS'
    job.save()

    from contracts.models import Contract
    contract, created = Contract.objects.get_or_create(
        job=job,
        client=job.client,
        freelancer=proposal.freelancer,
        defaults={'agreed_amount': proposal.bid_amount, 'status': 'ACTIVE'}
    )

    Notification.objects.create(
        user=proposal.freelancer,
        title="Proposal Accepted! 🎉",
        message=f"{job.client.username} accepted your proposal for '{job.title}'. Contract is now active!",
        link=f"/contracts/{contract.pk}/"
    )

    messages.success(request, f"Proposal from {proposal.freelancer.username} accepted! Contract created.")
    return redirect('contracts:contract_detail', pk=contract.pk)


# New Spec Extensions: Projects Showcase & Project Requests

def project_showcase_view(request):
    projects = PortfolioProject.objects.all().select_related('freelancer', 'freelancer__profile', 'category')
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')

    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(technologies__icontains=query)
        )

    if cat_slug:
        projects = projects.filter(category__slug=cat_slug)

    context = {
        'projects': projects,
        'categories': categories,
        'query': query,
        'selected_category': cat_slug,
    }
    return render(request, 'jobs/project_showcase.html', context)


def project_detail_view(request, pk):
    project = get_object_or_404(PortfolioProject, pk=pk)
    return render(request, 'jobs/project_detail.html', {'project': project})


@login_required
def create_project_request_view(request, freelancer_id):
    freelancer = get_object_or_404(CustomUser, pk=freelancer_id, role='FREELANCER')

    if request.user == freelancer:
        messages.error(request, "You cannot send a project request to yourself.")
        return redirect('users:profile_detail', username=freelancer.username)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        required_technology = request.POST.get('required_technology', '')
        budget = request.POST.get('budget', 15000)
        deadline_days = request.POST.get('deadline_days', 30)

        req = ProjectRequest.objects.create(
            client=request.user,
            freelancer=freelancer,
            title=title,
            description=description,
            required_technology=required_technology,
            budget=budget,
            deadline_days=deadline_days
        )

        Notification.objects.create(
            user=freelancer,
            title="New Project Request Received! 📋",
            message=f"{request.user.username} sent you a project request: '{title}' (Budget: ₹{budget}).",
            link="/dashboard/"
        )

        messages.success(request, f"Project request sent to {freelancer.username} successfully!")
        return redirect('dashboard:dashboard')

    return redirect('users:profile_detail', username=freelancer.username)


@login_required
def update_request_status_view(request, pk):
    req = get_object_or_404(ProjectRequest, pk=pk)

    if request.user != req.freelancer and request.user != req.client and not request.user.is_superuser:
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard:dashboard')

    new_status = request.GET.get('status')
    if new_status in ['ACCEPTED', 'REJECTED', 'COMPLETED']:
        req.status = new_status
        req.save()

        notify_user = req.client if request.user == req.freelancer else req.freelancer
        Notification.objects.create(
            user=notify_user,
            title=f"Project Request Status Updated ({new_status})",
            message=f"Status for '{req.title}' has been updated to {new_status}.",
            link="/dashboard/"
        )

        messages.success(request, f"Project request status updated to {new_status}.")

    return redirect('dashboard:dashboard')
