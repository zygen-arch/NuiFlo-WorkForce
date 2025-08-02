"""Populate space_id for existing teams

Revision ID: 005_populate_spaces
Revises: 004_add_team_spaces
Create Date: 2024-08-02 02:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
import json
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_populate_spaces'
down_revision = '004_add_team_spaces'
branch_labels = None
depends_on = None


def upgrade():
    # Get connection
    connection = op.get_bind()
    
    # Get all existing teams
    teams_result = connection.execute(sa.text("SELECT id, name FROM teams"))
    teams = teams_result.fetchall()
    
    for team in teams:
        team_id = team[0]
        team_name = team[1]
        
        # Create a space for this team
        space_id = f"space_{uuid.uuid4()}"
        space_name = f"{team_name} Space"
        
        # Prepare settings as JSON string
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
        
        # Insert team space
        connection.execute(sa.text("""
            INSERT INTO team_spaces (id, team_id, name, description, settings, storage_config, created_at, updated_at)
            VALUES (:space_id, :team_id, :name, :description, :settings, :storage_config, NOW(), NOW())
        """), {
            'space_id': space_id,
            'team_id': team_id,
            'name': space_name,
            'description': f"Default space for {team_name}",
            'settings': json.dumps(settings),
            'storage_config': json.dumps({})
        })
        
        # Update team with space_id
        connection.execute(sa.text("""
            UPDATE teams SET space_id = :space_id WHERE id = :team_id
        """), {
            'space_id': space_id,
            'team_id': team_id
        })
        
        # Update roles for this team
        connection.execute(sa.text("""
            UPDATE roles SET space_id = :space_id WHERE team_id = :team_id
        """), {
            'space_id': space_id,
            'team_id': team_id
        })
        
        # Update team_executions for this team
        connection.execute(sa.text("""
            UPDATE team_executions SET space_id = :space_id WHERE team_id = :team_id
        """), {
            'space_id': space_id,
            'team_id': team_id
        })
        
        # Update task_executions for this team (via roles)
        connection.execute(sa.text("""
            UPDATE task_executions SET space_id = :space_id 
            WHERE role_id IN (SELECT id FROM roles WHERE team_id = :team_id)
        """), {
            'space_id': space_id,
            'team_id': team_id
        })


def downgrade():
    # This migration is data migration, so downgrade would require
    # removing all space_id values and team_spaces records
    connection = op.get_bind()
    
    # Remove space_id from all tables
    connection.execute(sa.text("UPDATE teams SET space_id = NULL"))
    connection.execute(sa.text("UPDATE roles SET space_id = NULL"))
    connection.execute(sa.text("UPDATE team_executions SET space_id = NULL"))
    connection.execute(sa.text("UPDATE task_executions SET space_id = NULL"))
    
    # Remove all team_spaces records
    connection.execute(sa.text("DELETE FROM team_spaces")) 