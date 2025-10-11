create table public.campaign_influencer_participations (
  id uuid not null default gen_random_uuid (),
  campaign_id uuid not null,
  influencer_id uuid not null,
  manager_comment text null,
  influencer_requests text null,
  memo text null,
  sample_status public.sample_status not null default '요청'::sample_status,
  influencer_feedback text null,
  content_uploaded boolean not null default false,
  cost_krw numeric(14, 2) not null default 0,
  content_links text[] not null default '{}'::text[],
  created_by uuid null default auth.uid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint campaign_influencer_participations_pkey primary key (id),
  constraint uq_campaign_influencer unique (campaign_id, influencer_id),
  constraint campaign_influencer_participations_campaign_id_fkey foreign KEY (campaign_id) references campaigns (id) on delete CASCADE,
  constraint campaign_influencer_participations_influencer_id_fkey foreign KEY (influencer_id) references connecta_influencers (id) on delete CASCADE,
  constraint chk_cost_krw_nonnegative check ((cost_krw >= (0)::numeric))
) TABLESPACE pg_default;

create index IF not exists cip_campaign_id_idx on public.campaign_influencer_participations using btree (campaign_id) TABLESPACE pg_default;

create index IF not exists cip_influencer_id_idx on public.campaign_influencer_participations using btree (influencer_id) TABLESPACE pg_default;

create index IF not exists cip_sample_status_idx on public.campaign_influencer_participations using btree (sample_status) TABLESPACE pg_default;

create index IF not exists cip_uploaded_idx on public.campaign_influencer_participations using btree (content_uploaded) TABLESPACE pg_default;

create index IF not exists cip_cost_idx on public.campaign_influencer_participations using btree (cost_krw) TABLESPACE pg_default;

create trigger set_timestamp_cip BEFORE
update on campaign_influencer_participations for EACH row
execute FUNCTION trigger_set_timestamp ();