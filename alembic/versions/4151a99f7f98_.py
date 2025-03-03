"""empty message.

Revision ID: 4151a99f7f98
Revises: d2ec60b816de
Create Date: 2025-03-03 21:39:11.437357

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4151a99f7f98"
down_revision: str | None = "d2ec60b816de"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table("images",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("image", sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("images")
    # ### end Alembic commands ###
