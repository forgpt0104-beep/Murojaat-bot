"""Repository for Admin model."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select

from bot.database.models.admin import Admin
from bot.database.models.enums import AdminRole
from bot.database.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    model = Admin

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Admin]:
        result = await self.session.execute(
            select(Admin).where(Admin.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> Sequence[Admin]:
        result = await self.session.execute(
            select(Admin).where(Admin.is_active.is_(True))
        )
        return result.scalars().all()

    async def add_admin(
        self,
        telegram_id: int,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
        role: AdminRole = AdminRole.ADMIN,
    ) -> Admin:
        """Create an Admin row if missing. Never downgrades an existing role."""
        existing = await self.get_by_telegram_id(telegram_id)
        if existing is not None:
            existing.is_active = True
            if full_name is not None:
                existing.full_name = full_name
            if username is not None:
                existing.username = username
            await self.session.flush()
            return existing
        return await self.create(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            role=role,
            is_active=True,
        )

    async def deactivate(self, admin: Admin) -> Admin:
        admin.is_active = False
        await self.session.flush()
        return admin

    async def demote_stale_super_admins(self, current_telegram_id: int) -> Sequence[Admin]:
        """Deactivate any super_admin row that no longer matches the configured
        SUPER_ADMIN_ID, so rotating that env var actually transfers access
        instead of leaving the previous super admin permanently active.
        """
        result = await self.session.execute(
            select(Admin).where(
                Admin.role == AdminRole.SUPER_ADMIN,
                Admin.telegram_id != current_telegram_id,
                Admin.is_active.is_(True),
            )
        )
        stale = result.scalars().all()
        for admin in stale:
            admin.is_active = False
        if stale:
            await self.session.flush()
        return stale

    async def increment_replies_count(
        self,
        telegram_id: int,
        full_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        """Increment the reply counter, auto-registering the employee if needed.

        Staff are authorized purely by being members of the group, so their first
        reply is what creates their Admin/employee tracking row.
        """
        admin = await self.add_admin(
            telegram_id, full_name=full_name, username=username, role=AdminRole.EMPLOYEE
        )
        admin.replies_count += 1
        await self.session.flush()

    async def top_employees(self, limit: int = 10) -> Sequence[Admin]:
        result = await self.session.execute(
            select(Admin)
            .where(Admin.replies_count > 0)
            .order_by(Admin.replies_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
