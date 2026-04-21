from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    onboarding_status: Literal["pending", "completed"] | None = None
    must_change_password: bool | None = None
    doctor_user_id: UUID | None = None
