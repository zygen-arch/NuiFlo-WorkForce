-- ========================================
-- CORRECTED SECURITY FIXES FOR NUIFLO WORKFORCE
-- ========================================
-- This version works with standard Supabase SQL Editor permissions

-- 1. ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ==========================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_executions ENABLE ROW LEVEL SECURITY;

-- 2. CREATE SECURITY DEFINER FUNCTIONS (in public schema)
-- =======================================================

-- Function to check if user owns a team
CREATE OR REPLACE FUNCTION public.user_owns_team(team_id integer)
RETURNS boolean
LANGUAGE sql SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM teams 
    WHERE id = team_id 
    AND owner_id = auth.uid()::text::integer
  );
$$;

-- Function to get team ID from role ID
CREATE OR REPLACE FUNCTION public.get_team_from_role(role_id integer)
RETURNS integer
LANGUAGE sql SECURITY DEFINER
AS $$
  SELECT team_id FROM roles WHERE id = role_id;
$$;

-- Function to get team ID from team execution
CREATE OR REPLACE FUNCTION public.get_team_from_execution(execution_id integer)
RETURNS integer
LANGUAGE sql SECURITY DEFINER
AS $$
  SELECT team_id FROM team_executions WHERE id = execution_id;
$$;

-- 3. CREATE RLS POLICIES
-- ======================

-- USERS TABLE POLICIES
-- Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (id = auth.uid()::text::integer);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (id = auth.uid()::text::integer);

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (id = auth.uid()::text::integer);

-- TEAMS TABLE POLICIES
-- Users can only access teams they own
CREATE POLICY "Users can view own teams" ON teams
  FOR SELECT USING (owner_id = auth.uid()::text::integer);

CREATE POLICY "Users can create teams" ON teams
  FOR INSERT WITH CHECK (owner_id = auth.uid()::text::integer);

CREATE POLICY "Users can update own teams" ON teams
  FOR UPDATE USING (owner_id = auth.uid()::text::integer);

CREATE POLICY "Users can delete own teams" ON teams
  FOR DELETE USING (owner_id = auth.uid()::text::integer);

-- ROLES TABLE POLICIES
-- Users can only access roles from teams they own
CREATE POLICY "Users can view roles from own teams" ON roles
  FOR SELECT USING (public.user_owns_team(team_id));

CREATE POLICY "Users can create roles in own teams" ON roles
  FOR INSERT WITH CHECK (public.user_owns_team(team_id));

CREATE POLICY "Users can update roles in own teams" ON roles
  FOR UPDATE USING (public.user_owns_team(team_id));

CREATE POLICY "Users can delete roles from own teams" ON roles
  FOR DELETE USING (public.user_owns_team(team_id));

-- TEAM EXECUTIONS TABLE POLICIES
-- Users can only access executions from teams they own
CREATE POLICY "Users can view executions from own teams" ON team_executions
  FOR SELECT USING (public.user_owns_team(team_id));

CREATE POLICY "Users can create executions in own teams" ON team_executions
  FOR INSERT WITH CHECK (public.user_owns_team(team_id));

CREATE POLICY "Users can update executions in own teams" ON team_executions
  FOR UPDATE USING (public.user_owns_team(team_id));

-- TASK EXECUTIONS TABLE POLICIES
-- Users can only access task executions from teams they own
CREATE POLICY "Users can view task executions from own teams" ON task_executions
  FOR SELECT USING (public.user_owns_team(public.get_team_from_execution(team_execution_id)));

CREATE POLICY "Users can create task executions in own teams" ON task_executions
  FOR INSERT WITH CHECK (public.user_owns_team(public.get_team_from_execution(team_execution_id)));

CREATE POLICY "Users can update task executions in own teams" ON task_executions
  FOR UPDATE USING (public.user_owns_team(public.get_team_from_execution(team_execution_id)));

-- 4. CREATE PROFILES TABLE LINKED TO SUPABASE AUTH
-- ================================================

-- Create a profiles table that's properly linked to auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email text,
  full_name text,
  avatar_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for profiles
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- 5. CREATE TRIGGER TO AUTO-CREATE PROFILE
-- ========================================

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Note: The trigger creation requires admin privileges
-- You may need to contact Supabase support or use the Dashboard to create this trigger
-- Alternatively, create profiles manually when users sign up

-- 6. ADD AUTH_OWNER_ID COLUMN TO TEAMS TABLE
-- ==========================================

-- Add new column for auth user reference
ALTER TABLE teams ADD COLUMN IF NOT EXISTS auth_owner_id uuid REFERENCES auth.users(id);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_teams_auth_owner_id ON teams(auth_owner_id);

-- 7. UPDATE TEAMS TABLE POLICIES TO USE AUTH_OWNER_ID
-- ==================================================

-- Drop old policies first
DROP POLICY IF EXISTS "Users can view own teams" ON teams;
DROP POLICY IF EXISTS "Users can create teams" ON teams;
DROP POLICY IF EXISTS "Users can update own teams" ON teams;
DROP POLICY IF EXISTS "Users can delete own teams" ON teams;

-- Create new policies using auth_owner_id
CREATE POLICY "Users can view own teams" ON teams
  FOR SELECT USING (
    COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
  );

CREATE POLICY "Users can create teams" ON teams
  FOR INSERT WITH CHECK (auth_owner_id = auth.uid());

CREATE POLICY "Users can update own teams" ON teams
  FOR UPDATE USING (
    COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
  );

CREATE POLICY "Users can delete own teams" ON teams
  FOR DELETE USING (
    COALESCE(auth_owner_id = auth.uid(), owner_id = auth.uid()::text::integer)
  );

-- Update the helper function to check both columns for backward compatibility
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

-- ========================================
-- VERIFICATION QUERIES
-- ========================================

-- Check RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'teams', 'roles', 'team_executions', 'task_executions', 'profiles');

-- Check policies exist
SELECT schemaname, tablename, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname; 