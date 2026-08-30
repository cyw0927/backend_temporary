"""add MVP vertical slice tables

Revision ID: 0002_mvp_vertical_slice
Revises: 0001_create_users
Create Date: 2026-08-30
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_mvp_vertical_slice"
down_revision: str | None = "0001_create_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learning_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=False),
        sa.Column("reference_solution", sa.Text(), nullable=False),
        sa.Column("reward_amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "shop_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("learning_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result_message", sa.Text(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_attempts_task_id", "attempts", ["task_id"])
    op.create_table(
        "reward_ledger",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("attempt_id", name="uq_reward_ledger_attempt"),
    )
    op.create_index("ix_reward_ledger_user_id", "reward_ledger", ["user_id"])
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("shop_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "item_id", name="uq_inventory_user_item"),
    )
    op.create_index("ix_inventory_items_user_id", "inventory_items", ["user_id"])
    op.create_index("ix_inventory_items_item_id", "inventory_items", ["item_id"])
    op.create_table(
        "housing_placements",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("shop_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot", sa.String(length=50), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "slot", name="uq_housing_user_slot"),
    )
    op.create_index("ix_housing_placements_user_id", "housing_placements", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_housing_placements_user_id", table_name="housing_placements")
    op.drop_table("housing_placements")
    op.drop_index("ix_inventory_items_item_id", table_name="inventory_items")
    op.drop_index("ix_inventory_items_user_id", table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_index("ix_reward_ledger_user_id", table_name="reward_ledger")
    op.drop_table("reward_ledger")
    op.drop_index("ix_attempts_task_id", table_name="attempts")
    op.drop_index("ix_attempts_user_id", table_name="attempts")
    op.drop_table("attempts")
    op.drop_table("shop_items")
    op.drop_table("learning_tasks")
