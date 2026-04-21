"""Medication tracking and adherence logging.

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "medications",
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("doctor_user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("dosage_instructions", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["doctor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["patient_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medications_doctor_user_id", "medications", ["doctor_user_id"])
    op.create_index("ix_medications_patient_user_id", "medications", ["patient_user_id"])

    op.create_table(
        "adherence_logs",
        sa.Column("medication_id", sa.UUID(), nullable=False),
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("deviation_note", sa.Text(), nullable=True),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["medication_id"], ["medications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_adherence_logs_logged_at", "adherence_logs", ["logged_at"])
    op.create_index("ix_adherence_logs_medication_id", "adherence_logs", ["medication_id"])
    op.create_index("ix_adherence_logs_patient_user_id", "adherence_logs", ["patient_user_id"])


def downgrade() -> None:
    op.drop_index("ix_adherence_logs_patient_user_id", table_name="adherence_logs")
    op.drop_index("ix_adherence_logs_medication_id", table_name="adherence_logs")
    op.drop_index("ix_adherence_logs_logged_at", table_name="adherence_logs")
    op.drop_table("adherence_logs")

    op.drop_index("ix_medications_patient_user_id", table_name="medications")
    op.drop_index("ix_medications_doctor_user_id", table_name="medications")
    op.drop_table("medications")
