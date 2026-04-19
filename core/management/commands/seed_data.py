"""
management/commands/seed_data.py
---------------------------------
Creates demo users and sample fields for testing.

Usage:
  python manage.py seed_data

Creates:
  - 1 Admin:       username=admin,      password=admin123
  - 2 Field Agents: username=agent1/2,  password=agent123
  - 6 sample fields in various stages and statuses
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from fields.models import Field, FieldUpdate


class Command(BaseCommand):
    help = 'Seeds the database with demo users and field data for testing.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding SmartSeason demo data...\n')

        # ── Users ─────────────────────────────────────────────────────────
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'role': User.Role.ADMIN,
            'first_name': 'Sam',
            'last_name': 'Coordinator',
            'email': 'admin@smartseason.demo',
            'is_staff': True,
        })
        admin.set_password('admin123')
        admin.save()
        self.stdout.write(f'  ✓ Admin:       username=admin, password=admin123')

        agent1, _ = User.objects.get_or_create(username='agent1', defaults={
            'role': User.Role.FIELD_AGENT,
            'first_name': 'James',
            'last_name': 'Mwangi',
            'email': 'james@smartseason.demo',
        })
        agent1.set_password('agent123')
        agent1.save()
        self.stdout.write(f'  ✓ Agent 1:     username=agent1, password=agent123')

        agent2, _ = User.objects.get_or_create(username='agent2', defaults={
            'role': User.Role.FIELD_AGENT,
            'first_name': 'Grace',
            'last_name': 'Atieno',
            'email': 'grace@smartseason.demo',
        })
        agent2.set_password('agent123')
        agent2.save()
        self.stdout.write(f'  ✓ Agent 2:     username=agent2, password=agent123\n')

        today = date.today()

        # ── Fields ────────────────────────────────────────────────────────
        fields_data = [
            {
                'name': 'North Block A',
                'crop_type': 'Maize',
                'planting_date': today - timedelta(days=45),
                'expected_harvest_date': today + timedelta(days=50),
                'current_stage': Field.Stage.GROWING,
                'location': 'Kiambu County',
                'assigned_to': agent1,
                'notes': 'Primary maize plot. Irrigated.',
            },
            {
                'name': 'South Terrace',
                'crop_type': 'Tomatoes',
                'planting_date': today - timedelta(days=30),
                'expected_harvest_date': today + timedelta(days=40),
                'current_stage': Field.Stage.GROWING,
                'location': 'Kiambu County',
                'assigned_to': agent1,
                'notes': 'Drip-irrigated tomato terrace.',
            },
            {
                'name': 'Hillside Plot B',
                'crop_type': 'Beans',
                'planting_date': today - timedelta(days=70),
                'expected_harvest_date': today - timedelta(days=5),  # overdue!
                'current_stage': Field.Stage.READY,
                'location': 'Nakuru County',
                'assigned_to': agent2,
                'notes': 'Beans are ready — needs urgent harvest.',
            },
            {
                'name': 'River Edge Field',
                'crop_type': 'Sorghum',
                'planting_date': today - timedelta(days=90),
                'expected_harvest_date': today - timedelta(days=10),
                'current_stage': Field.Stage.HARVESTED,
                'location': 'Nakuru County',
                'assigned_to': agent2,
                'notes': 'Season complete.',
            },
            {
                'name': 'Upper Paddock',
                'crop_type': 'Sunflower',
                'planting_date': today - timedelta(days=10),
                'expected_harvest_date': today + timedelta(days=80),
                'current_stage': Field.Stage.PLANTED,
                'location': 'Murang\'a County',
                'assigned_to': agent1,
            },
            {
                'name': 'Valley Floor C',
                'crop_type': 'Potatoes',
                'planting_date': today - timedelta(days=20),
                'expected_harvest_date': today + timedelta(days=70),
                'current_stage': Field.Stage.PLANTED,
                'location': 'Nyandarua County',
                'assigned_to': None,  # unassigned
                'notes': 'Not yet assigned to an agent.',
            },
        ]

        for data in fields_data:
            field, created = Field.objects.get_or_create(
                name=data['name'],
                defaults={
                    **data,
                    'created_by': admin,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Field: {field.name} ({field.crop_type})')

        # ── Field Updates (sample activity) ───────────────────────────────
        north_a = Field.objects.filter(name='North Block A').first()
        if north_a and not north_a.updates.exists():
            FieldUpdate.objects.create(
                field=north_a,
                logged_by=agent1,
                stage_at_update=Field.Stage.PLANTED,
                notes='Seeds planted in rows. Soil moisture good after last week\'s rain.',
            )
            FieldUpdate.objects.create(
                field=north_a,
                logged_by=agent1,
                stage_at_update=Field.Stage.GROWING,
                notes='Seedlings emerged well. Approx 85% germination rate. No pest issues noted.',
            )

        south = Field.objects.filter(name='South Terrace').first()
        if south and not south.updates.exists():
            FieldUpdate.objects.create(
                field=south,
                logged_by=agent1,
                stage_at_update=Field.Stage.PLANTED,
                notes='Seedlings transplanted from nursery. 200 plants in total.',
            )
            FieldUpdate.objects.create(
                field=south,
                logged_by=agent1,
                stage_at_update=Field.Stage.GROWING,
                notes='Plants flowering. Applied organic fertiliser. Some leaf curl noted on southern end.',
            )

        hillside = Field.objects.filter(name='Hillside Plot B').first()
        if hillside and not hillside.updates.exists():
            FieldUpdate.objects.create(
                field=hillside,
                logged_by=agent2,
                stage_at_update=Field.Stage.READY,
                notes='Pods fully formed and dry. Ready for harvest. Will schedule crew.',
            )

        river = Field.objects.filter(name='River Edge Field').first()
        if river and not river.updates.exists():
            FieldUpdate.objects.create(
                field=river,
                logged_by=agent2,
                stage_at_update=Field.Stage.HARVESTED,
                notes='Harvest complete. Yield: ~1.8 tonnes. Stored in main barn.',
            )

        self.stdout.write('\n✅ Demo data seeded successfully!\n')
        self.stdout.write('─' * 40)
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:   admin / admin123')
        self.stdout.write('  Agent 1: agent1 / agent123')
        self.stdout.write('  Agent 2: agent2 / agent123')
        self.stdout.write('─' * 40 + '\n')
