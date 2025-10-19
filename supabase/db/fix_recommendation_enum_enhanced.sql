-- ============================================================================
-- AI 분석 추천도 enum 오류 수정 (강화된 버전)
-- ============================================================================

-- 1. 기존 enum 타입이 있다면 삭제 (주의: 기존 데이터가 있다면 백업 필요)
DROP TYPE IF EXISTS recommendation_ko CASCADE;

-- 2. recommendation_ko enum 타입 새로 생성
CREATE TYPE recommendation_ko AS ENUM ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부');

-- 3. 기존 데이터의 recommendation 값들을 정리
UPDATE ai_influencer_analyses 
SET recommendation = CASE 
    WHEN recommendation IN ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부') 
    THEN recommendation
    WHEN recommendation = '조건부 추천' OR recommendation = '조건부추천'
    THEN '조건부'
    WHEN recommendation = '매우추천' OR recommendation = '매우 추천'
    THEN '매우 추천'
    WHEN recommendation = '추천'
    THEN '추천'
    WHEN recommendation = '보통'
    THEN '보통'
    WHEN recommendation = '비추천'
    THEN '비추천'
    WHEN recommendation = '매우비추천' OR recommendation = '매우 비추천'
    THEN '매우 비추천'
    ELSE '보통'  -- 기본값
END;

-- 4. recommendation 컬럼을 text로 변경 (NOT NULL 제약조건 제거)
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation DROP NOT NULL;
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE text;

-- 5. recommendation 컬럼을 recommendation_ko enum으로 변경
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE recommendation_ko USING recommendation::recommendation_ko;

-- 6. NOT NULL 제약조건 재설정
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation SET NOT NULL;

-- 7. 인덱스 재생성
DROP INDEX IF EXISTS idx_ai_influencer_analyses_recommendation;
CREATE INDEX idx_ai_influencer_analyses_recommendation ON ai_influencer_analyses (recommendation);

-- 8. 검증 쿼리
SELECT 
    '✅ enum 타입 생성 완료' as step1,
    (SELECT COUNT(*) FROM ai_influencer_analyses WHERE recommendation IS NOT NULL) as valid_records,
    (SELECT COUNT(DISTINCT recommendation) FROM ai_influencer_analyses) as unique_recommendations;

-- 9. 최종 확인
SELECT 
    recommendation,
    COUNT(*) as count
FROM ai_influencer_analyses 
GROUP BY recommendation
ORDER BY count DESC;
