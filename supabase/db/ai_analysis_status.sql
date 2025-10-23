-- 인공지능 분석 상태 관리 테이블
-- tb_instagram_crawling 테이블의 각 레코드에 대한 AI 분석 상태를 추적

create table public.ai_analysis_status (
  id character varying(200) not null,
  is_analyzed boolean not null default false,
  analyzed_at timestamp with time zone null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint ai_analysis_status_pkey primary key (id),
  constraint fk_ai_analysis_status_crawling_id foreign key (id) 
    references public.tb_instagram_crawling(id) on delete cascade
) TABLESPACE pg_default;

-- 테이블 코멘트
comment on table public.ai_analysis_status is '인공지능 분석 상태 관리 테이블';
comment on column public.ai_analysis_status.id is 'tb_instagram_crawling 테이블의 id와 동일';
comment on column public.ai_analysis_status.is_analyzed is 'AI 분석 완료 여부 (true: 분석완료, false: 미분석)';
comment on column public.ai_analysis_status.analyzed_at is 'AI 분석 완료 시간';
comment on column public.ai_analysis_status.created_at is '레코드 생성 시간';
comment on column public.ai_analysis_status.updated_at is '레코드 수정 시간';

-- 인덱스 생성
create index if not exists idx_ai_analysis_status_is_analyzed on public.ai_analysis_status using btree (is_analyzed);
create index if not exists idx_ai_analysis_status_analyzed_at on public.ai_analysis_status using btree (analyzed_at);
create index if not exists idx_ai_analysis_status_created_at on public.ai_analysis_status using btree (created_at);

-- updated_at 자동 업데이트 트리거 함수 (이미 존재한다면 스킵)
create or replace function _touch_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- updated_at 트리거 생성
create trigger trg_ai_analysis_status_touch_updated_at 
  before update on public.ai_analysis_status 
  for each row 
  execute function _touch_updated_at();
