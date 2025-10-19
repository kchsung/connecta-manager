-- ============================================================================
-- AI 분석 추천도 enum 오류 수정
-- ============================================================================

-- 1. recommendation_ko enum 타입 생성 (이미 존재하지 않는 경우에만)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_ko') THEN
        CREATE TYPE recommendation_ko AS ENUM ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부');
    END IF;
END $$;

-- 2. 기존 데이터의 recommendation 컬럼을 text로 임시 변경
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE text;

-- 3. recommendation 컬럼을 recommendation_ko enum으로 변경
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation TYPE recommendation_ko USING recommendation::recommendation_ko;

-- 4. NOT NULL 제약조건 재설정
ALTER TABLE ai_influencer_analyses ALTER COLUMN recommendation SET NOT NULL;

-- 5. 인덱스 재생성 (필요한 경우)
DROP INDEX IF EXISTS idx_ai_influencer_analyses_recommendation;
CREATE INDEX idx_ai_influencer_analyses_recommendation ON ai_influencer_analyses (recommendation);

-- 6. 완료 메시지
SELECT 'recommendation_ko enum이 성공적으로 적용되었습니다.' as status;
