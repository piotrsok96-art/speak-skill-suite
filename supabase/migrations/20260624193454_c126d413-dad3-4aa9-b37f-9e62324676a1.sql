CREATE TABLE public.profile_data (
  profile_id TEXT PRIMARY KEY,
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

GRANT SELECT, INSERT, UPDATE, DELETE ON public.profile_data TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profile_data TO authenticated;
GRANT ALL ON public.profile_data TO service_role;

ALTER TABLE public.profile_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read profile_data"
  ON public.profile_data FOR SELECT
  USING (true);

CREATE POLICY "Public insert profile_data"
  ON public.profile_data FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Public update profile_data"
  ON public.profile_data FOR UPDATE
  USING (true) WITH CHECK (true);

ALTER PUBLICATION supabase_realtime ADD TABLE public.profile_data;