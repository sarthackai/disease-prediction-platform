-- ============================================
-- EXTENSIONS
-- ============================================
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- ============================================
-- ENUM TYPES
-- ============================================
create type user_role as enum ('patient', 'admin');
create type appointment_status as enum ('pending', 'confirmed', 'cancelled', 'completed');
create type severity_level as enum ('low', 'moderate', 'high', 'critical');
create type metric_type as enum (
  'daily_active_users', 'prediction_count', 'disease_distribution',
  'model_accuracy', 'model_drift', 'avg_confidence'
);

-- ============================================
-- USERS  (extends Supabase auth.users)
-- ============================================
create table public.users (
  user_id         uuid primary key default uuid_generate_v4()
                    references auth.users(id) on delete cascade,
  full_name       text not null,
  email           text unique not null,
  role            user_role not null default 'patient',
  phone           text,
  age             smallint check (age between 0 and 130),
  gender          text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

-- ============================================
-- DISEASES
-- ============================================
create table public.diseases (
  disease_id        uuid primary key default uuid_generate_v4(),
  disease_name      text unique not null,
  description       text,
  prevention_tips   text[],
  severity_level    severity_level not null default 'moderate',
  specialist_type   text,
  common_symptoms   text[],
  created_at        timestamptz not null default now()
);

-- ============================================
-- PREDICTIONS
-- ============================================
create table public.predictions (
  prediction_id        uuid primary key default uuid_generate_v4(),
  user_id               uuid not null references public.users(user_id) on delete cascade,
  predicted_disease_id  uuid references public.diseases(disease_id),
  symptoms_input        jsonb not null,
  confidence_score      numeric(5,4) check (confidence_score between 0 and 1),
  severity_score        numeric(5,4),
  top_predictions       jsonb,
  shap_explanation      jsonb,
  model_used            text not null,
  model_version         text not null,
  input_method          text default 'manual',
  created_at            timestamptz not null default now()
);

create index idx_predictions_user_id on public.predictions(user_id);
create index idx_predictions_created_at on public.predictions(created_at desc);
create index idx_predictions_disease_id on public.predictions(predicted_disease_id);

-- ============================================
-- HOSPITALS
-- ============================================
create table public.hospitals (
  hospital_id     uuid primary key default uuid_generate_v4(),
  name            text not null,
  latitude        double precision not null,
  longitude       double precision not null,
  address         text,
  phone           text,
  rating          numeric(2,1) check (rating between 0 and 5),
  specialties     text[],
  osm_place_id    text unique,
  source          text default 'osm',
  last_synced_at  timestamptz,
  created_at      timestamptz not null default now()
);

create index idx_hospitals_location on public.hospitals(latitude, longitude);

-- ============================================
-- APPOINTMENTS
-- ============================================
create table public.appointments (
  appointment_id    uuid primary key default uuid_generate_v4(),
  user_id            uuid not null references public.users(user_id) on delete cascade,
  hospital_id        uuid not null references public.hospitals(hospital_id),
  prediction_id       uuid references public.predictions(prediction_id),
  preferred_date       date,
  status               appointment_status not null default 'pending',
  notes                 text,
  created_at            timestamptz not null default now()
);

create index idx_appointments_user_id on public.appointments(user_id);

-- ============================================
-- MEDICAL REPORTS
-- ============================================
create table public.medical_reports (
  report_id       uuid primary key default uuid_generate_v4(),
  prediction_id    uuid not null references public.predictions(prediction_id) on delete cascade,
  user_id           uuid not null references public.users(user_id) on delete cascade,
  pdf_storage_path   text not null,
  generated_at        timestamptz not null default now()
);

-- ============================================
-- ANALYTICS
-- ============================================
create table public.analytics (
  analytics_id      uuid primary key default uuid_generate_v4(),
  metric_type        metric_type not null,
  metric_value         jsonb not null,
  recorded_for_date     date not null,
  model_version          text,
  created_at              timestamptz not null default now()
);

create unique index idx_analytics_unique_metric_day
  on public.analytics(metric_type, recorded_for_date, model_version);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
alter table public.users enable row level security;
alter table public.predictions enable row level security;
alter table public.appointments enable row level security;
alter table public.medical_reports enable row level security;
alter table public.hospitals enable row level security;
alter table public.diseases enable row level security;
alter table public.analytics enable row level security;

create policy "users_self_access" on public.users
  for all using (auth.uid() = user_id);

create policy "predictions_self_access" on public.predictions
  for all using (auth.uid() = user_id);

create policy "appointments_self_access" on public.appointments
  for all using (auth.uid() = user_id);

create policy "reports_self_access" on public.medical_reports
  for all using (auth.uid() = user_id);

create policy "diseases_public_read" on public.diseases
  for select using (true);

create policy "hospitals_public_read" on public.hospitals
  for select using (true);

create or replace function public.is_admin() returns boolean as $$
  select exists (
    select 1 from public.users
    where user_id = auth.uid() and role = 'admin'
  );
$$ language sql security definer;

create policy "admin_full_access_predictions" on public.predictions
  for all using (public.is_admin());

create policy "admin_full_access_analytics" on public.analytics
  for all using (public.is_admin());

create policy "admin_manage_diseases" on public.diseases
  for all using (public.is_admin());

create policy "admin_manage_hospitals" on public.hospitals
  for all using (public.is_admin());