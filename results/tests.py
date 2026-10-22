from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from elections.models import Election
from candidates.models import Candidate
from voting.models import Vote
from results.services import calculate_election_results


class ResultsSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        now = timezone.now()

        self.admin = CustomUser.objects.create_superuser(
            username='admin_res',
            email='admin_res@test.edu',
            password='AdminPassword123'
        )

        self.student = CustomUser.objects.create_user(
            username='stu_res',
            student_id='STU_RES',
            email='stu_res@test.edu',
            password='Password123',
            role='student',
            approval_status='approved'
        )

        self.election = Election.objects.create(
            title="Results Test Election",
            slug="results-test-election",
            description="Election for results testing",
            start_date=now - timedelta(days=2),
            end_date=now - timedelta(days=1),
            status='closed',
            is_published=False  # Initially unpublished
        )

        self.cand_a = Candidate.objects.create(
            election=self.election,
            name="Alice Walker",
            student_id="ALICE01",
            department="Computer Science & Engineering",
            position="President",
            manifesto="Platform A"
        )

        self.cand_b = Candidate.objects.create(
            election=self.election,
            name="Bob Smith",
            student_id="BOB01",
            department="Mechanical Engineering",
            position="President",
            manifesto="Platform B"
        )

    def test_unpublished_results_hidden_from_public(self):
        """Unpublished results should redirect public visitors and regular students."""
        # 1. Unauthenticated public visitor
        response = self.client.get(reverse('results:election_result', kwargs={'slug': self.election.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('results:results_list'))

        # 2. Logged in student
        self.client.login(username='stu_res', password='Password123')
        response2 = self.client.get(reverse('results:election_result', kwargs={'slug': self.election.slug}))
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, reverse('results:results_list'))

    def test_unpublished_results_accessible_to_admin(self):
        """Admin can preview unpublished results for verification."""
        self.client.login(username='admin_res', password='AdminPassword123')
        response = self.client.get(reverse('results:election_result', kwargs={'slug': self.election.slug}))
        self.assertEqual(response.status_code, 200)

    def test_published_results_accessible_to_everyone(self):
        """Once published, any visitor or student can view results."""
        self.election.is_published = True
        self.election.save()

        response = self.client.get(reverse('results:election_result', kwargs={'slug': self.election.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Results Test Election")

    def test_single_winner_calculation(self):
        """Test calculation of clear winner."""
        # 2 votes for Alice, 1 vote for Bob
        Vote.objects.create(election=self.election, candidate=self.cand_a)
        Vote.objects.create(election=self.election, candidate=self.cand_a)
        Vote.objects.create(election=self.election, candidate=self.cand_b)

        results = calculate_election_results(self.election)
        self.assertEqual(results['total_votes'], 3)
        self.assertFalse(results['has_tie'])
        self.assertEqual(results['winner_names'], ['Alice Walker'])
        self.assertIn("Winner: Alice Walker", results['winner_text'])

    def test_tie_outcome_calculation(self):
        """Test calculation when two candidates receive identical votes."""
        # 2 votes for Alice, 2 votes for Bob
        Vote.objects.create(election=self.election, candidate=self.cand_a)
        Vote.objects.create(election=self.election, candidate=self.cand_a)
        Vote.objects.create(election=self.election, candidate=self.cand_b)
        Vote.objects.create(election=self.election, candidate=self.cand_b)

        results = calculate_election_results(self.election)
        self.assertEqual(results['total_votes'], 4)
        self.assertTrue(results['has_tie'])
        self.assertIn('Alice Walker', results['winner_names'])
        self.assertIn('Bob Smith', results['winner_names'])
        self.assertIn("Tie between Alice Walker & Bob Smith (2 votes each)", results['winner_text'])
