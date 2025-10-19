-- ============================================================================
-- AI 분석 테이블 구조 확인 스크립트
-- ============================================================================

-- 1. 테이블 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_influencer_analyses') 
        THEN '✅ ai_influencer_analyses 테이블이 존재합니다.'
        ELSE '❌ ai_influencer_analyses 테이블이 존재하지 않습니다.'
    END as table_status;

-- 2. 테이블의 모든 컬럼 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'ai_influencer_analyses' 
ORDER BY ordinal_position;

-- 3. recommendation 컬럼 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'ai_influencer_analyses' 
            AND column_name = 'recommendation'
        ) 
        THEN '✅ recommendation 컬럼이 존재합니다.'
        ELSE '❌ recommendation 컬럼이 존재하지 않습니다.'
    END as recommendation_column_status;

-- 4. enum 타입 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_ko') 
        THEN '✅ recommendation_ko enum이 존재합니다.'
        ELSE '❌ recommendation_ko enum이 존재하지 않습니다.'
    END as enum_status;

-- 5. 테이블의 제약조건 확인
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'ai_influencer_analyses'::regclass;

-- 6. 테이블의 인덱스 확인
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'ai_influencer_analyses';
