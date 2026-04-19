"""
fields/views.py
---------------
All views for the SmartSeason field monitoring system.

Access control summary:
  - All views require login (@login_required)
  - Admin views additionally check request.user.is_admin_role
  - Field agents only see their assigned fields
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Q

from .models import Field, FieldUpdate
from .forms import FieldForm, FieldUpdateForm
from accounts.models import User


# ── Helpers ────────────────────────────────────────────────────────────────────

def admin_required(view_func):
    """
    Decorator that wraps @login_required and also checks for admin role.
    Returns 403 Forbidden if the user is not an admin.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_role:
            return HttpResponseForbidden(
                "You don't have permission to access this page. "
                "Contact your coordinator."
            )
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _get_status_counts(fields):
    """
    Helper: given a queryset of fields, compute status counts.
    Because status is a computed property (not a DB column),
    we loop through in Python rather than using SQL aggregation.
    """
    counts = {'active': 0, 'at_risk': 0, 'completed': 0}
    for f in fields:
        counts[f.status] += 1
    return counts


# ── Dashboard ──────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Main landing page after login.
    Admins see all fields + agent overview.
    Field agents see only their assigned fields.
    """
    user = request.user

    if user.is_admin_role:
        # Admin: all fields
        fields = Field.objects.select_related('assigned_to').prefetch_related('updates').all()

        # Recent activity: last 10 updates across all fields
        recent_updates = (
            FieldUpdate.objects
            .select_related('field', 'logged_by')
            .order_by('-created_at')[:10]
        )

        # Agent overview: each agent + their field counts
        agents = (
            User.objects
            .filter(role=User.Role.FIELD_AGENT, is_active=True)
            .prefetch_related('assigned_fields')
        )

        status_counts = _get_status_counts(fields)

        context = {
            'fields': fields,
            'recent_updates': recent_updates,
            'agents': agents,
            'status_counts': status_counts,
            'total_fields': fields.count(),
        }
        return render(request, 'fields/admin_dashboard.html', context)

    else:
        # Field Agent: only assigned fields
        fields = (
            Field.objects
            .filter(assigned_to=user)
            .prefetch_related('updates')
        )

        # Their recent activity
        recent_updates = (
            FieldUpdate.objects
            .filter(field__assigned_to=user)
            .select_related('field', 'logged_by')
            .order_by('-created_at')[:5]
        )

        status_counts = _get_status_counts(fields)

        context = {
            'fields': fields,
            'recent_updates': recent_updates,
            'status_counts': status_counts,
            'total_fields': fields.count(),
        }
        return render(request, 'fields/agent_dashboard.html', context)


# ── Field List (Admin) ─────────────────────────────────────────────────────────

@admin_required
def field_list(request):
    """Admin: see all fields with optional filtering."""
    fields = Field.objects.select_related('assigned_to').prefetch_related('updates').all()

    # Simple filters
    stage_filter = request.GET.get('stage', '')
    agent_filter = request.GET.get('agent', '')
    search = request.GET.get('q', '').strip()

    if stage_filter:
        fields = fields.filter(current_stage=stage_filter)
    if agent_filter:
        fields = fields.filter(assigned_to__id=agent_filter)
    if search:
        fields = fields.filter(
            Q(name__icontains=search) | Q(crop_type__icontains=search)
        )

    agents = User.objects.filter(role=User.Role.FIELD_AGENT, is_active=True)

    context = {
        'fields': fields,
        'agents': agents,
        'stage_choices': Field.Stage.choices,
        'current_stage_filter': stage_filter,
        'current_agent_filter': agent_filter,
        'search_query': search,
    }
    return render(request, 'fields/field_list.html', context)


# ── Field Detail ───────────────────────────────────────────────────────────────

@login_required
def field_detail(request, pk):
    """
    View a single field's full details and update history.
    Admins can view any field.
    Agents can only view their assigned fields.
    """
    field = get_object_or_404(Field.objects.prefetch_related('updates__logged_by'), pk=pk)

    # Access control: agents only see their own fields
    if request.user.is_field_agent and field.assigned_to != request.user:
        return HttpResponseForbidden("This field is not assigned to you.")

    updates = field.updates.all()  # ordered by -created_at (see model Meta)

    context = {
        'field': field,
        'updates': updates,
    }
    return render(request, 'fields/field_detail.html', context)


# ── Create Field (Admin) ───────────────────────────────────────────────────────

@admin_required
def field_create(request):
    """Admin: create a new field."""
    form = FieldForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            field = form.save(commit=False)
            field.created_by = request.user
            field.save()
            messages.success(request, f"Field '{field.name}' created successfully.")
            return redirect('field_detail', pk=field.pk)
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'fields/field_form.html', {
        'form': form,
        'form_title': 'Add New Field',
        'submit_label': 'Create Field',
    })


# ── Edit Field (Admin) ─────────────────────────────────────────────────────────

@admin_required
def field_edit(request, pk):
    """Admin: edit an existing field."""
    field = get_object_or_404(Field, pk=pk)
    form = FieldForm(request.POST or None, instance=field)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"Field '{field.name}' updated.")
            return redirect('field_detail', pk=field.pk)
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'fields/field_form.html', {
        'form': form,
        'field': field,
        'form_title': f'Edit Field — {field.name}',
        'submit_label': 'Save Changes',
    })


# ── Delete Field (Admin) ───────────────────────────────────────────────────────

@admin_required
def field_delete(request, pk):
    """Admin: confirm and delete a field."""
    field = get_object_or_404(Field, pk=pk)

    if request.method == 'POST':
        name = field.name
        field.delete()
        messages.success(request, f"Field '{name}' has been deleted.")
        return redirect('field_list')

    return render(request, 'fields/field_confirm_delete.html', {'field': field})


# ── Log Update (Field Agent) ───────────────────────────────────────────────────

@login_required
def log_update(request, pk):
    """
    Field Agent (or Admin) logs a new observation/update on a field.
    Also updates the field's current_stage to match.
    """
    field = get_object_or_404(Field, pk=pk)

    # Agents can only update their assigned fields
    if request.user.is_field_agent and field.assigned_to != request.user:
        return HttpResponseForbidden("This field is not assigned to you.")

    form = FieldUpdateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            update = form.save(commit=False)
            update.field = field
            update.logged_by = request.user
            update.save()

            # Keep the field's current_stage in sync with the latest update
            field.current_stage = update.stage_at_update
            field.save(update_fields=['current_stage', 'updated_at'])

            messages.success(request, 'Update logged successfully.')
            return redirect('field_detail', pk=field.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'fields/log_update.html', {
        'form': form,
        'field': field,
    })
