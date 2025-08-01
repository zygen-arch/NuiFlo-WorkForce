"""Add team spaces table and space_id columns

Revision ID: 004_add_team_spaces
Revises: 003_make_owner_id_nullable
Create Date: 2025-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_team_spaces'
down_revision = '003_make_owner_id_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create team_spaces table
    op.create_table('team_spaces',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id')
    )
    
    # Add indexes for performance
    op.create_index(op.f('ix_team_spaces_team_id'), 'team_spaces', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_spaces_created_at'), 'team_spaces', ['created_at'], unique=False)
    
    # Add space_id columns to existing tables (nullable first for migration)
    op.add_column('teams', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.add_column('roles', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.add_column('team_executions', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.add_column('task_executions', sa.Column('space_id', sa.String(length=50), nullable=True))
    
    # Add indexes for space_id columns
    op.create_index(op.f('ix_teams_space_id'), 'teams', ['space_id'], unique=False)
    op.create_index(op.f('ix_roles_space_id'), 'roles', ['space_id'], unique=False)
    op.create_index(op.f('ix_team_executions_space_id'), 'team_executions', ['space_id'], unique=False)
    op.create_index(op.f('ix_task_executions_space_id'), 'task_executions', ['space_id'], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index(op.f('ix_task_executions_space_id'), table_name='task_executions')
    op.drop_index(op.f('ix_team_executions_space_id'), table_name='team_executions')
    op.drop_index(op.f('ix_roles_space_id'), table_name='roles')
    op.drop_index(op.f('ix_teams_space_id'), table_name='teams')
    
    # Remove space_id columns
    op.drop_column('task_executions', 'space_id')
    op.drop_column('team_executions', 'space_id')
    op.drop_column('roles', 'space_id')
    op.drop_column('teams', 'space_id')
    
    # Remove team_spaces table indexes
    op.drop_index(op.f('ix_team_spaces_created_at'), table_name='team_spaces')
    op.drop_index(op.f('ix_team_spaces_team_id'), table_name='team_spaces')
    
    # Remove team_spaces table
    op.drop_table('team_spaces') 