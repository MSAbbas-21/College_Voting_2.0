from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from elections.models import Election
from candidates.models import Candidate
from voting.models import VoterParticipation, Vote


class VotingSystemIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        now = timezone.now()

        # Approved Student
        self.approved_student = CustomUser.objects.create_user(
            username='APP001',
            student_id='APP001',
            email='app001@test.edu',
            password='Password123',
            role='student',
            approval_status='approved'
        )

        # Pending Student
        self.pending_student = CustomUser.objects.create_user(
            username='PEN001',
            student_id='PEN001',
            email='pen001@test.edu',
            password='Password123',
            role='student',
            approval_status='pending'
        )

        # Active Election
        self.active_election = Election.objects.create(
            title="Open Campus Poll",
            slug="open-campus-poll",
            description="Active election description",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            status='active'
        )

        # Closed Election
        self.closed_election = Election.objects.create(
            title="Closed Campus Poll",
            slug="closed-campus-poll",
            description="Concluded election",
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=1),
            status='closed'
        )

        # Upcoming Election
        self.upcoming_election = Election.objects.create(
            title="Upcoming Campus Poll",
            slug="upcoming-campus-poll",
            description="Upcoming election",
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=5),
            status='active'
        )

        # Candidates
        self.cand1 = Candidate.objects.create(
            election=self.active_election,
            name="Candidate One",
            student_id="CAND001",
            department="Computer Science & Engineering",
            position="President",
            manifesto="Platform 1"
        )
        self.cand2 = Candidate.objects.create(
            election=self.active_election,
            name="Candidate Two",
            student_id="CAND002",
            department="Mechanical Engineering",
            position="President",
            manifesto="Platform 2"
        )

        # Candidate from another election
        self.cand_other = Candidate.objects.create(
            election=self.closed_election,
            name="Candidate Other",
            student_id="CAND003",
            department="Civil Engineering",
            position="President",
            manifesto="Platform Other"
        )

    def test_approved_student_successful_vote(self):
        """Test approved student can cast vote and receive confirmation receipt."""
        self.client.login(username='APP001', password='Password123')

        # 1. Access ballot
        ballot_res = self.client.get(reverse('voting:ballot', kwargs={'slug': self.active_election.slug}))
        self.assertEqual(ballot_res.status_code, 200)

        # 2. Confirm vote step
        confirm_res = self.client.post(
            reverse('voting:confirm_vote', kwargs={'slug': self.active_election.slug}),
            {'candidate_id': self.cand1.id}
        )
        self.assertEqual(confirm_res.status_code, 200)

        # 3. Submit vote
        submit_res = self.client.post(
            reverse('voting:submit_vote', kwargs={'slug': self.active_election.slug}),
            {'candidate_id': self.cand1.id}
        )
        self.assertEqual(submit_res.status_code, 302)

        # Verify VoterParticipation recorded
        self.assertTrue(VoterParticipation.objects.filter(
            student=self.approved_student,
            election=self.active_election
        ).exists())

        # Verify Vote recorded anonymously
        self.assertEqual(self.active_election.votes.count(), 1)
        self.assertEqual(self.cand1.votes.count(), 1)

    def test_pending_student_cannot_vote(self):
        """Test unapproved student is blocked from voting."""
        self.client.login(username='PEN001', password='Password123')

        response = self.client.get(reverse('voting:ballot', kwargs={'slug': self.active_election.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))

    def test_voting_in_closed_election_rejected(self):
        """Test attempting to vote in closed election is blocked."""
        self.client.login(username='APP001', password='Password123')

        response = self.client.get(reverse('voting:ballot', kwargs={'slug': self.closed_election.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))

    def test_voting_in_upcoming_election_rejected(self):
        """Test attempting to vote in upcoming election before start time is blocked."""
        self.client.login(username='APP001', password='Password123')

        response = self.client.get(reverse('voting:ballot', kwargs={'slug': self.upcoming_election.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))

    def test_duplicate_vote_rejected(self):
        """Test that student cannot cast more than one ballot in the same election."""
        self.client.login(username='APP001', password='Password123')

        # First vote
        self.client.post(
            reverse('voting:submit_vote', kwargs={'slug': self.active_election.slug}),
            {'candidate_id': self.cand1.id}
        )
        self.assertEqual(self.active_election.votes.count(), 1)

        # Second vote attempt for candidate 2
        dup_res = self.client.post(
            reverse('voting:submit_vote', kwargs={'slug': self.active_election.slug}),
            {'candidate_id': self.cand2.id}
        )
        self.assertEqual(dup_res.status_code, 302)
        # Total votes in election must still be 1!
        self.assertEqual(self.active_election.votes.count(), 1)
        self.assertEqual(self.cand2.votes.count(), 0)

    def test_invalid_candidate_rejected(self):
        """Test submitting candidate belonging to another election returns 404/error."""
        self.client.login(username='APP001', password='Password123')

        response = self.client.post(
            reverse('voting:submit_vote', kwargs={'slug': self.active_election.slug}),
            {'candidate_id': self.cand_other.id}  # candidate belongs to closed_election
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.active_election.votes.count(), 0)
