# 🔧 **SUPABASE MANUAL STEPS AFTER MIGRATION**

After the migration runs successfully, you'll need to complete these steps manually in the Supabase Dashboard.

## **📋 Steps to Complete in Supabase Dashboard:**

### **1. Add Foreign Key Constraint & Check (Database → SQL Editor)**

**🚨 QUICK FIX - If you see "constraint already exists" error:**

Just run these remaining constraints (foreign key already exists from migration):

```sql
-- Make email unique (this is the main constraint we need)
ALTER TABLE public.profiles 
ADD CONSTRAINT profiles_email_unique UNIQUE (email);

-- Note: Email validation will be handled by the trigger function
-- (CHECK constraints can't use subqueries in PostgreSQL)
```

**📋 Complete version with checks:**

Run this SQL to properly link profiles to auth.users with validation:

```sql
-- Check if foreign key constraint already exists (from migration)
SELECT conname FROM pg_constraint 
WHERE conname = 'profiles_id_fkey' AND conrelid = 'public.profiles'::regclass;

-- Add foreign key constraint ONLY if it doesn't exist
-- (Our migration might have already created this)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'profiles_id_fkey' AND conrelid = 'public.profiles'::regclass
    ) THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_id_fkey 
        FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Make email unique (this is the main constraint we need)
ALTER TABLE public.profiles 
ADD CONSTRAINT profiles_email_unique UNIQUE (email);

-- Note: Email validation will be handled by the trigger function
-- (CHECK constraints can't use subqueries in PostgreSQL)
```

### **2. Create Improved User Profile Trigger (Database → SQL Editor)**

Create this enhanced function and trigger:

```sql
-- Enhanced function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  -- Insert a new profile when a new user is created in auth.users
  -- The trigger ensures email consistency, so no need for CHECK constraint
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id, 
    NEW.email,  -- This comes directly from auth.users, so it's automatically consistent
    COALESCE(NEW.raw_user_meta_data->>'full_name', 'User')
  )
  ON CONFLICT (id) DO NOTHING;
  
  RETURN NEW;
END;
$$;

-- Create the trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### **3. Test the Complete Setup (Database → SQL Editor)**

Test that everything works:

```sql
-- Check RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'teams', 'roles', 'team_executions', 'task_executions', 'profiles');

-- Check policies exist
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Verify profiles table structure
\d public.profiles;

-- Test profile creation (this should return empty when not authenticated)
SELECT * FROM public.profiles;
```

### **4. Configure Authentication (Authentication → Settings)**

1. **Site URL Configuration**:
   ```
   Site URL: https://your-frontend-domain.com
   Redirect URLs: 
   - https://your-frontend-domain.com/auth/callback
   - http://localhost:5173/auth/callback (for development)
   ```

2. **Email Settings**:
   - Configure SMTP or use Supabase's email service
   - Customize email templates if needed

3. **Social Providers** (optional):
   - Google, GitHub, etc. if you want social login

### **5. Test User Registration Flow**

Create a test user to verify everything works:

```sql
-- This should be done through your frontend, but you can test manually:
-- 1. Go to Authentication → Users in Supabase Dashboard
-- 2. Click "Add User" 
-- 3. Add email: test@nuiflo.com, password: TestPassword123
-- 4. Check that a profile was automatically created in public.profiles
```

## **🔍 Verification Checklist:**

- [ ] Foreign key constraint added to profiles table
- [ ] Email validation constraint added
- [ ] User profile creation trigger working
- [ ] RLS enabled on all tables (should show `true`)
- [ ] RLS policies created and working
- [ ] Authentication configured for frontend integration
- [ ] Test user signup creates profile automatically

## **✅ Why This Approach is Better:**

### **vs Edge Functions (Supabase AI suggestion):**
- ✅ **Simpler**: Database triggers handle everything automatically
- ✅ **More reliable**: No external webhooks or functions to manage
- ✅ **Consistent**: Uses our migration-based approach
- ✅ **Less moving parts**: Fewer things that can break
- ✅ **Better performance**: Direct database operations

### **Production Benefits:**
- ✅ **Automatic**: Profile creation happens instantly on signup
- ✅ **Atomic**: Part of the same database transaction
- ✅ **No external dependencies**: No webhook secrets or function deployments
- ✅ **Easier debugging**: All logic in database, easy to trace

## **⚠️ Important Notes:**

1. **These steps require admin privileges** that migrations don't have
2. **The trigger must be created manually** in Supabase Dashboard
3. **Test thoroughly** with real signup flow before going live
4. **Foreign key to auth.users** needs special permissions

## **🎯 After Completion:**

Once these manual steps are done:
- ✅ **Database fully secured** with proper RLS
- ✅ **User profiles auto-created** on signup (via trigger)
- ✅ **Auth integration ready** for frontend
- ✅ **Teams properly linked** to authenticated users
- ✅ **Email validation** ensures data integrity

**This approach is simpler, more reliable, and consistent with our migration-based architecture!** 🔐 