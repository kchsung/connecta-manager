-- tb_instagram_crawling 테이블에 AI 분석 관련 컬럼 추가

-- AI 분석 상태 컬럼 추가
alter table public.tb_instagram_crawling 
add column if not exists ai_analysis_status boolean not null default false;

-- AI 분석 완료 시간 컬럼 추가
alter table public.tb_instagram_crawling 
add column if not exists ai_analyzed_at timestamp with time zone null;

-- 컬럼 코멘트 추가
comment on column public.tb_instagram_crawling.ai_analysis_status is 'AI 분석 완료 여부 (true: 분석완료, false: 미분석)';
comment on column public.tb_instagram_crawling.ai_analyzed_at is 'AI 분석 완료 시간';

-- 인덱스 생성
create index if not exists idx_tb_instagram_crawling_ai_analysis_status 
  on public.tb_instagram_crawling using btree (ai_analysis_status);

create index if not exists idx_tb_instagram_crawling_ai_analyzed_at 
  on public.tb_instagram_crawling using btree (ai_analyzed_at);

-- 복합 인덱스 (AI 분석 대상 조회용)
create index if not exists idx_tb_instagram_crawling_analysis_target 
  on public.tb_instagram_crawling using btree (status, ai_analysis_status) 
  where status = 'COMPLETE' and ai_analysis_status = false;
