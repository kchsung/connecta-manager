-- 기존 ai_influencer_analyses 데이터에 대해 분석 상태를 true로 업데이트하는 스크립트 (공백 문제 해결)

-- 1. 먼저 공백 문제가 있는 데이터 확인
select 
  'Whitespace issues found' as issue_type,
  count(*) as count
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and length(aia.influencer_id) != length(trim(aia.influencer_id));

-- 2. ai_influencer_analyses의 influencer_id 공백 제거 (필요한 경우)
-- 주의: 이 작업은 데이터를 수정하므로 신중하게 실행하세요
/*
update public.ai_influencer_analyses 
set influencer_id = trim(influencer_id)
where influencer_id is not null
  and length(influencer_id) != length(trim(influencer_id));
*/

-- 3. tb_instagram_crawling의 id 공백 제거 (필요한 경우)
-- 주의: 이 작업은 데이터를 수정하므로 신중하게 실행하세요
/*
update public.tb_instagram_crawling 
set id = trim(id)
where id is not null
  and length(id) != length(trim(id));
*/

-- 4. 공백을 제거한 상태로 ai_analysis_status 테이블에 레코드 추가
insert into public.ai_analysis_status (id, is_analyzed, analyzed_at, created_at, updated_at)
select 
  trim(aia.influencer_id) as influencer_id,
  true as is_analyzed,
  aia.analyzed_at,
  aia.created_at,
  now() as updated_at
from public.ai_influencer_analyses aia
inner join public.tb_instagram_crawling tic on trim(tic.id) = trim(aia.influencer_id)
where aia.influencer_id is not null
  and not exists (
    select 1 from public.ai_analysis_status aas 
    where aas.id = trim(aia.influencer_id)
  )
on conflict (id) do update set
  is_analyzed = true,
  analyzed_at = excluded.analyzed_at,
  updated_at = now();

-- 5. tb_instagram_crawling 테이블의 AI 분석 상태 업데이트 (공백 제거하여 매칭)
update public.tb_instagram_crawling 
set 
  ai_analysis_status = true,
  ai_analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
where trim(tb_instagram_crawling.id) = trim(aia.influencer_id)
  and aia.influencer_id is not null;

-- 6. 기존 ai_analysis_status 테이블의 is_analyzed를 true로 업데이트 (공백 제거하여 매칭)
update public.ai_analysis_status 
set 
  is_analyzed = true,
  analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
inner join public.tb_instagram_crawling tic on trim(tic.id) = trim(aia.influencer_id)
where ai_analysis_status.id = trim(aia.influencer_id)
  and aia.influencer_id is not null;

-- 7. 결과 확인 쿼리
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

-- 8. 여전히 매칭되지 않는 데이터 확인
select 
  'Still unmatched in ai_influencer_analyses' as issue_type,
  count(*) as count
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.tb_instagram_crawling tic 
    where trim(tic.id) = trim(aia.influencer_id)
  );
