# 인공지능 분석 로직 개선

## 개요
인공지능 분석 시스템의 효율성을 높이기 위해 분석 상태를 추적하고 관리하는 새로운 테이블과 로직을 추가했습니다.

## 주요 변경사항

### 1. 새로운 테이블 생성
- **`ai_analysis_status`**: 각 크롤링 데이터의 AI 분석 상태를 추적하는 테이블
  - `id`: tb_instagram_crawling 테이블의 id와 동일
  - `is_analyzed`: AI 분석 완료 여부 (boolean)
  - `analyzed_at`: AI 분석 완료 시간
  - `created_at`, `updated_at`: 레코드 생성/수정 시간

### 2. 기존 테이블 컬럼 추가
- **`tb_instagram_crawling`** 테이블에 다음 컬럼 추가:
  - `ai_analysis_status`: AI 분석 완료 여부 (boolean, 기본값: false)
  - `ai_analyzed_at`: AI 분석 완료 시간

### 3. 자동화 트리거
- **tb_instagram_crawling INSERT**: 새 크롤링 데이터 추가 시 ai_analysis_status 테이블에 자동으로 레코드 생성
- **ai_influencer_analyses INSERT**: AI 분석 완료 시 관련 테이블들의 분석 상태를 true로 자동 업데이트
- **tb_instagram_crawling UPDATE**: AI 분석 상태 변경 시 ai_analysis_status 테이블과 동기화

### 4. 분석 실행 로직 개선
- **분석 대상 필터링**: `status='COMPLETE'` AND `ai_analysis_status=false`인 데이터만 분석 대상으로 선정
- **중복 분석 방지**: 이미 분석된 데이터는 자동으로 제외
- **상태 추적**: 분석 완료 시 모든 관련 테이블의 상태가 자동으로 업데이트

## 파일 구조

```
supabase/db/
├── ai_analysis_status.sql                    # AI 분석 상태 테이블 생성
├── add_ai_analysis_columns.sql              # tb_instagram_crawling 컬럼 추가
├── ai_analysis_triggers.sql                 # 트리거 함수 및 트리거 생성
├── update_existing_analysis_status.sql      # 기존 데이터 업데이트
├── apply_ai_analysis_improvements.sql       # 통합 실행 스크립트
└── README_ai_analysis_improvements.md       # 이 문서
```

## 실행 방법

### 방법 1: 통합 스크립트 실행 (권장)
```sql
-- supabase/db/apply_ai_analysis_improvements.sql 파일을 Supabase SQL Editor에서 실행
```

### 방법 2: 개별 파일 순차 실행
1. `ai_analysis_status.sql` - AI 분석 상태 테이블 생성
2. `add_ai_analysis_columns.sql` - 기존 테이블에 컬럼 추가
3. `ai_analysis_triggers.sql` - 트리거 함수 및 트리거 생성
4. `update_existing_analysis_status.sql` - 기존 데이터 업데이트

## 코드 변경사항

### src/ui/ai_analysis_common.py
- `get_completed_crawling_data()`: AI 분석이 필요한 데이터만 조회하도록 수정
- `get_completed_crawling_data_count()`: AI 분석 대상 개수만 카운트하도록 수정
- `is_recently_analyzed_by_id()`: ai_analysis_status 테이블을 사용하도록 수정
- `save_ai_analysis_result()`: AI 분석 완료 시 상태 업데이트 로직 추가

## 데이터 흐름

1. **크롤링 데이터 추가**
   ```
   tb_instagram_crawling INSERT → ai_analysis_status 자동 생성 (is_analyzed=false)
   ```

2. **AI 분석 실행**
   ```
   status='COMPLETE' AND ai_analysis_status=false인 데이터만 분석 대상
   ```

3. **AI 분석 완료**
   ```
   ai_influencer_analyses INSERT → 
   ai_analysis_status.is_analyzed=true 업데이트 →
   tb_instagram_crawling.ai_analysis_status=true 업데이트
   ```

## 확인 쿼리

### 분석 상태 현황 확인
```sql
-- 전체 분석 상태 현황
SELECT 
  'ai_analysis_status' as table_name,
  count(*) as total_records,
  count(*) filter (where is_analyzed = true) as analyzed_records,
  count(*) filter (where is_analyzed = false) as not_analyzed_records
FROM public.ai_analysis_status
UNION ALL
SELECT 
  'tb_instagram_crawling' as table_name,
  count(*) as total_records,
  count(*) filter (where ai_analysis_status = true) as analyzed_records,
  count(*) filter (where ai_analysis_status = false) as not_analyzed_records
FROM public.tb_instagram_crawling;
```

### AI 분석 대기 중인 데이터 확인
```sql
-- AI 분석이 필요한 데이터 개수
SELECT count(*) as pending_analysis_count
FROM public.tb_instagram_crawling 
WHERE status = 'COMPLETE' 
  AND ai_analysis_status = false;
```

## 장점

1. **효율성 향상**: 이미 분석된 데이터를 제외하고 분석 대상만 선별
2. **중복 방지**: 동일한 데이터의 중복 분석 방지
3. **상태 추적**: 각 데이터의 분석 상태를 명확히 추적 가능
4. **자동화**: 트리거를 통한 자동 상태 관리
5. **확장성**: 향후 분석 로직 확장 시 유연한 대응 가능

## 주의사항

1. **기존 데이터**: 기존 ai_influencer_analyses에 있는 데이터는 자동으로 분석 완료 상태로 설정됩니다.
2. **트리거 의존성**: 트리거가 정상 작동하지 않을 경우 수동으로 상태를 동기화해야 할 수 있습니다.
3. **성능**: 대용량 데이터의 경우 인덱스가 자동으로 생성되어 성능에 도움이 됩니다.

## 문제 해결

### 트리거가 작동하지 않는 경우
```sql
-- 트리거 재생성
DROP TRIGGER IF EXISTS trg_insert_ai_analysis_status ON public.tb_instagram_crawling;
CREATE TRIGGER trg_insert_ai_analysis_status
  AFTER INSERT ON public.tb_instagram_crawling
  FOR EACH ROW
  EXECUTE FUNCTION insert_ai_analysis_status();
```

### 상태 동기화 문제
```sql
-- 수동 동기화
UPDATE public.ai_analysis_status 
SET is_analyzed = true, analyzed_at = aia.analyzed_at
FROM public.ai_influencer_analyses aia
WHERE ai_analysis_status.id = aia.influencer_id;
```
