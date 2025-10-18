-- Supabase schema for SentinelGuard
-- Run this in Supabase SQL Editor (or via psql) for your project

-- 1) users table
CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  role text NOT NULL DEFAULT 'admin',
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 2) anomaly_logs table
CREATE TABLE IF NOT EXISTS public.anomaly_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  metrics jsonb NOT NULL,
  score double precision,
  label text,
  timestamp timestamptz NOT NULL DEFAULT now()
);

-- 3) test_collection (used by backend/test_db.py)
CREATE TABLE IF NOT EXISTS public.test_collection (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  test boolean,
  message text,
  timestamp timestamptz
);

-- Optional: allow public (anon) role to select/insert for development only
-- WARNING: The following policy opens these tables to anyone with your anon key.
-- Use only for local development. For production use proper RLS policies.

-- Disable row level security (RLS) for development simplicity
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.anomaly_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_collection ENABLE ROW LEVEL SECURITY;

-- Policy to allow inserts/selects by authenticated role (adjust as needed)
CREATE POLICY "Allow anon selects and inserts (dev only)" ON public.users
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow anon selects and inserts (dev only)" ON public.anomaly_logs
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow anon selects and inserts (dev only)" ON public.test_collection
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- If you prefer to allow the anon key to read/write in dev, replace the policies above with:
-- CREATE POLICY "Allow anon read/write (dev only)" ON public.users
--   FOR ALL
--   USING (true)
--   WITH CHECK (true);

-- Same for the other tables.

-- End of migration
