from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from elections.models import Election
from elections.forms import ElectionForm


class ElectionModelAndFormTests(TestCase):
    def test_election_creation_and_slug(self):
        """Test slug is automatically generated from title."""
        now = timezone.now()
        el = Election.objects.create(
            title="Council Election 2026",
            description="Election for student council.",
            start_date=now,
            end_date=now + timedelta(days=2),
            status='active'
        )
        self.assertEqual(el.slug, 'council-election-2026')

    def test_is_currently_open_logic(self):
        """Test open/close detection across time windows."""
        now = timezone.now()

        # 1. Active window
        active_el = Election.objects.create(
            title="Active Poll",
            description="Active now",
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
            status='active'
        )
        self.assertTrue(active_el.is_currently_open)
        self.assertEqual(active_el.time_status, 'Active')

        # 2. Upcoming window
        upcoming_el = Election.objects.create(
            title="Future Poll",
            description="Starts tomorrow",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=2),
            status='active'
        )
        self.assertFalse(upcoming_el.is_currently_open)
        self.assertEqual(upcoming_el.time_status, 'Upcoming')

        # 3. Closed status
        closed_el = Election.objects.create(
            title="Manually Closed Poll",
            description="Closed by admin",
            start_date=now - timedelta(hours=2),
            end_date=now + timedelta(hours=2),
            status='closed'
        )
        self.assertFalse(closed_el.is_currently_open)
        self.assertEqual(closed_el.time_status, 'Closed')

    def test_election_form_end_date_validation(self):
        """Test that form raises validation error if end_date <= start_date."""
        now = timezone.now()
        data = {
            'title': 'Invalid Election Schedule',
            'description': 'Description',
            'start_date': now + timedelta(days=2),
            'end_date': now + timedelta(days=1),  # earlier than start
            'status': 'draft',
        }
        form = ElectionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Election end time must be later than the start time.", form.non_field_errors())
