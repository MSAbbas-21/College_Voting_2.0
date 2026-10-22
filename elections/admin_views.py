from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from accounts.decorators import admin_required
from elections.models import Election
from elections.forms import ElectionForm
from candidates.models import Candidate
from candidates.forms import CandidateForm
from voting.models import VoterParticipation, Vote
from results.services import calculate_election_results


@admin_required
def admin_dashboard(request):
    """
    Main Administrator Dashboard with system metrics, quick actions,
    pending student queue, and election overview.
    """
    now = timezone.now()

    # Core statistics for metrics cards
    total_students = CustomUser.objects.filter(role='student').count()
    pending_approvals = CustomUser.objects.filter(role='student', approval_status='pending').count()
    approved_students = CustomUser.objects.filter(role='student', approval_status='approved').count()
    total_candidates = Candidate.objects.count()
    active_elections = Election.objects.filter(status='active', start_date__lte=now, end_date__gte=now).count()
    total_elections = Election.objects.count()
    total_votes = Vote.objects.count()

    # Pending student approval queue (top 5)
    pending_students = CustomUser.objects.filter(
        role='student',
        approval_status='pending'
    ).order_by('-date_joined')[:5]

    # Recent elections with vote and candidate counts
    recent_elections = Election.objects.annotate(
        c_count=Count('candidates', distinct=True),
        v_count=Count('votes', distinct=True)
    ).order_by('-created_at')[:5]

    # Recent participation records (Voter student name & election - NO candidate choice exposed)
    recent_activity = VoterParticipation.objects.select_related('student', 'election').order_by('-voted_at')[:8]

    context = {
        'total_students': total_students,
        'pending_approvals': pending_approvals,
        'approved_students': approved_students,
        'total_candidates': total_candidates,
        'active_elections': active_elections,
        'total_elections': total_elections,
        'total_votes': total_votes,
        'pending_students': pending_students,
        'recent_elections': recent_elections,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ==========================================
# Student Management Views
# ==========================================

@admin_required
def students_list(request):
    """
    Manage student registrations: filter by status, search by name/roll/email.
    """
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    students = CustomUser.objects.filter(role='student')

    if status_filter in ['pending', 'approved', 'rejected']:
        students = students.filter(approval_status=status_filter)

    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    counts = {
        'all': CustomUser.objects.filter(role='student').count(),
        'pending': CustomUser.objects.filter(role='student', approval_status='pending').count(),
        'approved': CustomUser.objects.filter(role='student', approval_status='approved').count(),
        'rejected': CustomUser.objects.filter(role='student', approval_status='rejected').count(),
    }

    context = {
        'students': students.order_by('-date_joined'),
        'status_filter': status_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'dashboard/students_list.html', context)


@admin_required
def student_detail(request, user_id):
    """View detailed profile of a student."""
    student = get_object_or_404(CustomUser, pk=user_id, role='student')
    participations = student.election_participations.select_related('election').order_by('-voted_at')
    
    context = {
        'student': student,
        'participations': participations,
    }
    return render(request, 'dashboard/student_detail.html', context)


@admin_required
@require_POST
def student_approve(request, user_id):
    """Approve a student account for voting."""
    student = get_object_or_404(CustomUser, pk=user_id, role='student')
    student.approve(request.user)
    messages.success(request, f"Student {student.get_full_name()} ({student.student_id}) has been approved.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:students_list')


@admin_required
@require_POST
def student_reject(request, user_id):
    """Reject a student registration with optional note."""
    student = get_object_or_404(CustomUser, pk=user_id, role='student')
    reason = request.POST.get('rejection_reason', 'Details did not match college records.')
    student.reject(request.user, reason=reason)
    messages.warning(request, f"Student {student.get_full_name()} ({student.student_id}) has been rejected.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:students_list')


@admin_required
@require_POST
def student_toggle_active(request, user_id):
    """Activate or deactivate a student account."""
    student = get_object_or_404(CustomUser, pk=user_id, role='student')
    student.is_active = not student.is_active
    student.save(update_fields=['is_active'])
    status_str = "activated" if student.is_active else "deactivated"
    messages.info(request, f"Student account for {student.get_full_name()} has been {status_str}.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:students_list')


# ==========================================
# Election Management Views
# ==========================================

@admin_required
def elections_list(request):
    """List and manage all elections."""
    elections = Election.objects.annotate(
        c_count=Count('candidates', distinct=True),
        v_count=Count('votes', distinct=True)
    ).order_by('-created_at')

    return render(request, 'dashboard/election_list.html', {'elections': elections})


@admin_required
def election_create(request):
    """Create a new election."""
    if request.method == 'POST':
        form = ElectionForm(request.POST, request.FILES)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            messages.success(request, f"Election '{election.title}' created successfully!")
            return redirect('dashboard:election_detail', pk=election.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ElectionForm()

    return render(request, 'dashboard/election_form.html', {'form': form, 'title': 'Create New Election'})


@admin_required
def election_edit(request, pk):
    """Edit an existing election."""
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        form = ElectionForm(request.POST, request.FILES, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, f"Election '{election.title}' updated successfully!")
            return redirect('dashboard:election_detail', pk=election.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ElectionForm(instance=election)

    return render(request, 'dashboard/election_form.html', {'form': form, 'election': election, 'title': f"Edit {election.title}"})


@admin_required
def election_detail_admin(request, pk):
    """Administrator view of election, candidates, and live statistics."""
    election = get_object_or_404(Election, pk=pk)
    results = calculate_election_results(election)
    candidates = election.candidates.all()
    participations = election.participating_voters.select_related('student').order_by('-voted_at')[:20]

    context = {
        'election': election,
        'results': results,
        'candidates': candidates,
        'participations': participations,
    }
    return render(request, 'dashboard/election_detail.html', context)


@admin_required
@require_POST
def election_toggle_status(request, pk):
    """Toggle election status between active and closed."""
    election = get_object_or_404(Election, pk=pk)
    if election.status == 'active':
        election.status = 'closed'
        messages.info(request, f"Election '{election.title}' voting has been closed.")
    else:
        election.status = 'active'
        messages.success(request, f"Election '{election.title}' is now open and active!")
    election.save(update_fields=['status'])
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:elections_list')


@admin_required
@require_POST
def election_toggle_publish(request, pk):
    """Toggle publication of results for public and students."""
    election = get_object_or_404(Election, pk=pk)
    election.is_published = not election.is_published
    election.save(update_fields=['is_published'])
    state_str = "published and visible to everyone" if election.is_published else "hidden from public view"
    messages.success(request, f"Results for '{election.title}' are now {state_str}.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:elections_list')


@admin_required
@require_POST
def election_delete(request, pk):
    """Delete an election and its associated candidates & votes."""
    election = get_object_or_404(Election, pk=pk)
    title = election.title
    election.delete()
    messages.success(request, f"Election '{title}' was successfully deleted.")
    return redirect('dashboard:elections_list')


# ==========================================
# Candidate Management Views
# ==========================================

@admin_required
def candidates_list(request):
    """List all candidates with election filter."""
    election_id = request.GET.get('election')
    candidates = Candidate.objects.select_related('election').all()
    
    if election_id:
        candidates = candidates.filter(election_id=election_id)
        
    elections = Election.objects.all().order_by('-start_date')

    context = {
        'candidates': candidates.order_by('election', 'position', 'name'),
        'elections': elections,
        'selected_election': election_id,
    }
    return render(request, 'dashboard/candidate_list.html', context)


@admin_required
def candidate_create(request):
    """Add a new candidate."""
    initial = {}
    if 'election' in request.GET:
        initial['election'] = request.GET.get('election')

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save()
            messages.success(request, f"Candidate {candidate.name} added to {candidate.election.title}!")
            return redirect('dashboard:candidates_list')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = CandidateForm(initial=initial)

    return render(request, 'dashboard/candidate_form.html', {'form': form, 'title': 'Add New Candidate'})


@admin_required
def candidate_edit(request, pk):
    """Edit candidate profile."""
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, f"Candidate {candidate.name} updated successfully!")
            return redirect('dashboard:candidates_list')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = CandidateForm(instance=candidate)

    return render(request, 'dashboard/candidate_form.html', {'form': form, 'candidate': candidate, 'title': f"Edit {candidate.name}"})


@admin_required
@require_POST
def candidate_delete(request, pk):
    """Delete a candidate."""
    candidate = get_object_or_404(Candidate, pk=pk)
    name = candidate.name
    candidate.delete()
    messages.success(request, f"Candidate '{name}' has been deleted.")
    return redirect('dashboard:candidates_list')


# ==========================================
# Analytics & Reports View
# ==========================================

@admin_required
def analytics_summary(request):
    """System-wide voting turnout and department participation analytics."""
    departments = CustomUser.DEPARTMENT_CHOICES
    dept_stats = []
    
    for code, name in departments:
        reg_count = CustomUser.objects.filter(role='student', department=code).count()
        app_count = CustomUser.objects.filter(role='student', department=code, approval_status='approved').count()
        dept_stats.append({
            'code': code,
            'name': name,
            'registered': reg_count,
            'approved': app_count,
        })

    elections = Election.objects.all().order_by('-start_date')
    election_summaries = [calculate_election_results(el) for el in elections]

    context = {
        'dept_stats': dept_stats,
        'election_summaries': election_summaries,
    }
    return render(request, 'dashboard/analytics.html', context)
