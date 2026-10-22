from django.db.models import Count
from candidates.models import Candidate
from accounts.models import CustomUser


def calculate_election_results(election):
    """
    Computes election outcome, vote totals, percentages, voter turnout,
    and accurately resolves single winners or ties.
    """
    total_votes = election.votes.count()
    total_approved_students = CustomUser.objects.filter(
        role='student',
        approval_status='approved',
        is_active=True
    ).count()

    turnout_percentage = 0.0
    if total_approved_students > 0:
        turnout_percentage = round((total_votes / total_approved_students) * 100, 1)

    # Fetch candidates with their vote count
    candidate_list = list(
        election.candidates.annotate(total_candidate_votes=Count('votes')).order_by('-total_candidate_votes', 'name')
    )

    results_data = []
    max_votes = -1
    for c in candidate_list:
        v_count = c.total_candidate_votes
        if v_count > max_votes:
            max_votes = v_count

        pct = round((v_count / total_votes * 100), 1) if total_votes > 0 else 0.0
        results_data.append({
            'candidate': c,
            'votes': v_count,
            'percentage': pct,
            'is_winner': False,
            'is_tie': False,
        })

    # Determine winner or tie
    winner_names = []
    has_tie = False
    winner_text = "No votes cast yet"

    if total_votes > 0 and max_votes > 0:
        top_candidates = [item for item in results_data if item['votes'] == max_votes]
        if len(top_candidates) == 1:
            top_candidates[0]['is_winner'] = True
            winner_names.append(top_candidates[0]['candidate'].name)
            winner_text = f"Winner: {top_candidates[0]['candidate'].name} ({top_candidates[0]['candidate'].position}) with {max_votes} votes ({top_candidates[0]['percentage']}%)"
        elif len(top_candidates) > 1:
            has_tie = True
            for item in top_candidates:
                item['is_tie'] = True
                winner_names.append(item['candidate'].name)
            names_str = " & ".join(winner_names)
            winner_text = f"Tie between {names_str} ({max_votes} votes each)"

    return {
        'election': election,
        'total_votes': total_votes,
        'total_eligible_voters': total_approved_students,
        'turnout_percentage': turnout_percentage,
        'results_data': results_data,
        'max_votes': max_votes,
        'has_tie': has_tie,
        'winner_names': winner_names,
        'winner_text': winner_text,
        'is_published': election.is_published,
    }
