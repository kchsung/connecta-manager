-- ============================================================================
-- AI 분석 추천도 enum 오류 최종 해결 스크립트
-- ============================================================================

-- 1. 현재 상황 확인
SELECT '현재 상황 진단 시작...' as status;

-- 2. 기존 enum 타입 완전 삭제 (CASCADE로 관련 객체도 함께 삭제)
DROP TYPE IF EXISTS recommendation_ko CASCADE;

-- 3. recommendation_ko enum 타입 새로 생성
CREATE TYPE recommendation_ko AS ENUM ('추천', '조건부', '비추천');

-- 4. recommendation 컬럼을 text로 변경 (NOT NULL 제약조건 제거)
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation DROP NOT NULL;
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE text;

-- 5. 데이터 정리 및 정규화
UPDATE ai_influencer_analyses 
SET recommendation = CASE 
    -- 정확한 매칭
    WHEN recommendation IN ('추천', '조건부', '비추천') 
    THEN recommendation
    
    -- 유사한 값들 정규화
    WHEN recommendation ILIKE '%매우%추천%' OR recommendation = '매우추천' OR recommendation = '매우 추천'
    THEN '추천'
    WHEN recommendation ILIKE '%추천%' AND recommendation NOT ILIKE '%비추천%' AND recommendation NOT ILIKE '%매우%'
    THEN '추천'
    WHEN recommendation ILIKE '%보통%'
    THEN '조건부'
    WHEN recommendation ILIKE '%매우%비추천%' OR recommendation = '매우비추천' OR recommendation = '매우 비추천'
    THEN '비추천'
    WHEN recommendation ILIKE '%비추천%'
    THEN '비추천'
    WHEN recommendation ILIKE '%조건부%'
    THEN '조건부'
    
    -- 기본값
    ELSE '조건부'
END;

-- 6. NULL 값 처리
UPDATE ai_influencer_analyses 
SET recommendation = '조건부'
WHERE recommendation IS NULL OR recommendation = '';

-- 7. recommendation 컬럼을 recommendation_ko enum으로 변경
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE recommendation_ko USING recommendation::recommendation_ko;

-- 8. NOT NULL 제약조건 재설정
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation SET NOT NULL;

-- 9. 인덱스 재생성
DROP INDEX IF EXISTS idx_ai_influencer_analyses_recommendation;
CREATE INDEX idx_ai_influencer_analyses_recommendation ON ai_influencer_analyses (recommendation);

-- 10. 최종 검증
SELECT 
    '✅ 수정 완료' as status,
    (SELECT COUNT(*) FROM ai_influencer_analyses WHERE recommendation IS NOT NULL) as valid_records,
    (SELECT COUNT(DISTINCT recommendation) FROM ai_influencer_analyses) as unique_recommendations;

-- 11. 최종 데이터 확인
SELECT 
    recommendation,
    COUNT(*) as count
FROM ai_influencer_analyses 
GROUP BY recommendation
ORDER BY count DESC;

-- 12. enum 타입 확인
SELECT 
    typname as enum_name,
    enumlabel as enum_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE typname = 'recommendation_ko'
ORDER BY e.enumsortorder;
