"""Make owner_id nullable for auth migration

Revision ID: 003
Revises: 002
Create Date: 2025-01-28 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    """Make owner_id nullable to support auth_owner_id transition."""
    # Make owner_id nullable since we're transitioning to auth_owner_id
    op.alter_column('teams', 'owner_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)

def downgrade():
    """Revert owner_id to not nullable."""
    # Note: This might fail if there are NULL values
    op.alter_column('teams', 'owner_id', 
                    existing_type=sa.INTEGER(),
                    nullable=False) 