-- 기존 ai_influencer_analyses 데이터에 대해 분석 상태를 true로 업데이트하는 스크립트 (수정된 버전)
-- 외래키 제약조건 오류 해결: tb_instagram_crawling에 존재하는 influencer_id만 처리

-- 1. 먼저 문제가 되는 데이터 확인
-- ai_influencer_analyses에 있지만 tb_instagram_crawling에 없는 influencer_id 확인
select 
  'Missing in tb_instagram_crawling' as issue_type,
  count(*) as count,
  string_agg(distinct aia.influencer_id, ', ') as sample_ids
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.tb_instagram_crawling tic 
    where tic.id = aia.influencer_id
  );

-- 2. tb_instagram_crawling에 존재하는 influencer_id만을 대상으로 ai_analysis_status 테이블에 레코드 추가
insert into public.ai_analysis_status (id, is_analyzed, analyzed_at, created_at, updated_at)
select 
  aia.influencer_id,
  true as is_analyzed,
  aia.analyzed_at,
  aia.created_at,
  now() as updated_at
from public.ai_influencer_analyses aia
inner join public.tb_instagram_crawling tic on tic.id = aia.influencer_id
where aia.influencer_id is not null
  and not exists (
    select 1 from public.ai_analysis_status aas 
    where aas.id = aia.influencer_id
  )
on conflict (id) do update set
  is_analyzed = true,
  analyzed_at = excluded.analyzed_at,
  updated_at = now();

-- 3. tb_instagram_crawling 테이블의 AI 분석 상태 업데이트 (존재하는 데이터만)
update public.tb_instagram_crawling 
set 
  ai_analysis_status = true,
  ai_analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
where tb_instagram_crawling.id = aia.influencer_id
  and aia.influencer_id is not null;

-- 4. 기존 ai_analysis_status 테이블의 is_analyzed를 true로 업데이트 (존재하는 데이터만)
update public.ai_analysis_status 
set 
  is_analyzed = true,
  analyzed_at = aia.analyzed_at,
  updated_at = now()
from public.ai_influencer_analyses aia
inner join public.tb_instagram_crawling tic on tic.id = aia.influencer_id
where ai_analysis_status.id = aia.influencer_id
  and aia.influencer_id is not null;

-- 5. 누락된 데이터에 대한 ai_analysis_status 레코드 생성 (외래키 제약조건 없이)
-- 이 부분은 선택사항이며, 누락된 데이터를 별도로 관리하고 싶은 경우에만 실행
-- 주석 처리: 외래키 제약조건 때문에 실행할 수 없음
/*
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
    select 1 from public.tb_instagram_crawling tic 
    where tic.id = aia.influencer_id
  )
  and not exists (
    select 1 from public.ai_analysis_status aas 
    where aas.id = aia.influencer_id
  );
*/

-- 6. 결과 확인 쿼리
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

-- 7. 누락된 데이터 현황 확인
select 
  'ai_influencer_analyses without tb_instagram_crawling' as issue_type,
  count(*) as count
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.tb_instagram_crawling tic 
    where tic.id = aia.influencer_id
  );
