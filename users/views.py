from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser, Profile, Notification, PortfolioItem, Favorite, Skill
from jobs.models import PortfolioProject, Service, ProjectRequest, Category
from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            Notification.objects.create(
                user=user,
                title="Welcome to Freelancify! 🎉",
                message="Your account has been created successfully. Discover developers or showcase your projects!",
                link="/users/profile/"
            )
            login(request, user)
            messages.success(request, f"Welcome to Freelancify, {user.username}!")
            return redirect('dashboard:dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    demo_role = request.GET.get('demo')
    if demo_role:
        demo_username = None
        if demo_role == 'freelancer':
            demo_username = 'rahul_kumar'
        elif demo_role == 'client':
            demo_username = 'techcorp'
        elif demo_role == 'admin':
            demo_username = 'admin'

        if demo_username:
            user = CustomUser.objects.filter(username=demo_username).first()
            if not user and demo_role == 'freelancer':
                user = CustomUser.objects.filter(role='FREELANCER').first()

            if user:
                login(request, user)
                messages.success(request, f"Logged in as Demo {user.get_role_display()} ({user.username})!")
                return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('home')

def freelancer_list_view(request):
    freelancers = CustomUser.objects.filter(role='FREELANCER').select_related('profile')
    
    query = request.GET.get('q', '')
    skill = request.GET.get('skill', '')
    exp = request.GET.get('exp', '')
    min_rate = request.GET.get('min_rate', '')
    max_rate = request.GET.get('max_rate', '')

    if query:
        freelancers = freelancers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profile__title__icontains=query) |
            Q(profile__skills__icontains=query)
        )

    if skill:
        freelancers = freelancers.filter(profile__skills__icontains=skill)

    if exp:
        freelancers = freelancers.filter(profile__experience__icontains=exp)

    if min_rate:
        try:
            freelancers = freelancers.filter(profile__hourly_rate__gte=float(min_rate))
        except ValueError:
            pass

    if max_rate:
        try:
            freelancers = freelancers.filter(profile__hourly_rate__lte=float(max_rate))
        except ValueError:
            pass

    saved_ids = []
    if request.user.is_authenticated and request.user.is_client():
        saved_ids = list(Favorite.objects.filter(client=request.user).values_list('freelancer_id', flat=True))

    context = {
        'freelancers': freelancers,
        'query': query,
        'skill': skill,
        'exp': exp,
        'min_rate': min_rate,
        'max_rate': max_rate,
        'saved_ids': saved_ids,
    }
    return render(request, 'users/freelancer_list.html', context)

def profile_detail_view(request, username):
    user_obj = get_object_or_404(CustomUser, username=username)
    profile = get_object_or_404(Profile, user=user_obj)
    
    from contracts.models import Review
    reviews = Review.objects.filter(reviewee=user_obj).select_related('reviewer')
    portfolio_projects = PortfolioProject.objects.filter(freelancer=user_obj)
    services = Service.objects.filter(freelancer=user_obj)
    
    is_saved = False
    if request.user.is_authenticated and request.user.is_client():
        is_saved = Favorite.objects.filter(client=request.user, freelancer=user_obj).exists()

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'reviews': reviews,
        'portfolio_projects': portfolio_projects,
        'services': services,
        'is_saved': is_saved,
    }
    return render(request, 'users/profile_detail.html', context)

@login_required
def toggle_favorite(request, freelancer_id):
    if not request.user.is_client():
        messages.error(request, "Only clients can save developers.")
        return redirect('users:freelancer_list')

    freelancer = get_object_or_404(CustomUser, pk=freelancer_id, role='FREELANCER')
    fav, created = Favorite.objects.get_or_create(client=request.user, freelancer=freelancer)
    
    if not created:
        fav.delete()
        messages.info(request, f"Removed {freelancer.username} from your saved developers.")
    else:
        messages.success(request, f"Saved {freelancer.username} to your favorites!")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('users:freelancer_list')

@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            # Optional: handle extra fields
            profile.experience = request.POST.get('experience', profile.experience)
            profile.education = request.POST.get('education', profile.education)
            profile.availability = request.POST.get('availability', profile.availability)
            profile.github_link = request.POST.get('github_link', profile.github_link)
            profile.linkedin_link = request.POST.get('linkedin_link', profile.linkedin_link)
            profile.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('users:profile_detail', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
    }
    return render(request, 'users/profile_edit.html', context)

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    notifications.update(is_read=True)
    return render(request, 'users/notifications.html', {'notifications': notifications})
