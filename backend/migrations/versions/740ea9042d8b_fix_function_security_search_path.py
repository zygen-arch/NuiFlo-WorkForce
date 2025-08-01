"""fix_function_security_search_path

Revision ID: 740ea9042d8b
Revises: 002_rls_security
Create Date: 2025-01-27 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '740ea9042d8b'
down_revision: Union[str, None] = '002_rls_security'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix function security by adding SET search_path = public to all security definer functions."""
    
    # Fix user_owns_team function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.user_owns_team(team_id integer)
        RETURNS boolean
        LANGUAGE sql SECURITY DEFINER SET search_path = public
        AS $$
          SELECT EXISTS (
            SELECT 1 FROM teams 
            WHERE id = team_id 
            AND (
              auth_owner_id = auth.uid()
              OR owner_id = auth.uid()::text::integer
            )
          );
        $$;
    """)
    
    # Fix get_team_from_role function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_role(role_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER SET search_path = public
        AS $$
          SELECT team_id FROM roles WHERE id = role_id;
        $$;
    """)
    
    # Fix get_team_from_execution function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_execution(execution_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER SET search_path = public
        AS $$
          SELECT team_id FROM team_executions WHERE id = execution_id;
        $$;
    """)
    
    # Fix handle_new_user function (already has search_path but ensure it's correct)
    op.execute("""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = public
        AS $$
        BEGIN
          INSERT INTO public.profiles (id, email, full_name)
          VALUES (
            NEW.id, 
            NEW.email,
            COALESCE(NEW.raw_user_meta_data->>'full_name', 'User')
          )
          ON CONFLICT (id) DO NOTHING;
          
          RETURN NEW;
        END;
        $$;
    """)


def downgrade() -> None:
    """Revert function security changes by removing SET search_path."""
    
    # Revert user_owns_team function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.user_owns_team(team_id integer)
        RETURNS boolean
        LANGUAGE sql SECURITY DEFINER
        AS $$
          SELECT EXISTS (
            SELECT 1 FROM teams 
            WHERE id = team_id 
            AND (
              auth_owner_id = auth.uid()
              OR owner_id = auth.uid()::text::integer
            )
          );
        $$;
    """)
    
    # Revert get_team_from_role function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_role(role_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER
        AS $$
          SELECT team_id FROM roles WHERE id = role_id;
        $$;
    """)
    
    # Revert get_team_from_execution function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_execution(execution_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER
        AS $$
          SELECT team_id FROM team_executions WHERE id = execution_id;
        $$;
    """)
    
    # Revert handle_new_user function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = public
        AS $$
        BEGIN
          INSERT INTO public.profiles (id, email, full_name)
          VALUES (
            NEW.id, 
            NEW.email,
            COALESCE(NEW.raw_user_meta_data->>'full_name', 'User')
          )
          ON CONFLICT (id) DO NOTHING;
          
          RETURN NEW;
        END;
        $$;
    """) 