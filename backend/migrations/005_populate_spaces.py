"""Populate spaces for existing teams

Revision ID: 005_populate_spaces
Revises: 004_add_team_spaces
Create Date: 2025-01-28 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '005_populate_spaces'
down_revision = '004_add_team_spaces'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection
    connection = op.get_bind()
    
    # Create spaces for existing teams
    teams_result = connection.execute(sa.text("SELECT id, name FROM teams"))
    teams = teams_result.fetchall()
    
    for team in teams:
        team_id = team[0]
        team_name = team[1]
        
        # Create space for this team
        space_id = f"space_{uuid.uuid4()}"
        space_name = f"{team_name} Space"
        
        # Default settings
        settings = {
            "storage": {
                "type": "local",
                "size_gb": 10,
                "external_providers": []
            },
            "quotas": {
                "monthly_budget": 500.0,
                "execution_limit": 1000,
                "agent_limit": 10
            },
            "permissions": {
                "default_agent_access": ["read", "write"],
                "allow_external_storage": True,
                "allow_cross_space_references": False
            }
        }
        
        # Insert space
        connection.execute(
            sa.text("""
                INSERT INTO team_spaces (id, team_id, name, settings, storage_config, created_at, updated_at)
                VALUES (:space_id, :team_id, :name, :settings, '{}', :created_at, :updated_at)
            """),
            {
                "space_id": space_id,
                "team_id": team_id,
                "name": space_name,
                "settings": settings,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        
        # Update team with space_id
        connection.execute(
            sa.text("UPDATE teams SET space_id = :space_id WHERE id = :team_id"),
            {"space_id": space_id, "team_id": team_id}
        )
        
        # Update existing roles with space_id
        connection.execute(
            sa.text("UPDATE roles SET space_id = :space_id WHERE team_id = :team_id"),
            {"space_id": space_id, "team_id": team_id}
        )
        
        # Update existing team_executions with space_id
        connection.execute(
            sa.text("UPDATE team_executions SET space_id = :space_id WHERE team_id = :team_id"),
            {"space_id": space_id, "team_id": team_id}
        )
        
        # Update existing task_executions with space_id (via team_executions)
        connection.execute(
            sa.text("""
                UPDATE task_executions 
                SET space_id = :space_id 
                WHERE team_execution_id IN (
                    SELECT id FROM team_executions WHERE team_id = :team_id
                )
            """),
            {"space_id": space_id, "team_id": team_id}
        )


def downgrade() -> None:
    # Get connection
    connection = op.get_bind()
    
    # Remove space_id from all tables
    connection.execute(sa.text("UPDATE teams SET space_id = NULL"))
    connection.execute(sa.text("UPDATE roles SET space_id = NULL"))
    connection.execute(sa.text("UPDATE team_executions SET space_id = NULL"))
    connection.execute(sa.text("UPDATE task_executions SET space_id = NULL"))
    
    # Delete all team_spaces
    connection.execute(sa.text("DELETE FROM team_spaces")) 