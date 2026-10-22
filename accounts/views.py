from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q

from .models import CustomUser
from .forms import StudentRegistrationForm, StudentLoginForm, StudentProfileUpdateForm
from .decorators import student_required, admin_required
from elections.models import Election
from candidates.models import Candidate
from voting.models import VoterParticipation, Vote


def home_view(request):
    """
    Public landing page with hero banner, live election ticker,
    system highlights, and call-to-action buttons.
    """
    now = timezone.now()
    active_elections = Election.objects.filter(
        status='active',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('end_date')[:3]

    upcoming_elections = Election.objects.filter(
        status='active',
        start_date__gt=now
    ).order_by('start_date')[:3]

    published_results = Election.objects.filter(
        is_published=True
    ).order_by('-end_date')[:3]

    stats = {
        'total_students': CustomUser.objects.filter(role='student').count(),
        'approved_voters': CustomUser.objects.filter(role='student', approval_status='approved').count(),
        'total_elections': Election.objects.count(),
        'total_votes_cast': Vote.objects.count(),
    }

    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'published_results': published_results,
        'stats': stats,
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    """About page explaining the college voting system, security, and governance."""
    return render(request, 'public/about.html')


def contact_view(request):
    """Help & Contact page for students and faculty."""
    if request.method == 'POST':
        messages.success(request, "Your inquiry has been received by the Election Commission desk.")
        return redirect('public:contact')
    return render(request, 'public/contact.html')


def register_view(request):
    """
    Student registration view with server-side validation.
    New accounts require administrator approval.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Registration successful for {user.get_full_name()}! "
                "Your account is pending administrator verification. You may log in to check your status."
            )
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Login view supporting Student ID or College Email.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Authentication failed. Please check your credentials.")
    else:
        form = StudentLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logs out the active user session."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('public:home')


@login_required
def dashboard_redirect(request):
    """Directs users to the appropriate portal according to their role."""
    if request.user.is_admin_user:
        return redirect('dashboard:admin_dashboard')
    return redirect('accounts:student_dashboard')


@login_required
def student_dashboard(request):
    """
    Student home portal displaying:
    - Approval status alert
    - Active elections eligible to vote
    - Upcoming elections
    - Student voting participation history with receipts
    - Published election results
    """
    user = request.user
    if user.is_admin_user:
        return redirect('dashboard:admin_dashboard')

    now = timezone.now()

    # Elections the student has already voted in
    participated_election_ids = VoterParticipation.objects.filter(
        student=user
    ).values_list('election_id', flat=True)

    participations = VoterParticipation.objects.filter(
        student=user
    ).select_related('election').order_by('-voted_at')

    # Active elections currently open
    open_elections = Election.objects.filter(
        status='active',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('end_date')

    # Upcoming elections
    upcoming_elections = Election.objects.filter(
        status='active',
        start_date__gt=now
    ).order_by('start_date')

    # Published results
    published_results = Election.objects.filter(
        is_published=True
    ).order_by('-end_date')[:5]

    context = {
        'participated_election_ids': list(participated_election_ids),
        'participations': participations,
        'open_elections': open_elections,
        'upcoming_elections': upcoming_elections,
        'published_results': published_results,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def student_profile(request):
    """View and update student personal information."""
    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:student_profile')
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = StudentProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
