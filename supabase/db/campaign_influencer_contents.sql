create table public.campaign_influencer_contents (
  id uuid not null default gen_random_uuid (),
  participation_id uuid not null,
  content_url text not null,
  posted_at timestamp with time zone null,
  caption text null,
  qualitative_note text null,
  likes integer not null default 0,
  comments integer not null default 0,
  shares integer not null default 0,
  views integer not null default 0,
  clicks integer not null default 0,
  conversions integer not null default 0,
  is_rels integer not null default 0,
  created_by uuid null default auth.uid (),
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint campaign_influencer_contents_pkey primary key (id),
  constraint uq_participation_url unique (participation_id, content_url),
  constraint campaign_influencer_contents_participation_id_fkey foreign KEY (participation_id) references campaign_influencer_participations (id) on delete CASCADE,
  constraint campaign_influencer_contents_likes_check check ((likes >= 0)),
  constraint campaign_influencer_contents_clicks_check check ((clicks >= 0)),
  constraint campaign_influencer_contents_conversions_check check ((conversions >= 0)),
  constraint campaign_influencer_contents_shares_check check ((shares >= 0)),
  constraint campaign_influencer_contents_views_check check ((views >= 0)),
  constraint campaign_influencer_contents_comments_check check ((comments >= 0))
) TABLESPACE pg_default;

create index IF not exists idx_cic_participation on public.campaign_influencer_contents using btree (participation_id) TABLESPACE pg_default;

create index IF not exists idx_cic_created_at on public.campaign_influencer_contents using btree (created_at) TABLESPACE pg_default;

create trigger set_timestamp_campaign_influencer_contents BEFORE
update on campaign_influencer_contents for EACH row
execute FUNCTION trigger_set_timestamp ();