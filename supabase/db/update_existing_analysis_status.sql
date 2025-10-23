-- 기존 ai_influencer_analyses 데이터에 대해 분석 상태를 true로 업데이트하는 스크립트

-- 1. 기존 ai_influencer_analyses에 있는 influencer_id들을 기반으로 
--    ai_analysis_status 테이블에 레코드가 없다면 추가하고 is_analyzed를 true로 설정
insert into public.ai_analysis_status (id, is_analyzed, analyzed_at, created_at, updated_at)
select 
  aia.influencer_id,
  true as is_analyzed,
  aia.analyzed_at,
  aia.created_at,
  now() as updated_at
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.ai_analysis_status aas 
    where aas.id = aia.influencer_id
  )
on conflict (id) do update set
  is_analyzed = true,
  analyzed_at = excluded.analyzed_at,
  updated_at = now();

-- 2. tb_instagram_crawling 테이블의 AI 분석 상태도 업데이트
update public.tb_instagram_crawling 
set 
  ai_analysis_status = true,
  ai_analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
where tb_instagram_crawling.id = aia.influencer_id
  and aia.influencer_id is not null;

-- 3. 기존 ai_analysis_status 테이블의 is_analyzed를 true로 업데이트 (이미 존재하는 레코드들)
update public.ai_analysis_status 
set 
  is_analyzed = true,
  analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
where ai_analysis_status.id = aia.influencer_id
  and aia.influencer_id is not null;

-- 4. 결과 확인 쿼리 (실행 후 확인용)
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
