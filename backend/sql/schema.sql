-- Purpose: Supabase PostgreSQL schema for recommendation platform with telemetry and feedback loop.
-- Callers: Supabase SQL Editor / psql migration application.
-- Deps: PostgreSQL with pgcrypto extension for gen_random_uuid.
-- API: DDL + seed inserts for master, telemetry, feedback, and prediction log tables.
-- Side effects: Creates tables and indexes used by backend logging, metrics, and retraining flow.

create extension if not exists pgcrypto;

create table if not exists sma_tracks (
  id serial primary key,
  name varchar(50) not null unique,
  is_active boolean default true,
  created_at timestamptz default now()
);

insert into sma_tracks (name)
values ('IPA'), ('IPS'), ('Bahasa')
on conflict (name) do nothing;

create table if not exists majors (
  id serial primary key,
  name varchar(150) not null unique,
  cluster varchar(50),
  description text,
  is_active boolean default true,
  created_at timestamptz default now()
);

insert into majors (name, cluster)
values
  ('Teknik Informatika', 'STEM'),
  ('Sistem Informasi', 'STEM'),
  ('Teknik Sipil', 'STEM'),
  ('Teknik Elektro', 'STEM'),
  ('Kedokteran', 'Health'),
  ('Farmasi', 'Health'),
  ('Biologi', 'Health'),
  ('Matematika', 'STEM'),
  ('Psikologi', 'Social'),
  ('Ilmu Komunikasi', 'Social'),
  ('Hukum', 'Social'),
  ('Pendidikan Bahasa Inggris', 'Social'),
  ('Manajemen', 'Business'),
  ('Akuntansi', 'Business'),
  ('Desain Komunikasi Visual', 'Arts')
on conflict (name) do nothing;

create table if not exists interests (
  id serial primary key,
  name varchar(100) not null unique,
  description text,
  is_active boolean default true,
  created_at timestamptz default now()
);

insert into interests (name)
values
  ('Teknologi'),
  ('Data & AI'),
  ('Rekayasa'),
  ('Sosial/Manusia'),
  ('Komunikasi'),
  ('Hukum/Politik'),
  ('Alam/Kesehatan'),
  ('Bisnis/Manajemen'),
  ('Seni/Kreatif'),
  ('Pendidikan/Bahasa')
on conflict (name) do nothing;

create table if not exists prediction_log (
  id uuid primary key default gen_random_uuid(),
  session_id uuid,
  sma_track varchar(50),
  math_score numeric(5,2),
  physics_score numeric(5,2),
  chemistry_score numeric(5,2),
  biology_score numeric(5,2),
  economics_score numeric(5,2),
  indonesian_score numeric(5,2),
  english_score numeric(5,2),
  interests text[],
  top_1_major varchar(150),
  top_1_score numeric(5,4),
  top_2_major varchar(150),
  top_2_score numeric(5,4),
  top_3_major varchar(150),
  top_3_score numeric(5,4),
  model_version varchar(30),
  source varchar(30) default 'web',
  created_at timestamptz default now()
);

create table if not exists prediction_metrics (
  id uuid primary key default gen_random_uuid(),
  session_id uuid,
  model_version varchar(30) not null,
  latency_ms numeric(10,2) not null,
  sma_track varchar(50),
  features jsonb not null,
  top_major varchar(150),
  bias_score numeric(8,4) default 0,
  created_at timestamptz default now()
);

create table if not exists user_feedback (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  selected_major varchar(150),
  aligns_with_goals boolean not null,
  rating int not null check (rating between 1 and 5),
  notes text,
  created_at timestamptz default now()
);

create table if not exists prediction_explanations (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null,
  model_version varchar(30) not null,
  major varchar(150) not null,
  shap_values jsonb not null,
  created_at timestamptz default now()
);

create index if not exists idx_prediction_log_created_at on prediction_log(created_at);
create index if not exists idx_prediction_log_top_1 on prediction_log(top_1_major);
create index if not exists idx_prediction_metrics_created_at on prediction_metrics(created_at);
create index if not exists idx_prediction_metrics_model_version on prediction_metrics(model_version);
create index if not exists idx_user_feedback_created_at on user_feedback(created_at);
create index if not exists idx_user_feedback_rating on user_feedback(rating);
create index if not exists idx_prediction_explanations_session_id on prediction_explanations(session_id);
create index if not exists idx_prediction_explanations_created_at on prediction_explanations(created_at);
