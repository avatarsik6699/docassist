"""Doctor/patient profiles and seeded doctor account.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEFAULT_PASSWORD_HASH = "$2b$12$JUH0ENl95Y26jqTeiVPWi.PpsvrCT.ema92b.rd/.bXedDhfsi5mu"


def upgrade() -> None:
    op.create_table(
        "doctor_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "patient_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("doctor_user_id", sa.UUID(), nullable=False),
        sa.Column(
            "onboarding_status",
            sa.String(length=32),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active_with_doctor", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(
        "ix_patient_profiles_doctor_user_id",
        "patient_profiles",
        ["doctor_user_id"],
    )

    op.execute(
        sa.text(
            "INSERT INTO users (id, email, hashed_password, role, is_active) "
            "VALUES (gen_random_uuid(), :email, :pw, 'doctor', true) "
            "ON CONFLICT (email) DO UPDATE SET role = 'doctor', is_active = true"
        ).bindparams(
            email="doctor@example.com",
            pw=_DEFAULT_PASSWORD_HASH,
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO doctor_profiles (user_id) "
            "SELECT id FROM users WHERE email = :email "
            "ON CONFLICT (user_id) DO NOTHING"
        ).bindparams(email="doctor@example.com")
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM doctor_profiles WHERE user_id IN "
            "(SELECT id FROM users WHERE email = :email)"
        ).bindparams(email="doctor@example.com")
    )
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email").bindparams(email="doctor@example.com")
    )
    op.drop_index("ix_patient_profiles_doctor_user_id", table_name="patient_profiles")
    op.drop_table("patient_profiles")
    op.drop_table("doctor_profiles")
