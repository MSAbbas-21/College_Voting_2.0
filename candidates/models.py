from django.db import models
from elections.models import Election


class Candidate(models.Model):
    """
    Candidate running for a position within a specific Election.
    """
    POSITION_CHOICES = (
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('General Secretary', 'General Secretary'),
        ('Joint Secretary', 'Joint Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Cultural Secretary', 'Cultural Secretary'),
        ('Sports Secretary', 'Sports Secretary'),
        ('Technical Secretary', 'Technical Secretary'),
        ('Department Representative', 'Department Representative'),
    )

    DEPARTMENT_CHOICES = (
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Management Studies (MBA)', 'Management Studies (MBA)'),
        ('Applied Sciences', 'Applied Sciences'),
    )

    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='candidates',
        verbose_name="Election"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Candidate Full Name"
    )
    student_id = models.CharField(
        max_length=50,
        verbose_name="Student ID / Roll No"
    )
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        default='Computer Science & Engineering',
        verbose_name="Department"
    )
    position = models.CharField(
        max_length=100,
        choices=POSITION_CHOICES,
        default='President',
        verbose_name="Position / Post"
    )
    manifesto = models.TextField(
        verbose_name="Candidate Manifesto / Vision",
        help_text="Key priorities, plans, and statements for student voters."
    )
    photo = models.ImageField(
        upload_to='candidates/',
        blank=True,
        null=True,
        verbose_name="Profile Photo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'name']
        unique_together = ('election', 'student_id')
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        return f"{self.name} - {self.position} ({self.election.title})"

    def vote_count(self):
        """Count of votes received in its election."""
        return self.votes.count()

    def vote_percentage(self):
        """Calculates percentage of total votes cast in the election."""
        total = self.election.votes.count()
        if total == 0:
            return 0.0
        return round((self.vote_count() / total) * 100, 1)
