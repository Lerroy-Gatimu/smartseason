"""
accounts/models.py
------------------
We extend Django's built-in User model to add a "role" field.
This is the cleanest approach — one table, all auth features included.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user with two roles:
      - ADMIN      → can see all fields, all agents, full dashboard
      - FIELD_AGENT → can only see and update their assigned fields
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin (Coordinator)'
        FIELD_AGENT = 'field_agent', 'Field Agent'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FIELD_AGENT,
        help_text="Controls what this user can see and do."
    )

    # ── Convenience properties ─────────────────────────────────────────────

    @property
    def is_admin_role(self):
        """True if this user is an Admin/Coordinator."""
        return self.role == self.Role.ADMIN

    @property
    def is_field_agent(self):
        """True if this user is a Field Agent."""
        return self.role == self.Role.FIELD_AGENT

    @property
    def display_role(self):
        return self.get_role_display()

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.display_role})"
