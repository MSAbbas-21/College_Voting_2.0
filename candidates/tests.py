from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from elections.models import Election
from candidates.models import Candidate


class CandidateModelTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.election = Election.objects.create(
            title="Presidential Poll",
            description="Election",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            status='active'
        )

    def test_candidate_creation_and_string_representation(self):
        """Test candidate model representation."""
        cand = Candidate.objects.create(
            election=self.election,
            name="Alex Morgan",
            student_id="CS2023999",
            department="Computer Science & Engineering",
            position="President",
            manifesto="Better campus wifi."
        )
        self.assertEqual(str(cand), "Alex Morgan - President (Presidential Poll)")

    def test_duplicate_candidate_in_same_election_rejected(self):
        """Test unique constraint on (election, student_id)."""
        Candidate.objects.create(
            election=self.election,
            name="Alex Morgan",
            student_id="CS2023999",
            department="Computer Science & Engineering",
            position="President",
            manifesto="Platform 1"
        )
        with self.assertRaises(IntegrityError):
            Candidate.objects.create(
                election=self.election,
                name="Alex Duplicate",
                student_id="CS2023999",
                department="Computer Science & Engineering",
                position="President",
                manifesto="Platform 2"
            )
