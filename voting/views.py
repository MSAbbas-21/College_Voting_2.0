from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.views.decorators.http import require_POST
from django.utils import timezone

from accounts.decorators import approved_voter_required, student_required
from elections.models import Election
from candidates.models import Candidate
from voting.models import VoterParticipation, Vote


@student_required
@approved_voter_required
def ballot_view(request, slug):
    """
    Displays the ballot for an election with all candidate choices.
    Validates eligibility, timing, and ensures voter has not already voted.
    """
    election = get_object_or_404(Election, slug=slug)

    # Verify election is active and within window
    if not election.is_currently_open:
        messages.warning(
            request,
            f"Voting is not currently open for '{election.title}'. (Status: {election.time_status})"
        )
        return redirect('accounts:student_dashboard')

    # Verify student hasn't already voted
    has_voted = VoterParticipation.objects.filter(
        student=request.user,
        election=election
    ).exists()

    if has_voted:
        receipt = VoterParticipation.objects.filter(
            student=request.user,
            election=election
        ).first()
        messages.info(
            request,
            f"You have already cast your vote in '{election.title}'. "
            f"Your verification receipt is {receipt.receipt_code if receipt else 'recorded'}."
        )
        return redirect('accounts:student_dashboard')

    candidates = election.candidates.all().order_by('position', 'name')
    if not candidates.exists():
        messages.warning(request, "There are currently no candidates registered for this election.")
        return redirect('accounts:student_dashboard')

    # Group candidates by position if needed or display in list
    context = {
        'election': election,
        'candidates': candidates,
    }
    return render(request, 'voting/ballot.html', context)


@student_required
@approved_voter_required
@require_POST
def confirm_vote(request, slug):
    """
    Step 2 of Voting: Shows an explicit confirmation page before final submission.
    """
    election = get_object_or_404(Election, slug=slug)

    if not election.is_currently_open:
        messages.error(request, "This election is no longer open for voting.")
        return redirect('accounts:student_dashboard')

    if VoterParticipation.objects.filter(student=request.user, election=election).exists():
        messages.error(request, "You have already cast your ballot in this election.")
        return redirect('accounts:student_dashboard')

    candidate_id = request.POST.get('candidate_id')
    if not candidate_id:
        messages.error(request, "Please select a candidate before proceeding.")
        return redirect('voting:ballot', slug=election.slug)

    candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)

    context = {
        'election': election,
        'candidate': candidate,
    }
    return render(request, 'voting/confirm_vote.html', context)


@student_required
@approved_voter_required
@require_POST
def submit_vote(request, slug):
    """
    Step 3 of Voting: Atomically records participation and anonymized ballot.
    Uses database transactions and unique constraint to prevent race conditions.
    """
    election = get_object_or_404(Election, slug=slug)

    # 1. Check time window
    if not election.is_currently_open:
        messages.error(request, "Voting has closed or is not currently open for this election.")
        return redirect('accounts:student_dashboard')

    # 2. Get and validate candidate
    candidate_id = request.POST.get('candidate_id')
    if not candidate_id:
        messages.error(request, "No candidate was selected.")
        return redirect('voting:ballot', slug=election.slug)

    candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)

    # 3. Atomic transaction to prevent double voting
    try:
        with transaction.atomic():
            # Check participation under atomic transaction
            if VoterParticipation.objects.filter(student=request.user, election=election).exists():
                messages.error(request, "Double voting prevented: You have already cast a vote in this election.")
                return redirect('accounts:student_dashboard')

            # Generate unique receipt token
            receipt_code = VoterParticipation.generate_receipt()

            # Record voter participation (links student + election)
            participation = VoterParticipation.objects.create(
                student=request.user,
                election=election,
                receipt_code=receipt_code
            )

            # Record secret ballot (links candidate + election, NO student identifier)
            Vote.objects.create(
                election=election,
                candidate=candidate
            )

    except IntegrityError:
        messages.error(request, "Duplicate vote submission rejected by database integrity constraints.")
        return redirect('accounts:student_dashboard')

    # Store receipt in session for display
    request.session['last_receipt'] = receipt_code
    request.session['voted_election_title'] = election.title

    return redirect('voting:vote_success', slug=election.slug)


@login_required
def vote_success(request, slug):
    """Displays success screen with the digital receipt code."""
    election = get_object_or_404(Election, slug=slug)
    receipt_code = request.session.get('last_receipt', '')

    context = {
        'election': election,
        'receipt_code': receipt_code,
    }
    return render(request, 'voting/vote_success.html', context)


@student_required
def my_votes_history(request):
    """View voter's participation records and receipts."""
    participations = VoterParticipation.objects.filter(
        student=request.user
    ).select_related('election').order_by('-voted_at')

    context = {
        'participations': participations,
    }
    return render(request, 'voting/my_votes.html', context)
