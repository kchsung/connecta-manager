-- 인공지능 분석 로직 개선 통합 실행 스크립트
-- 실행 순서: 1. 테이블 생성 → 2. 컬럼 추가 → 3. 트리거 생성 → 4. 기존 데이터 업데이트

-- ============================================
-- 1. AI 분석 상태 관리 테이블 생성
-- ============================================
create table if not exists public.ai_analysis_status (
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

-- ============================================
-- 2. tb_instagram_crawling 테이블에 AI 분석 관련 컬럼 추가
-- ============================================
alter table public.tb_instagram_crawling 
add column if not exists ai_analysis_status boolean not null default false;

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

-- ============================================
-- 3. 트리거 함수 및 트리거 생성
-- ============================================

-- updated_at 자동 업데이트 트리거 함수 (이미 존재한다면 스킵)
create or replace function _touch_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- 1. tb_instagram_crawling에 새 레코드가 추가될 때 ai_analysis_status 테이블에도 자동으로 레코드 추가
create or replace function insert_ai_analysis_status()
returns trigger as $$
begin
  -- ai_analysis_status 테이블에 새 레코드 삽입 (기본값: is_analyzed = false)
  insert into public.ai_analysis_status (id, is_analyzed, created_at, updated_at)
  values (new.id, false, now(), now())
  on conflict (id) do nothing; -- 이미 존재하는 경우 무시
  
  return new;
end;
$$ language plpgsql;

-- 2. ai_influencer_analyses에 새 분석 결과가 추가될 때 관련 테이블들의 분석 상태를 true로 업데이트
create or replace function update_ai_analysis_status_on_completion()
returns trigger as $$
begin
  -- ai_analysis_status 테이블의 is_analyzed를 true로 업데이트
  update public.ai_analysis_status 
  set 
    is_analyzed = true,
    analyzed_at = new.analyzed_at,
    updated_at = now()
  where id = new.influencer_id;
  
  -- tb_instagram_crawling 테이블의 AI 분석 상태도 업데이트
  update public.tb_instagram_crawling 
  set 
    ai_analysis_status = true,
    ai_analyzed_at = new.analyzed_at,
    updated_at = now()
  where id = new.influencer_id;
  
  return new;
end;
$$ language plpgsql;

-- 3. tb_instagram_crawling의 AI 분석 상태가 업데이트될 때 ai_analysis_status 테이블도 동기화
create or replace function sync_ai_analysis_status()
returns trigger as $$
begin
  -- ai_analysis_status 테이블의 상태도 동기화
  update public.ai_analysis_status 
  set 
    is_analyzed = new.ai_analysis_status,
    analyzed_at = new.ai_analyzed_at,
    updated_at = now()
  where id = new.id;
  
  return new;
end;
$$ language plpgsql;

-- 트리거 생성
-- 1. tb_instagram_crawling INSERT 트리거
drop trigger if exists trg_insert_ai_analysis_status on public.tb_instagram_crawling;
create trigger trg_insert_ai_analysis_status
  after insert on public.tb_instagram_crawling
  for each row
  execute function insert_ai_analysis_status();

-- 2. ai_influencer_analyses INSERT 트리거
drop trigger if exists trg_update_ai_analysis_status_on_completion on public.ai_influencer_analyses;
create trigger trg_update_ai_analysis_status_on_completion
  after insert on public.ai_influencer_analyses
  for each row
  execute function update_ai_analysis_status_on_completion();

-- 3. tb_instagram_crawling UPDATE 트리거 (AI 분석 상태 변경 시)
drop trigger if exists trg_sync_ai_analysis_status on public.tb_instagram_crawling;
create trigger trg_sync_ai_analysis_status
  after update of ai_analysis_status, ai_analyzed_at on public.tb_instagram_crawling
  for each row
  execute function sync_ai_analysis_status();

-- 4. ai_analysis_status updated_at 트리거
drop trigger if exists trg_ai_analysis_status_touch_updated_at on public.ai_analysis_status;
create trigger trg_ai_analysis_status_touch_updated_at 
  before update on public.ai_analysis_status 
  for each row 
  execute function _touch_updated_at();

-- ============================================
-- 4. 기존 데이터 업데이트
-- ============================================

-- 4-1. 기존 ai_influencer_analyses에 있는 influencer_id들을 기반으로 
--      ai_analysis_status 테이블에 레코드가 없다면 추가하고 is_analyzed를 true로 설정
--      (중복 제거: influencer_id별로 가장 최근 analyzed_at을 가진 레코드만 사용)
insert into public.ai_analysis_status (id, is_analyzed, analyzed_at, created_at, updated_at)
select 
  trim(aia.influencer_id) as influencer_id,
  true as is_analyzed,
  aia.analyzed_at,
  aia.created_at,
  now() as updated_at
from (
  -- 중복 제거: influencer_id별로 가장 최근 analyzed_at을 가진 레코드만 선택
  select distinct on (trim(influencer_id))
    influencer_id,
    analyzed_at,
    created_at
  from public.ai_influencer_analyses
  where influencer_id is not null
  order by trim(influencer_id), analyzed_at desc
) aia
inner join public.tb_instagram_crawling tic on trim(tic.id) = trim(aia.influencer_id)
where not exists (
  select 1 from public.ai_analysis_status aas 
  where aas.id = trim(aia.influencer_id)
)
on conflict (id) do update set
  is_analyzed = true,
  analyzed_at = excluded.analyzed_at,
  updated_at = now();

-- 4-2. tb_instagram_crawling 테이블의 AI 분석 상태도 업데이트 (중복 제거하여 매칭)
update public.tb_instagram_crawling 
set 
  ai_analysis_status = true,
  ai_analyzed_at = aia.analyzed_at,
  updated_at = now()
from (
  -- 중복 제거: influencer_id별로 가장 최근 analyzed_at을 가진 레코드만 선택
  select distinct on (trim(influencer_id))
    influencer_id,
    analyzed_at
  from public.ai_influencer_analyses
  where influencer_id is not null
  order by trim(influencer_id), analyzed_at desc
) aia
where trim(tb_instagram_crawling.id) = trim(aia.influencer_id);

-- 4-3. 기존 ai_analysis_status 테이블의 is_analyzed를 true로 업데이트 (이미 존재하는 레코드들)
--      (중복 제거하여 매칭)
update public.ai_analysis_status 
set 
  is_analyzed = true,
  analyzed_at = aia.analyzed_at,
  updated_at = now()
from (
  -- 중복 제거: influencer_id별로 가장 최근 analyzed_at을 가진 레코드만 선택
  select distinct on (trim(influencer_id))
    influencer_id,
    analyzed_at
  from public.ai_influencer_analyses
  where influencer_id is not null
  order by trim(influencer_id), analyzed_at desc
) aia
inner join public.tb_instagram_crawling tic on trim(tic.id) = trim(aia.influencer_id)
where ai_analysis_status.id = trim(aia.influencer_id);

-- ============================================
-- 5. 결과 확인
-- ============================================
-- 분석 완료된 데이터 개수 확인
select 
  'ai_analysis_status' as table_name,
  count(*) as total_records,
  count(*) filter (where is_analyzed = true) as analyzed_records,
  count(*) filter (where is_analyzed = false) as not_analyzed_records
from public.ai_analysis_status
union all
select 
  'tb_instagram_crawling' as table_name,
  count(*) as total_records,
  count(*) filter (where ai_analysis_status = true) as analyzed_records,
  count(*) filter (where ai_analysis_status = false) as not_analyzed_records
from public.tb_instagram_crawling
union all
select 
  'ai_influencer_analyses' as table_name,
  count(*) as total_records,
  count(*) as analyzed_records,
  0 as not_analyzed_records
from public.ai_influencer_analyses;

-- AI 분석 대상 데이터 확인 (status='COMPLETE' and ai_analysis_status=false)
select 
  count(*) as pending_analysis_count
from public.tb_instagram_crawling 
where status = 'COMPLETE' 
  and ai_analysis_status = false;
