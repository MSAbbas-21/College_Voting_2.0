import uuid
from django.db import models
from django.conf import settings
from elections.models import Election
from candidates.models import Candidate


class VoterParticipation(models.Model):
    """
    Tracks THAT a student has cast a ballot in an election,
    enforcing one vote per election without recording which candidate they chose.
    Generates an anonymous receipt code for verification.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='election_participations',
        verbose_name="Voter Student"
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='participating_voters',
        verbose_name="Election"
    )
    receipt_code = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Ballot Receipt Code",
        help_text="Verification token returned to student after voting."
    )
    voted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Time Cast"
    )

    class Meta:
        # Strict database constraint to prevent duplicate voting
        unique_together = ('student', 'election')
        ordering = ['-voted_at']
        verbose_name = "Voter Participation Record"
        verbose_name_plural = "Voter Participation Records"

    def __str__(self):
        return f"{self.student.username} participated in {self.election.title}"

    @classmethod
    def generate_receipt(cls):
        """Generates a secure, human-readable voting receipt token."""
        return f"VOTE-{uuid.uuid4().hex[:10].upper()}"


class Vote(models.Model):
    """
    Secret ballot record.
    Stores the candidate chosen for a specific election.
    Notice: No foreign key to student/user exists here, ensuring separation
    between voter identity and ballot selection.
    """
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Election"
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name="Candidate"
    )
    cast_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )

    class Meta:
        ordering = ['-cast_at']
        verbose_name = "Secret Ballot Vote"
        verbose_name_plural = "Secret Ballot Votes"

    def __str__(self):
        return f"Ballot for {self.candidate.name} in {self.election.title}"
