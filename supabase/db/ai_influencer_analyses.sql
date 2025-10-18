-- AI 인플루언서 분석 결과 테이블
-- AI를 통해 분석된 인플루언서 데이터를 저장하는 테이블

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

-- 테이블 코멘트
comment on table public.ai_influencer_analyses is 'AI 인플루언서 분석 결과 저장 테이블';
comment on column public.ai_influencer_analyses.id is '분석 결과 고유 ID';
comment on column public.ai_influencer_analyses.influencer_id is '인플루언서 ID (tb_instagram_crawling 테이블의 id와 동일)';
comment on column public.ai_influencer_analyses.platform is '플랫폼 (instagram, youtube, tiktok 등)';
comment on column public.ai_influencer_analyses.name is '인플루언서 이름';
comment on column public.ai_influencer_analyses.alias is '인플루언서 별명/닉네임';
comment on column public.ai_influencer_analyses.followers is '팔로워 수';
comment on column public.ai_influencer_analyses.followings is '팔로잉 수';
comment on column public.ai_influencer_analyses.posts_count is '게시물 수';
comment on column public.ai_influencer_analyses.category is '카테고리';
comment on column public.ai_influencer_analyses.tags is '태그 배열';
comment on column public.ai_influencer_analyses.follow_network_analysis is '팔로워 네트워크 분석 결과 (JSON)';
comment on column public.ai_influencer_analyses.comment_authenticity_analysis is '댓글 진정성 분석 결과 (JSON)';
comment on column public.ai_influencer_analyses.content_analysis is '콘텐츠 분석 결과 (JSON)';
comment on column public.ai_influencer_analyses.evaluation is '종합 평가 결과 (JSON)';
comment on column public.ai_influencer_analyses.insights is '인사이트 (JSON)';
comment on column public.ai_influencer_analyses.summary is '분석 요약';
comment on column public.ai_influencer_analyses.recommendation is '추천도 (매우 추천, 추천, 보통, 비추천, 매우 비추천)';
comment on column public.ai_influencer_analyses.notes is '추가 노트 (JSON)';
comment on column public.ai_influencer_analyses.inference_confidence is '추론 신뢰도 (0-1, 자동 생성)';
comment on column public.ai_influencer_analyses.engagement_score is '참여도 점수 (0-10, 자동 생성)';
comment on column public.ai_influencer_analyses.activity_score is '활동성 점수 (0-10, 자동 생성)';
comment on column public.ai_influencer_analyses.communication_score is '소통능력 점수 (0-10, 자동 생성)';
comment on column public.ai_influencer_analyses.growth_potential_score is '성장잠재력 점수 (0-10, 자동 생성)';
comment on column public.ai_influencer_analyses.overall_score is '종합점수 (0-10, 자동 생성)';
comment on column public.ai_influencer_analyses.source is '분석 소스 (ai_auto, manual 등)';
comment on column public.ai_influencer_analyses.analyzed_at is '분석 완료일시';
comment on column public.ai_influencer_analyses.analyzed_on is '분석 완료일';
comment on column public.ai_influencer_analyses.created_at is '생성일시';
comment on column public.ai_influencer_analyses.updated_at is '수정일시';

-- 인덱스 생성
create unique INDEX IF not exists uq_ai_influencer_alias_per_day on public.ai_influencer_analyses using btree (
  COALESCE(
    influencer_id,
    'unknown'::character varying
  ),
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

create index IF not exists idx_ai_influencer_analyses_insights_gin on public.ai_influencer_analyses using gin (insights jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_evaluation_gin on public.ai_influencer_analyses using gin (evaluation jsonb_path_ops) TABLESPACE pg_default;

create index IF not exists idx_ai_influencer_analyses_notes_gin on public.ai_influencer_analyses using gin (notes jsonb_path_ops) TABLESPACE pg_default;

-- 트리거 생성
create trigger trg_ai_influencer_analyses_set_analyzed_on BEFORE INSERT
or
update on ai_influencer_analyses for EACH row
execute FUNCTION _set_analyzed_on ();

create trigger trg_ai_influencer_analyses_touch_updated_at BEFORE
update on ai_influencer_analyses for EACH row
execute FUNCTION _touch_updated_at ();
