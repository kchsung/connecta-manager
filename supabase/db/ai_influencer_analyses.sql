create table public.ai_influencer_analyses (
  id uuid not null default gen_random_uuid (),
  influencer_id character varying(200) null,
  platform public.platform not null,
  name text null,
  alias text not null,
  followers bigint null,
  followings bigint null,
  posts_count integer null,
  category text not null,
  tags text[] not null default '{}'::text[],
  follow_network_analysis jsonb not null default '{}'::jsonb,
  comment_authenticity_analysis jsonb not null default '{}'::jsonb,
  content_analysis jsonb not null,
  evaluation jsonb not null,
  insights jsonb not null,
  summary text not null,
  recommendation public.recommendation_ko not null,
  notes jsonb not null,
  inference_confidence numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (content_analysis ->> 'inference_confidence'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  engagement_score numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (evaluation ->> 'engagement'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  activity_score numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (evaluation ->> 'activity'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  communication_score numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (evaluation ->> 'communication'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  growth_potential_score numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (evaluation ->> 'growth_potential'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  overall_score numeric GENERATED ALWAYS as (
    (
      NULLIF(
        TRIM(
          both '"'::text
          from
            (evaluation ->> 'overall_score'::text)
        ),
        ''::text
      )
    )::numeric
  ) STORED null,
  source text null default 'ai_auto'::text,
  analyzed_at timestamp with time zone not null default now(),
  analyzed_on date not null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint ai_influencer_analyses_pkey primary key (id),
  constraint chk_inference_confidence_range check (
    (
      (inference_confidence is null)
      or (
        (inference_confidence >= (0)::numeric)
        and (inference_confidence <= (1)::numeric)
      )
    )
  ),
  constraint chk_scores_range check (
    (
      (
        (engagement_score is null)
        or (
          (engagement_score >= (0)::numeric)
          and (engagement_score <= (10)::numeric)
        )
      )
      and (
        (activity_score is null)
        or (
          (activity_score >= (0)::numeric)
          and (activity_score <= (10)::numeric)
        )
      )
      and (
        (communication_score is null)
        or (
          (communication_score >= (0)::numeric)
          and (communication_score <= (10)::numeric)
        )
      )
      and (
        (growth_potential_score is null)
        or (
          (growth_potential_score >= (0)::numeric)
          and (growth_potential_score <= (10)::numeric)
        )
      )
      and (
        (overall_score is null)
        or (
          (overall_score >= (0)::numeric)
          and (overall_score <= (10)::numeric)
        )
      )
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_insights_gin on public.ai_influencer_analyses using gin (insights jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_evaluation_gin on public.ai_influencer_analyses using gin (evaluation jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_notes_gin on public.ai_influencer_analyses using gin (notes jsonb_path_ops) TABLESPACE pg_default;

create unique INDEX IF not exists uq_ai_influencer_alias_per_day on public.ai_influencer_analyses using btree (
  COALESCE(influencer_id, 'unknown'::character varying),
  alias,
  analyzed_on
) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_influencer_id on public.ai_influencer_analyses using btree (influencer_id) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_platform on public.ai_influencer_analyses using btree (platform) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_category on public.ai_influencer_analyses using btree (category) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_recommendation on public.ai_influencer_analyses using btree (recommendation) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_overall_score on public.ai_influencer_analyses using btree (overall_score) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_tags on public.ai_influencer_analyses using gin (tags) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_follow_network_gin on public.ai_influencer_analyses using gin (follow_network_analysis jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_comment_auth_gin on public.ai_influencer_analyses using gin (comment_authenticity_analysis jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_content_gin on public.ai_influencer_analyses using gin (content_analysis jsonb_path_ops) TABLESPACE pg_default;

create trigger trg_ai_influencer_analyses_set_analyzed_on BEFORE INSERT
or
update on ai_influencer_analyses for EACH row
execute FUNCTION _set_analyzed_on ();

create trigger trg_ai_influencer_analyses_touch_updated_at BEFORE
update on ai_influencer_analyses for EACH row
execute FUNCTION _touch_updated_at ();