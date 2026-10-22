from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


class Election(models.Model):
    """
    Represents a student council or department election.
    Administrators control schedule, open/close state, and publishing of results.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft (Not Visible)'),
        ('active', 'Active (Scheduled / Open)'),
        ('closed', 'Closed (Voting Concluded)'),
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Election Title",
        help_text="e.g. Student Council Presidential Election 2026"
    )
    slug = models.SlugField(
        max_length=230,
        unique=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="Election Description & Rules",
        help_text="Provide context, guidelines, and voting rules for voters."
    )
    start_date = models.DateTimeField(
        verbose_name="Voting Start Time",
        help_text="When students can begin casting ballots."
    )
    end_date = models.DateTimeField(
        verbose_name="Voting End Time",
        help_text="When voting automatically closes."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Operational Status"
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Publish Election Results",
        help_text="Check to reveal candidate votes and winners to students and visitors."
    )
    banner_image = models.ImageField(
        upload_to='elections/',
        blank=True,
        null=True,
        verbose_name="Election Banner Image"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='elections_created',
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = "Election"
        verbose_name_plural = "Elections"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "election"
            slug = base_slug
            counter = 1
            while Election.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_currently_open(self):
        """
        True only if status is active AND current time falls between start_date and end_date.
        """
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date

    @property
    def time_status(self):
        """Returns human-readable time status."""
        now = timezone.now()
        if self.status == 'closed':
            return 'Closed'
        if self.status == 'draft':
            return 'Draft'
        if now < self.start_date:
            return 'Upcoming'
        elif self.start_date <= now <= self.end_date:
            return 'Active'
        else:
            return 'Ended'

    @property
    def status_badge_class(self):
        """Bootstrap badge class for display."""
        ts = self.time_status
        if ts == 'Active':
            return 'badge bg-success'
        elif ts == 'Upcoming':
            return 'badge bg-primary'
        elif ts == 'Draft':
            return 'badge bg-secondary'
        else:
            return 'badge bg-dark'

    def total_votes_count(self):
        return self.votes.count()

    def total_voters_count(self):
        return self.participating_voters.count()

    def candidate_count(self):
        return self.candidates.count()
