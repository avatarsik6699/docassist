"""Side effect reports and patient summary support.

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "side_effect_reports",
        sa.Column("patient_user_id", sa.UUID(), nullable=False),
        sa.Column("doctor_user_id", sa.UUID(), nullable=False),
        sa.Column("medication_id", sa.UUID(), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("symptom", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "reported_at",
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
        sa.ForeignKeyConstraint(["doctor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["medication_id"], ["medications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["patient_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_side_effect_reports_patient_user_id",
        "side_effect_reports",
        ["patient_user_id"],
    )
    op.create_index(
        "ix_side_effect_reports_doctor_user_id",
        "side_effect_reports",
        ["doctor_user_id"],
    )
    op.create_index("ix_side_effect_reports_medication_id", "side_effect_reports", ["medication_id"])
    op.create_index("ix_side_effect_reports_reported_at", "side_effect_reports", ["reported_at"])


def downgrade() -> None:
    op.drop_index("ix_side_effect_reports_reported_at", table_name="side_effect_reports")
    op.drop_index("ix_side_effect_reports_medication_id", table_name="side_effect_reports")
    op.drop_index("ix_side_effect_reports_doctor_user_id", table_name="side_effect_reports")
    op.drop_index("ix_side_effect_reports_patient_user_id", table_name="side_effect_reports")
    op.drop_table("side_effect_reports")
