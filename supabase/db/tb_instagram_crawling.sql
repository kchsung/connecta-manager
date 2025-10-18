-- 크롤링 raw 정보 테이블
-- 인스타그램 크롤링 데이터를 저장하는 테이블

create table public.tb_instagram_crawling (
  id character varying(200) not null,
  status character varying(20) not null default 'WAIT'::character varying,
  description text null,
  image_url character varying(1000) null,
  posts text null,
  created_at timestamp without time zone null default now(),
  updated_at timestamp without time zone null,
  constraint tb_instagram_crawling_pkey primary key (id)
) TABLESPACE pg_default;

-- 테이블 코멘트
comment on table public.tb_instagram_crawling is '인스타그램 크롤링 raw 데이터 저장 테이블';
comment on column public.tb_instagram_crawling.id is '크롤링 대상 고유 ID';
comment on column public.tb_instagram_crawling.status is '크롤링 상태 (WAIT, PROCESSING, COMPLETE, FAILED)';
comment on column public.tb_instagram_crawling.description is '크롤링 대상 설명';
comment on column public.tb_instagram_crawling.image_url is '프로필 이미지 URL';
comment on column public.tb_instagram_crawling.posts is '크롤링된 게시물 데이터 (JSON 형태)';
comment on column public.tb_instagram_crawling.created_at is '생성일시';
comment on column public.tb_instagram_crawling.updated_at is '수정일시';

-- 인덱스 생성
create index if not exists idx_tb_instagram_crawling_status on public.tb_instagram_crawling using btree (status);
create index if not exists idx_tb_instagram_crawling_created_at on public.tb_instagram_crawling using btree (created_at);
