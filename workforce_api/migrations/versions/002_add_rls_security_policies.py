"""Add RLS security policies and Supabase Auth integration

Revision ID: 002_rls_security
Revises: 99f80f3018e3
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_rls_security'
down_revision = '99f80f3018e3_create_initial_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply RLS security policies and add Supabase Auth integration."""
    
    # Step 1: Add auth_owner_id column to teams table
    op.add_column('teams', sa.Column('auth_owner_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key('fk_teams_auth_owner', 'teams', 'auth.users', ['auth_owner_id'], ['id'])
    op.create_index('idx_teams_auth_owner_id', 'teams', ['auth_owner_id'])
    
    # Step 2: Create profiles table for Supabase Auth
    op.create_table('profiles',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('full_name', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Step 3: Enable Row Level Security on all tables
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE teams ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE roles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE team_executions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE task_executions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY")
    
    # Step 4: Create security helper functions
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
    
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_role(role_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER
        AS $$
          SELECT team_id FROM roles WHERE id = role_id;
        $$;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_team_from_execution(execution_id integer)
        RETURNS integer
        LANGUAGE sql SECURITY DEFINER
        AS $$
          SELECT team_id FROM team_executions WHERE id = execution_id;
        $$;
    """)
    
    # Step 5: Create RLS policies for users table
    op.execute("""
        CREATE POLICY "Users can view own profile" ON users
          FOR SELECT USING (id = auth.uid()::text::integer);
    """)
    
    op.execute("""
        CREATE POLICY "Users can update own profile" ON users
          FOR UPDATE USING (id = auth.uid()::text::integer);
    """)
    
    op.execute("""
        CREATE POLICY "Users can insert own profile" ON users
          FOR INSERT WITH CHECK (id = auth.uid()::text::integer);
    """)
    
    # Step 6: Create RLS policies for teams table
    op.execute("""
        CREATE POLICY "Users can view own teams" ON teams
          FOR SELECT USING (
            COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
          );
    """)
    
    op.execute("""
        CREATE POLICY "Users can create teams" ON teams
          FOR INSERT WITH CHECK (auth_owner_id = auth.uid());
    """)
    
    op.execute("""
        CREATE POLICY "Users can update own teams" ON teams
          FOR UPDATE USING (
            COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
          );
    """)
    
    op.execute("""
        CREATE POLICY "Users can delete own teams" ON teams
          FOR DELETE USING (
            COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
          );
    """)
    
    # Step 7: Create RLS policies for roles table
    op.execute("""
        CREATE POLICY "Users can view roles from own teams" ON roles
          FOR SELECT USING (public.user_owns_team(team_id));
    """)
    
    op.execute("""
        CREATE POLICY "Users can create roles in own teams" ON roles
          FOR INSERT WITH CHECK (public.user_owns_team(team_id));
    """)
    
    op.execute("""
        CREATE POLICY "Users can update roles in own teams" ON roles
          FOR UPDATE USING (public.user_owns_team(team_id));
    """)
    
    op.execute("""
        CREATE POLICY "Users can delete roles from own teams" ON roles
          FOR DELETE USING (public.user_owns_team(team_id));
    """)
    
    # Step 8: Create RLS policies for team_executions table
    op.execute("""
        CREATE POLICY "Users can view executions from own teams" ON team_executions
          FOR SELECT USING (public.user_owns_team(team_id));
    """)
    
    op.execute("""
        CREATE POLICY "Users can create executions in own teams" ON team_executions
          FOR INSERT WITH CHECK (public.user_owns_team(team_id));
    """)
    
    op.execute("""
        CREATE POLICY "Users can update executions in own teams" ON team_executions
          FOR UPDATE USING (public.user_owns_team(team_id));
    """)
    
    # Step 9: Create RLS policies for task_executions table
    op.execute("""
        CREATE POLICY "Users can view task executions from own teams" ON task_executions
          FOR SELECT USING (public.user_owns_team(public.get_team_from_execution(team_execution_id)));
    """)
    
    op.execute("""
        CREATE POLICY "Users can create task executions in own teams" ON task_executions
          FOR INSERT WITH CHECK (public.user_owns_team(public.get_team_from_execution(team_execution_id)));
    """)
    
    op.execute("""
        CREATE POLICY "Users can update task executions in own teams" ON task_executions
          FOR UPDATE USING (public.user_owns_team(public.get_team_from_execution(team_execution_id)));
    """)
    
    # Step 10: Create RLS policies for profiles table
    op.execute("""
        CREATE POLICY "Users can view own profile" ON profiles
          FOR SELECT USING (auth.uid() = id);
    """)
    
    op.execute("""
        CREATE POLICY "Users can update own profile" ON profiles
          FOR UPDATE USING (auth.uid() = id);
    """)
    
    op.execute("""
        CREATE POLICY "Users can insert own profile" ON profiles
          FOR INSERT WITH CHECK (auth.uid() = id);
    """)
    
    # Step 11: Create trigger function for auto-creating profiles
    op.execute("""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = public
        AS $$
        BEGIN
          INSERT INTO public.profiles (id, email, full_name)
          VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
          RETURN new;
        END;
        $$;
    """)
    
    # Note: The trigger creation on auth.users requires superuser privileges
    # This will need to be done manually in Supabase Dashboard or by support
    # op.execute("CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();")


def downgrade() -> None:
    """Remove RLS security policies and revert to insecure state."""
    
    # Drop all policies
    op.execute("DROP POLICY IF EXISTS \"Users can view own profile\" ON users")
    op.execute("DROP POLICY IF EXISTS \"Users can update own profile\" ON users")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own profile\" ON users")
    
    op.execute("DROP POLICY IF EXISTS \"Users can view own teams\" ON teams")
    op.execute("DROP POLICY IF EXISTS \"Users can create teams\" ON teams")
    op.execute("DROP POLICY IF EXISTS \"Users can update own teams\" ON teams")
    op.execute("DROP POLICY IF EXISTS \"Users can delete own teams\" ON teams")
    
    op.execute("DROP POLICY IF EXISTS \"Users can view roles from own teams\" ON roles")
    op.execute("DROP POLICY IF EXISTS \"Users can create roles in own teams\" ON roles")
    op.execute("DROP POLICY IF EXISTS \"Users can update roles in own teams\" ON roles")
    op.execute("DROP POLICY IF EXISTS \"Users can delete roles from own teams\" ON roles")
    
    op.execute("DROP POLICY IF EXISTS \"Users can view executions from own teams\" ON team_executions")
    op.execute("DROP POLICY IF EXISTS \"Users can create executions in own teams\" ON team_executions")
    op.execute("DROP POLICY IF EXISTS \"Users can update executions in own teams\" ON team_executions")
    
    op.execute("DROP POLICY IF EXISTS \"Users can view task executions from own teams\" ON task_executions")
    op.execute("DROP POLICY IF EXISTS \"Users can create task executions in own teams\" ON task_executions")
    op.execute("DROP POLICY IF EXISTS \"Users can update task executions in own teams\" ON task_executions")
    
    op.execute("DROP POLICY IF EXISTS \"Users can view own profile\" ON profiles")
    op.execute("DROP POLICY IF EXISTS \"Users can update own profile\" ON profiles")
    op.execute("DROP POLICY IF EXISTS \"Users can insert own profile\" ON profiles")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS public.user_owns_team(integer)")
    op.execute("DROP FUNCTION IF EXISTS public.get_team_from_role(integer)")
    op.execute("DROP FUNCTION IF EXISTS public.get_team_from_execution(integer)")
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user()")
    
    # Disable RLS
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE teams DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE roles DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE team_executions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE task_executions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE profiles DISABLE ROW LEVEL SECURITY")
    
    # Drop profiles table
    op.drop_table('profiles')
    
    # Drop auth_owner_id column
    op.drop_index('idx_teams_auth_owner_id')
    op.drop_constraint('fk_teams_auth_owner', 'teams', type_='foreignkey')
    op.drop_column('teams', 'auth_owner_id') 