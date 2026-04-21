"""Questionnaire assignments and responses.

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "questionnaire_assignments",
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("doctor_user_id", sa.UUID(), nullable=False),
        sa.Column("questionnaire_code", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="assigned"),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index(
        "ix_questionnaire_assignments_patient_user_id",
        "questionnaire_assignments",
        ["patient_user_id"],
    )
    op.create_index(
        "ix_questionnaire_assignments_doctor_user_id",
        "questionnaire_assignments",
        ["doctor_user_id"],
    )

    op.create_table(
        "questionnaire_responses",
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("questionnaire_code", sa.String(length=16), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("has_safety_signal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "submitted_at",
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
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["questionnaire_assignments.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["patient_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assignment_id"),
    )
    op.create_index(
        "ix_questionnaire_responses_assignment_id",
        "questionnaire_responses",
        ["assignment_id"],
    )
    op.create_index(
        "ix_questionnaire_responses_patient_user_id",
        "questionnaire_responses",
        ["patient_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_questionnaire_responses_patient_user_id",
        table_name="questionnaire_responses",
    )
    op.drop_index("ix_questionnaire_responses_assignment_id", table_name="questionnaire_responses")
    op.drop_table("questionnaire_responses")

    op.drop_index(
        "ix_questionnaire_assignments_doctor_user_id",
        table_name="questionnaire_assignments",
    )
    op.drop_index(
        "ix_questionnaire_assignments_patient_user_id",
        table_name="questionnaire_assignments",
    )
    op.drop_table("questionnaire_assignments")
