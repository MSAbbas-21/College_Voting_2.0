from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from elections.models import Election
from .services import calculate_election_results


def results_index(request):
    """
    Public and student results directory.
    Only shows elections with published results (admins can see all).
    """
    is_admin = request.user.is_authenticated and request.user.is_admin_user

    if is_admin:
        elections = Election.objects.all().order_by('-end_date', '-created_at')
    else:
        elections = Election.objects.filter(is_published=True).order_by('-end_date')

    # Calculate summary stats for each election
    elections_with_data = []
    for el in elections:
        res = calculate_election_results(el)
        elections_with_data.append({
            'election': el,
            'summary': res,
        })

    context = {
        'elections_with_data': elections_with_data,
        'is_admin': is_admin,
    }
    return render(request, 'results/results_list.html', context)


def election_result_detail(request, slug):
    """
    Detailed result breakdown with vote counts, percentages,
    progress bars, and winner / tie alerts.
    """
    election = get_object_or_404(Election, slug=slug)
    is_admin = request.user.is_authenticated and request.user.is_admin_user

    # Restrict unpublished results to administrators
    if not election.is_published and not is_admin:
        messages.info(
            request,
            f"Results for '{election.title}' have not yet been published by the Election Commission."
        )
        return redirect('results:results_list')

    results = calculate_election_results(election)

    context = {
        'election': election,
        'results': results,
        'is_admin': is_admin,
    }
    return render(request, 'results/election_result.html', context)


def print_result_report(request, slug):
    """
    Print-friendly official college election certificate & tally report.
    """
    election = get_object_or_404(Election, slug=slug)
    is_admin = request.user.is_authenticated and request.user.is_admin_user

    if not election.is_published and not is_admin:
        messages.error(request, "Unpublished results cannot be printed.")
        return redirect('results:results_list')

    results = calculate_election_results(election)

    context = {
        'election': election,
        'results': results,
        'generated_at': timezone.now(),
    }
    return render(request, 'results/print_result.html', context)
