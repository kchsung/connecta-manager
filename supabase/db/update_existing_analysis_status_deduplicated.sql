-- 기존 ai_influencer_analyses 데이터에 대해 분석 상태를 true로 업데이트하는 스크립트 (중복 제거 버전)
-- ON CONFLICT DO UPDATE 오류 해결: 중복된 influencer_id 처리

-- 1. 중복된 influencer_id 확인
select 
  'Duplicate influencer_ids in ai_influencer_analyses' as issue_type,
  influencer_id,
  count(*) as duplicate_count
from public.ai_influencer_analyses
where influencer_id is not null
group by influencer_id
having count(*) > 1
order by duplicate_count desc
limit 10;

-- 2. 중복을 제거한 상태로 ai_analysis_status 테이블에 레코드 추가
-- 가장 최근의 analyzed_at을 가진 레코드만 사용
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

-- 3. tb_instagram_crawling 테이블의 AI 분석 상태 업데이트 (중복 제거하여 매칭)
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

-- 4. 기존 ai_analysis_status 테이블의 is_analyzed를 true로 업데이트 (중복 제거하여 매칭)
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

-- 5. 결과 확인 쿼리
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

-- 6. 여전히 매칭되지 않는 데이터 확인
select 
  'Still unmatched in ai_influencer_analyses' as issue_type,
  count(*) as count
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.tb_instagram_crawling tic 
    where trim(tic.id) = trim(aia.influencer_id)
  );
