from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Election


def public_election_list(request):
    """Public listing of all elections (active, upcoming, and completed)."""
    now = timezone.now()
    active_elections = Election.objects.filter(
        status='active',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('end_date')

    upcoming_elections = Election.objects.filter(
        status='active',
        start_date__gt=now
    ).order_by('start_date')

    past_elections = Election.objects.filter(
        status__in=['closed', 'active'],
        end_date__lt=now
    ).order_by('-end_date')

    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'past_elections': past_elections,
    }
    return render(request, 'public/election_list.html', context)


def public_election_detail(request, slug):
    """Public view of an election, its candidates, positions, and manifestos."""
    election = get_object_or_404(Election, slug=slug)
    candidates = election.candidates.all().order_by('position', 'name')

    has_voted = False
    if request.user.is_authenticated and request.user.is_student:
        has_voted = election.participating_voters.filter(student=request.user).exists()

    context = {
        'election': election,
        'candidates': candidates,
        'has_voted': has_voted,
    }
    return render(request, 'public/election_detail.html', context)
