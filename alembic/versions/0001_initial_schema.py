"""Initial schema: users, appeals, appeal_messages, admins, settings, banned_users, statistics

Revision ID: 0001
Revises:
Create Date: 2026-01-12 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column(
            "language",
            sa.String(length=8),
            nullable=False,
            server_default="uz",
        ),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.String(length=16),
            nullable=False,
            server_default="admin",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("replies_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_admins_telegram_id", "admins", ["telegram_id"], unique=True)

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_unique_constraint("uq_settings_key", "settings", ["key"])

    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("new_appeals_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("answered_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("closed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_users_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_statistics_date", "statistics", ["date"], unique=True)

    op.execute("CREATE SEQUENCE IF NOT EXISTS appeal_number_seq START WITH 1 INCREMENT BY 1")

    op.create_table(
        "appeals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appeal_number",
            sa.Integer(),
            server_default=sa.text("nextval('appeal_number_seq')"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="new",
        ),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("group_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("group_message_id", sa.BigInteger(), nullable=True),
        sa.Column("closed_at", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_appeals_appeal_number", "appeals", ["appeal_number"], unique=True)
    op.create_index("ix_appeals_user_id", "appeals", ["user_id"])
    op.create_index("ix_appeals_status", "appeals", ["status"])
    op.create_index(
        "ix_appeals_group_message_id", "appeals", ["group_chat_id", "group_message_id"]
    )
    op.execute(
        "ALTER SEQUENCE appeal_number_seq OWNED BY appeals.appeal_number"
    )

    op.create_table(
        "appeal_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appeal_id",
            sa.Integer(),
            sa.ForeignKey("appeals.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(length=16), nullable=False),
        sa.Column("content_type", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("file_id", sa.String(length=512), nullable=True),
        sa.Column("file_unique_id", sa.String(length=255), nullable=True),
        sa.Column("media_group_id", sa.String(length=64), nullable=True),
        sa.Column("user_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("user_message_id", sa.BigInteger(), nullable=True),
        sa.Column("group_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("group_message_id", sa.BigInteger(), nullable=True),
        sa.Column("employee_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_appeal_messages_appeal_id", "appeal_messages", ["appeal_id"])
    op.create_index(
        "ix_appeal_messages_group_message",
        "appeal_messages",
        ["group_chat_id", "group_message_id"],
    )
    op.create_index(
        "ix_appeal_messages_user_message",
        "appeal_messages",
        ["user_chat_id", "user_message_id"],
    )

    op.create_table(
        "banned_users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=512), nullable=True),
        sa.Column("banned_by_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_banned_users_user_id", "banned_users", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_banned_users_user_id", table_name="banned_users")
    op.drop_table("banned_users")

    op.drop_index("ix_appeal_messages_user_message", table_name="appeal_messages")
    op.drop_index("ix_appeal_messages_group_message", table_name="appeal_messages")
    op.drop_index("ix_appeal_messages_appeal_id", table_name="appeal_messages")
    op.drop_table("appeal_messages")

    op.drop_index("ix_appeals_group_message_id", table_name="appeals")
    op.drop_index("ix_appeals_status", table_name="appeals")
    op.drop_index("ix_appeals_user_id", table_name="appeals")
    op.drop_index("ix_appeals_appeal_number", table_name="appeals")
    op.drop_table("appeals")
    op.execute("DROP SEQUENCE IF EXISTS appeal_number_seq")

    op.drop_index("ix_statistics_date", table_name="statistics")
    op.drop_table("statistics")

    op.drop_constraint("uq_settings_key", "settings", type_="unique")
    op.drop_table("settings")

    op.drop_index("ix_admins_telegram_id", table_name="admins")
    op.drop_table("admins")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
