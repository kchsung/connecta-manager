create table public.campaigns (
  id uuid not null default gen_random_uuid (),
  campaign_name text not null,
  campaign_description text null,
  campaign_type public.campaign_type not null,
  start_date date not null,
  end_date date null,
  status public.campaign_status not null default 'planned'::campaign_status,
  created_by uuid null default auth.uid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  campaign_instructions text null,
  tags text null default ''::text,
  constraint campaigns_pkey primary key (id),
  constraint campaigns_end_after_start check (
    (
      (end_date is null)
      or (end_date >= start_date)
    )
  )
) TABLESPACE pg_default;

create index IF not exists campaigns_type_idx on public.campaigns using btree (campaign_type) TABLESPACE pg_default;

create index IF not exists campaigns_status_idx on public.campaigns using btree (status) TABLESPACE pg_default;

create index IF not exists campaigns_start_date_idx on public.campaigns using btree (start_date) TABLESPACE pg_default;

create index IF not exists campaigns_tags_gin_idx on public.campaigns using gin (tags gin_trgm_ops) TABLESPACE pg_default;

create trigger set_timestamp_campaigns BEFORE
update on campaigns for EACH row
execute FUNCTION trigger_set_timestamp ();

create trigger trg_campaign_status_transition BEFORE
update OF status on campaigns for EACH row
execute FUNCTION validate_campaign_status_transition ();