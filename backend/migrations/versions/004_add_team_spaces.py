"""Add team spaces table and space_id columns

Revision ID: 004_add_team_spaces
Revises: 003_make_owner_id_nullable
Create Date: 2024-08-02 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_team_spaces'
down_revision = '003_make_owner_id_nullable'
branch_labels = None
depends_on = None


def upgrade():
    # Create team_spaces table
    op.create_table('team_spaces',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id')
    )
    
    # Add space_id column to teams table
    op.add_column('teams', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'teams', 'team_spaces', ['space_id'], ['id'])
    
    # Add space_id column to roles table
    op.add_column('roles', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'roles', 'team_spaces', ['space_id'], ['id'])
    
    # Add space_id column to team_executions table
    op.add_column('team_executions', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'team_executions', 'team_spaces', ['space_id'], ['id'])
    
    # Add space_id column to task_executions table
    op.add_column('task_executions', sa.Column('space_id', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'task_executions', 'team_spaces', ['space_id'], ['id'])


def downgrade():
    # Remove foreign key constraints
    op.drop_constraint(None, 'task_executions', type_='foreignkey')
    op.drop_constraint(None, 'team_executions', type_='foreignkey')
    op.drop_constraint(None, 'roles', type_='foreignkey')
    op.drop_constraint(None, 'teams', type_='foreignkey')
    
    # Remove space_id columns
    op.drop_column('task_executions', 'space_id')
    op.drop_column('team_executions', 'space_id')
    op.drop_column('roles', 'space_id')
    op.drop_column('teams', 'space_id')
    
    # Drop team_spaces table
    op.drop_table('team_spaces') 