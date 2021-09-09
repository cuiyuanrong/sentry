# Generated by Django 2.2.23 on 2021-09-09 16:13

import django.utils.timezone
from django.db import migrations, models

import sentry.db.models.fields.bounded
import sentry.db.models.fields.jsonfield


def _make_deferrable(apps, schema_editor):
    """
    Change the unique constraint to be deferrable
    """
    # Get the db name of the constraint
    FrontendManifest = apps.get_model("sentry", "FrontendManifest")
    CONSTRAINT_NAME = schema_editor._constraint_names(
        FrontendManifest, ["is_production"], unique=True
    )[0]
    TABLE_NAME = FrontendManifest._meta.db_table

    # Drop then re-add with deferrable as ALTER doesnt seem to work for unique constraints in psql
    with schema_editor.connection.create_cursor() as curs:
        curs.execute(f'ALTER TABLE {TABLE_NAME} DROP CONSTRAINT "{CONSTRAINT_NAME}";')
        curs.execute(
            f"ALTER TABLE {TABLE_NAME} ADD CONSTRAINT"
            f" {CONSTRAINT_NAME}"
            f" UNIQUE (col1, col2) DEFERRABLE INITIALLY DEFERRED;"
        )


def _unmake_deferrable(apps, schema_editor):
    """
    Reverse the unique constraint to be not deferrable
    """
    # Get the db name of unique constraint
    FrontendManifest = apps.get_model("myapp", "FrontendManifest")
    CONSTRAINT_NAME = schema_editor._constraint_names(
        FrontendManifest, ["is_production"], unique=True
    )[0]
    TABLE_NAME = FrontendManifest._meta.db_table

    with schema_editor.connection.create_cursor() as curs:
        curs.execute(f'ALTER TABLE {TABLE_NAME} DROP CONSTRAINT "{CONSTRAINT_NAME}";')
        curs.execute(
            f"ALTER TABLE {TABLE_NAME} ADD CONSTRAINT"
            f" {CONSTRAINT_NAME}"
            f" UNIQUE (col1, col2) NOT DEFERRABLE;"
        )


class Migration(migrations.Migration):
    # This flag is used to mark that a migration shouldn't be automatically run in
    # production. We set this to True for operations that we think are risky and want
    # someone from ops to run manually and monitor.
    # General advice is that if in doubt, mark your migration as `is_dangerous`.
    # Some things you should always mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that
    #   they can be monitored. Since data migrations will now hold a transaction open
    #   this is even more important.
    # - Adding columns to highly active tables, even ones that are NULL.
    is_dangerous = False

    # This flag is used to decide whether to run this migration in a transaction or not.
    # By default we prefer to run in a transaction, but for migrations where you want
    # to `CREATE INDEX CONCURRENTLY` this needs to be set to False. Typically you'll
    # want to create an index concurrently when adding one to an existing table.
    # You'll also usually want to set this to `False` if you're writing a data
    # migration, since we don't want the entire migration to run in one long-running
    # transaction.
    atomic = True

    dependencies = [
        ("sentry", "0228_update_auditlog_index_with_entry"),
    ]

    operations = [
        migrations.CreateModel(
            name="FrontendManifest",
            fields=[
                (
                    "id",
                    sentry.db.models.fields.bounded.BoundedBigAutoField(
                        primary_key=True, serialize=False
                    ),
                ),
                ("version", models.CharField(db_index=True, max_length=128)),
                ("date_created", models.DateTimeField(default=django.utils.timezone.now)),
                ("manifest", sentry.db.models.fields.jsonfield.JSONField(default=dict)),
                ("is_production", models.BooleanField(db_index=True, default=False, null=True)),
            ],
            options={
                "db_table": "sentry_frontendmanifest",
            },
        ),
        migrations.AddConstraint(
            model_name="frontendmanifest",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_production=True),
                fields=("is_production",),
                name="unique_production_index",
            ),
        ),
        migrations.RunPython(code=_make_deferrable, reverse_code=_unmake_deferrable),
    ]
