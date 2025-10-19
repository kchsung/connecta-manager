# AI 분석 추천도 Enum 오류 해결 방법

## 문제 상황
인공지능 분석 결과 조회 시 다음과 같은 오류가 발생합니다:
```
분석 데이터 개수 조회 중 오류: {'message': 'invalid input value for enum recommendation_ko: "매우 추천"', 'code': '22P02', 'hint': None, 'details': None}
```

## 원인
- `ai_influencer_analyses` 테이블의 `recommendation` 컬럼이 `recommendation_ko` enum 타입으로 정의되어 있음
- 하지만 해당 enum 타입이 데이터베이스에 생성되지 않았음
- AI 분석 결과에서 사용하는 추천도 값들이 enum에 정의되지 않음

## 해결 방법

### 1. 안전한 문제 진단 (권장)
먼저 문제를 정확히 파악하기 위해 안전한 진단 스크립트를 실행하세요:

```sql
-- diagnose_enum_issue_safe.sql 파일의 내용을 복사하여 실행
```

### 2. 최종 수정 스크립트 실행
진단 결과에 따라 최종 수정 스크립트를 실행하세요:

```sql
-- fix_recommendation_enum_final.sql 파일의 내용을 복사하여 실행
```

### 3. 기본 수정 스크립트 (대안)
위 방법이 실패하는 경우 기본 스크립트를 시도하세요:

```sql
-- fix_recommendation_enum.sql 파일의 내용을 복사하여 실행
```

### 4. 수동 실행 (고급 사용자)
다음 명령어들을 순서대로 실행하세요:

```sql
-- 1. 기존 enum 타입 삭제 (주의: 데이터 백업 필요)
DROP TYPE IF EXISTS recommendation_ko CASCADE;

-- 2. recommendation_ko enum 타입 새로 생성
CREATE TYPE recommendation_ko AS ENUM ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부');

-- 3. 기존 데이터 정리
UPDATE ai_influencer_analyses 
SET recommendation = CASE 
    WHEN recommendation IN ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부') 
    THEN recommendation
    ELSE '보통'  -- 기본값
END;

-- 4. 컬럼 타입 변경
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE text;
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE recommendation_ko USING recommendation::recommendation_ko;
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation SET NOT NULL;

-- 5. 인덱스 재생성
DROP INDEX IF EXISTS idx_ai_influencer_analyses_recommendation;
CREATE INDEX idx_ai_influencer_analyses_recommendation ON ai_influencer_analyses (recommendation);
```

### 3. 확인
스크립트 실행 후 다음 명령어로 확인하세요:

```sql
-- enum 타입 확인
SELECT typname, enumlabel FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE typname = 'recommendation_ko';

-- 테이블 구조 확인
\d ai_influencer_analyses
```

## 지원되는 추천도 값
- `추천`
- `조건부`
- `비추천`

## 주의사항
- 스크립트 실행 전 데이터베이스 백업을 권장합니다
- 기존 데이터에 유효하지 않은 추천도 값이 있다면 오류가 발생할 수 있습니다
- 프로덕션 환경에서는 신중하게 실행하세요

## 문제가 지속되는 경우
1. 데이터베이스 로그 확인
2. 기존 데이터의 recommendation 값들 검토
3. 필요시 데이터 정리 후 재실행
