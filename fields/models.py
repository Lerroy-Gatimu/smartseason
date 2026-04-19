"""
fields/models.py
----------------
Core data models for the SmartSeason system.

Two models:
  Field       — represents one farm field with crop info
  FieldUpdate — an observation/stage update logged by a field agent
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta

from accounts.models import User


class Field(models.Model):
    """
    Represents a single crop field being monitored during a growing season.
    """

    # ── Stage choices (lifecycle of the crop) ─────────────────────────────
    class Stage(models.TextChoices):
        PLANTED   = 'planted',   'Planted'
        GROWING   = 'growing',   'Growing'
        READY     = 'ready',     'Ready to Harvest'
        HARVESTED = 'harvested', 'Harvested'

    # ── Status choices (computed from field data — see compute_status()) ──
    class Status(models.TextChoices):
        ACTIVE    = 'active',    'Active'
        AT_RISK   = 'at_risk',   'At Risk'
        COMPLETED = 'completed', 'Completed'

    # ── Core fields ───────────────────────────────────────────────────────

    name = models.CharField(max_length=200, help_text="Field name or plot identifier")
    crop_type = models.CharField(max_length=100, help_text="Type of crop, e.g. Maize, Tomatoes")
    planting_date = models.DateField(help_text="Date the crop was planted")
    location = models.CharField(max_length=200, blank=True, help_text="Optional: county/ward/coordinates")

    current_stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.PLANTED,
    )

    # ── Assignment ────────────────────────────────────────────────────────
    # Each field is assigned to one field agent.
    # SET_NULL means if the agent is deleted, field is not deleted.
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_fields',
        limit_choices_to={'role': 'field_agent'},
        help_text="The field agent responsible for this field",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_fields',
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # ── Expected harvest ─────────────────────────────────────────────────
    expected_harvest_date = models.DateField(
        null=True, blank=True,
        help_text="When is this field expected to be ready for harvest?"
    )

    # ── Notes ─────────────────────────────────────────────────────────────
    notes = models.TextField(blank=True, help_text="Admin-level notes about this field")

    # ─────────────────────────────────────────────────────────────────────
    # STATUS LOGIC
    # ─────────────────────────────────────────────────────────────────────
    # Status is NOT stored in the database — it's computed fresh each time
    # from the field's current data. This avoids stale data.
    #
    # Rules:
    #   COMPLETED → stage is 'harvested'
    #
    #   AT RISK   → any of:
    #     - Stage is 'planted' or 'growing' AND no update in the last 7 days
    #     - Past the expected harvest date and NOT yet harvested
    #
    #   ACTIVE    → everything else (being monitored, within schedule)
    # ─────────────────────────────────────────────────────────────────────

    @property
    def status(self):
        return self.compute_status()

    def compute_status(self):
        today = timezone.now().date()

        # Rule 1: If harvested → Completed
        if self.current_stage == self.Stage.HARVESTED:
            return self.Status.COMPLETED

        # Rule 2: Overdue harvest
        if self.expected_harvest_date and today > self.expected_harvest_date:
            return self.Status.AT_RISK

        # Rule 3: No update in the last 7 days (stale monitoring)
        last_update = self.updates.order_by('-created_at').first()
        if last_update:
            days_since_update = (timezone.now() - last_update.created_at).days
            if days_since_update > 7:
                return self.Status.AT_RISK
        else:
            # Never updated + planted more than 7 days ago
            days_since_planted = (today - self.planting_date).days
            if days_since_planted > 7:
                return self.Status.AT_RISK

        return self.Status.ACTIVE

    @property
    def status_label(self):
        return self.Status(self.status).label

    @property
    def days_since_planted(self):
        return (timezone.now().date() - self.planting_date).days

    @property
    def is_overdue(self):
        if self.expected_harvest_date:
            return timezone.now().date() > self.expected_harvest_date
        return False

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.crop_type}) — {self.get_current_stage_display()}"


class FieldUpdate(models.Model):
    """
    A single observation or stage update logged by a field agent.
    Acts as an audit trail of everything that happens to a field.
    """
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='updates',
    )
    logged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='field_updates',
    )

    # The stage at the time of this update (may change over time)
    stage_at_update = models.CharField(
        max_length=20,
        choices=Field.Stage.choices,
    )

    notes = models.TextField(help_text="Observations, issues, measurements, etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update on {self.field.name} by {self.logged_by} at {self.created_at:%Y-%m-%d %H:%M}"
