-- ============================================================================
-- AI 분석 추천도 enum 문제 진단 스크립트 (안전한 버전)
-- ============================================================================

-- 1. enum 타입 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_ko') 
        THEN '✅ recommendation_ko enum이 존재합니다.'
        ELSE '❌ recommendation_ko enum이 존재하지 않습니다.'
    END as enum_status;

-- 2. enum 값들 확인
SELECT 
    typname as enum_name,
    enumlabel as enum_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE typname = 'recommendation_ko'
ORDER BY e.enumsortorder;

-- 3. 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'ai_influencer_analyses' 
AND column_name = 'recommendation';

-- 4. 테이블 제약조건 확인
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'ai_influencer_analyses'::regclass
AND conname LIKE '%recommendation%';

-- 5. 안전한 데이터 확인 (text로 캐스팅하여 enum 오류 방지)
SELECT 
    recommendation::text as recommendation_text,
    COUNT(*) as count
FROM ai_influencer_analyses 
GROUP BY recommendation::text
ORDER BY count DESC;

-- 6. 유효하지 않은 recommendation 값 확인 (안전한 방법)
WITH valid_values AS (
    SELECT unnest(ARRAY['추천', '조건부', '비추천']) as valid_value
)
SELECT 
    recommendation::text as invalid_recommendation,
    COUNT(*) as count
FROM ai_influencer_analyses 
WHERE recommendation::text NOT IN (SELECT valid_value FROM valid_values)
GROUP BY recommendation::text;

-- 7. 전체 레코드 수 확인
SELECT COUNT(*) as total_records FROM ai_influencer_analyses;

-- 8. NULL 값 확인
SELECT COUNT(*) as null_recommendations 
FROM ai_influencer_analyses 
WHERE recommendation IS NULL;
