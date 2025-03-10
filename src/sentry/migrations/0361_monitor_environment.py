# Generated by Django 2.2.28 on 2023-02-24 00:38

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import sentry.db.models.fields.bounded
import sentry.db.models.fields.foreignkey
from sentry.new_migrations.migrations import CheckedMigration


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production. For
    # the most part, this should only be used for operations where it's safe to run the migration
    # after your code has deployed. So this should not be used for most operations that alter the
    # schema of a table.
    # Here are some things that make sense to mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that they can
    #   be monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   have ops run this and not block the deploy. Note that while adding an index is a schema
    #   change, it's completely safe to run the operation after the code has deployed.
    is_dangerous = False

    dependencies = [
        ("sentry", "0360_authenticator_config_type_change"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonitorEnvironment",
            fields=[
                (
                    "id",
                    sentry.db.models.fields.bounded.BoundedBigAutoField(
                        primary_key=True, serialize=False
                    ),
                ),
                ("status", sentry.db.models.fields.bounded.BoundedPositiveIntegerField(default=0)),
                ("next_checkin", models.DateTimeField(null=True)),
                ("last_checkin", models.DateTimeField(null=True)),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "environment",
                    sentry.db.models.fields.foreignkey.FlexibleForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sentry.Environment",
                        db_constraint=False,
                    ),
                ),
                (
                    "monitor",
                    sentry.db.models.fields.foreignkey.FlexibleForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="sentry.Monitor"
                    ),
                ),
            ],
            options={
                "db_table": "sentry_monitorenvironment",
            },
        ),
        migrations.AddIndex(
            model_name="monitorenvironment",
            index=models.Index(
                fields=["monitor", "environment"], name="sentry_moni_monitor_3d7eb9_idx"
            ),
        ),
    ]
