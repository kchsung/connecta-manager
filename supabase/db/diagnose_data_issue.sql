-- 데이터 불일치 문제 진단 스크립트

-- 1. ai_influencer_analyses에 있는 influencer_id 중 tb_instagram_crawling에 없는 것들 확인
select 
  'Missing in tb_instagram_crawling' as issue_type,
  aia.influencer_id,
  length(aia.influencer_id) as id_length,
  ascii(substring(aia.influencer_id from length(aia.influencer_id))) as last_char_ascii,
  aia.analyzed_at
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and not exists (
    select 1 from public.tb_instagram_crawling tic 
    where tic.id = aia.influencer_id
  )
order by aia.influencer_id
limit 20;

-- 2. tb_instagram_crawling에 있는 id 중 ai_influencer_analyses에 없는 것들 확인
select 
  'Missing in ai_influencer_analyses' as issue_type,
  tic.id,
  length(tic.id) as id_length,
  ascii(substring(tic.id from length(tic.id))) as last_char_ascii,
  tic.status
from public.tb_instagram_crawling tic
where tic.id is not null
  and not exists (
    select 1 from public.ai_influencer_analyses aia 
    where aia.influencer_id = tic.id
  )
order by tic.id
limit 20;

-- 3. 공백이나 특수문자 문제가 있는지 확인
select 
  'Potential whitespace issues' as issue_type,
  aia.influencer_id,
  '[' || aia.influencer_id || ']' as id_with_brackets,
  length(aia.influencer_id) as id_length,
  trim(aia.influencer_id) as trimmed_id,
  length(trim(aia.influencer_id)) as trimmed_length
from public.ai_influencer_analyses aia
where aia.influencer_id is not null
  and length(aia.influencer_id) != length(trim(aia.influencer_id))
limit 10;

-- 4. 정확히 매칭되는 데이터 개수 확인
select 
  'Matching records' as issue_type,
  count(*) as count
from public.ai_influencer_analyses aia
inner join public.tb_instagram_crawling tic on tic.id = aia.influencer_id
where aia.influencer_id is not null;

-- 5. 전체 데이터 개수 확인
select 
  'ai_influencer_analyses total' as table_name,
  count(*) as total_count,
  count(distinct influencer_id) as unique_influencer_ids
from public.ai_influencer_analyses
where influencer_id is not null
union all
select 
  'tb_instagram_crawling total' as table_name,
  count(*) as total_count,
  count(distinct id) as unique_ids
from public.tb_instagram_crawling;
