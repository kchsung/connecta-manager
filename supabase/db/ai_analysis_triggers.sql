-- AI 분석 상태 관리 트리거 함수들

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
