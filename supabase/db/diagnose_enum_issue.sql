-- ============================================================================
-- AI 분석 추천도 enum 문제 진단 스크립트
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

-- 4. 기존 데이터의 recommendation 값들 확인
SELECT 
    recommendation,
    COUNT(*) as count
FROM ai_influencer_analyses 
GROUP BY recommendation
ORDER BY count DESC;

-- 5. 유효하지 않은 recommendation 값 확인
SELECT 
    recommendation,
    COUNT(*) as count
FROM ai_influencer_analyses 
WHERE recommendation NOT IN ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부')
GROUP BY recommendation;

-- 6. 테이블 제약조건 확인
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'ai_influencer_analyses'::regclass
AND conname LIKE '%recommendation%';
